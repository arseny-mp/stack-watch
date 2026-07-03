#!/usr/bin/env python3
import os
import re
import sys
import json
import logging
import urllib.request
import time
from datetime import datetime

# Import NotebookLMClient
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from notebooklm_client import NotebookLMClient
from models import CurationResult, CurationDetailsResult

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
LOG_FILE = os.path.join(WORKSPACE_DIR, "curate-findings.log")

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] Curation: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_api_key(name):
    # Try env first
    val = os.environ.get(name)
    if val:
        return val
    # Try Keychain only on macOS
    import sys
    if sys.platform == 'darwin':
        try:
            import subprocess
            result = subprocess.run(
                ['security', 'find-generic-password', '-a', 'user', '-s', name, '-w'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return result.stdout.decode('utf-8').strip()
        except Exception:
            pass
    return None

def call_gemini(key, prompt, response_schema):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }
    }
    
    import time
    import urllib.error
    for attempt in range(1, 6):
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=180) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                text = res["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except Exception as e:
            is_retryable = False
            error_msg = str(e)
            
            if isinstance(e, urllib.error.HTTPError):
                if e.code in [429, 500, 503]:
                    is_retryable = True
                    error_msg = f"HTTP {e.code}"
            elif isinstance(e, (urllib.error.URLError, TimeoutError)):
                is_retryable = True
                error_msg = f"Network/Timeout ({e})"
            elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                is_retryable = True
                error_msg = f"Timeout error ({e})"
                
            if is_retryable and attempt < 5:
                sleep_time = attempt * 30
                logging.warning(f"Gemini Curation error: {error_msg}. Retrying in {sleep_time}s (attempt {attempt}/5)...")
                time.sleep(sleep_time)
            else:
                raise e


def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    daily_dir = os.path.join(WORKSPACE_DIR, date_str)
    feed_file = os.path.join(daily_dir, "feed_updates.json")
    
    if not os.path.exists(feed_file):
        logging.error(f"No daily feed_updates.json found at {feed_file}")
        sys.exit(1)
        
    with open(feed_file, 'r', encoding='utf-8') as f:
        updates = json.load(f)
        
    # Fetch NotebookLM summaries for kept YouTube videos
    youtube_client = None
    for item in updates:
        if item.get("screened_verdict") == "keep" and (item.get("component") == "YouTube Discovery" or "youtube.com" in item.get("url", "") or "youtu.be" in item.get("url", "")):
            url = item.get("url")
            logging.info(f"Detected YouTube video to summarize: {url}")
            if not youtube_client:
                youtube_client = NotebookLMClient()
                try:
                    youtube_client.connect()
                except Exception as e:
                    logging.error(f"Failed to connect to NotebookLM MCP server: {e}")
                    youtube_client = None
            
            if youtube_client:
                try:
                    notebook_id = youtube_client.find_or_create_notebook("Stack Watch Research")
                    youtube_client.add_url(notebook_id, url)
                    logging.info("Waiting 20 seconds for NotebookLM ingestion...")
                    time.sleep(20)
                    summary = youtube_client.query_notebook(
                        notebook_id,
                        "Сделай подробный структурированный конспект этого видео на русском языке. Выдели ключевые мысли, таймкоды, если они есть, инструменты и выводы."
                    )
                    item["notebooklm_summary"] = summary
                    logging.info("NotebookLM summary generated successfully.")
                except Exception as e:
                    logging.error(f"Error getting YouTube summary from NotebookLM: {e}")
                    
    if youtube_client:
        try:
            youtube_client.disconnect()
        except Exception:
            pass

    if not updates:
        logging.info("No updates to curate. Writing EMPTY marker.")
        with open(os.path.join(daily_dir, "EMPTY"), 'w') as f:
            f.write("")
        sys.exit(0)
        
    # Read rubric
    rubric_file = os.path.join(WORKSPACE_DIR, "_rubric.md")
    rubric_content = ""
    if os.path.exists(rubric_file):
        with open(rubric_file, 'r', encoding='utf-8') as f:
            rubric_content = f.read()
            
    # Read learnings
    learnings_file = os.path.join(WORKSPACE_DIR, "learnings.md")
    learnings_content = ""
    if os.path.exists(learnings_file):
        with open(learnings_file, 'r', encoding='utf-8') as f:
            learnings_content = f.read()

    # Filter candidates based on screened_verdict
    kept_candidates = []
    skipped_candidates = []
    for idx, item in enumerate(updates):
        item["original_index"] = idx
        if item.get("screened_verdict") == "keep":
            kept_candidates.append(item)
        else:
            skipped_candidates.append(item)
            
    logging.info(f"Loaded {len(updates)} updates. Kept: {len(kept_candidates)}, Skipped: {len(skipped_candidates)}.")

    do_now_items = []
    experiment_items = []
    parking_items = []
    skipped_kept_items = []
    actionable_findings = []
    breaking_marker_detected = False

    if kept_candidates:
        # Call Gemini API
        api_key = get_api_key("GEMINI_API_KEY") or get_api_key("GOOGLE_API_KEY")
        if not api_key:
            logging.error("No GEMINI_API_KEY or GOOGLE_API_KEY found.")
            sys.exit(1)

        # Prepare candidates payload for Gemini
        gemini_candidates = []
        for item in kept_candidates:
            cand = {
                "id": item["original_index"],
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "date": item.get("date", ""),
                "component": item.get("component", ""),
                "version": item.get("version", ""),
                "type": item.get("type", "")
            }
            if "notebooklm_summary" in item:
                cand["notebooklm_summary"] = item["notebooklm_summary"]
            gemini_candidates.append(cand)

        # --- Step 1: Classification & Summarization ---
        step1_prompt = f"""You are the autonomous Curation Agent for the Stack Watch news system.
Your job is to evaluate today's daily updates, apply the rubric, consult active learnings exceptions, and classify each of them.

Today's Date: {date_str}

=== Rubric Guidelines ===
{rubric_content}

=== Active Learnings & Corrections ===
{learnings_content}

=== Raw Candidate Feeds (Only kept ones) ===
{json.dumps(gemini_candidates, indent=2)}

Tasks:
For each candidate:
1. Determine the final verdict: "do now", "experiment", "parking lot", or "skip".
2. Extract the touch components (e.g. "Claude Code CLI").
3. Determine confidence: "high", "medium", or "low".
4. Determine severity: "breaking/security", "critical", "minor", "performance", "integration".
5. Provide a short explanation (why_this_verdict) in Russian (1-2 sentences).
6. Provide tags (list of keywords).
7. If verdict is "do now" or "experiment", formulate a concise action plan in Russian with estimation, e.g. "Обновить ... (~1 час)". If "parking lot", formulate action plan as "Мониторить ..." or similar.
8. Suggest a clean title in English and a slug (lowercase-dashed-title-slug).

Respond with a JSON object matching the requested schema. Ensure all Russian translations are precise and follow standard professional language.
"""

        step1_schema = {
            "type": "OBJECT",
            "properties": {
                "classifications": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "id": {"type": "INTEGER", "description": "The ID of the candidate from the input feed list"},
                            "slug": {"type": "STRING", "description": "The finding slug (e.g., lowercase-title-slug)"},
                            "title": {"type": "STRING", "description": "Concise title in English"},
                            "verdict": {"type": "STRING", "description": "do now | experiment | parking lot | skip"},
                            "why_this_verdict": {"type": "STRING", "description": "Why this verdict in Russian (1-2 sentences)"},
                            "touches": {"type": "STRING", "description": "Component/tool touched"},
                            "severity": {"type": "STRING", "description": "breaking/security | critical | minor | performance | integration"},
                            "confidence": {"type": "STRING", "description": "high | medium | low"},
                            "tags": {
                                "type": "ARRAY",
                                "items": {"type": "STRING"}
                            },
                            "action_plan": {"type": "STRING", "description": "Action plan or monitoring description in Russian"}
                        },
                        "required": ["id", "slug", "title", "verdict", "why_this_verdict", "touches", "severity", "confidence", "tags", "action_plan"]
                    }
                },
                "breaking_marker_detected": {
                    "type": "BOOLEAN",
                    "description": "True if there is any critical/breaking severity finding that warrants a breaking-marker file"
                }
            },
            "required": ["classifications", "breaking_marker_detected"]
        }

        logging.info("Querying Gemini for daily curation (Step 1: Classification & Summary)...")
        try:
            step1_result = call_gemini(api_key, step1_prompt, step1_schema)
        except Exception as e:
            logging.error(f"Gemini Curation Step 1 failed: {e}")
            sys.exit(1)

        try:
            validated_result = CurationResult.model_validate(step1_result)
            breaking_marker_detected = validated_result.breaking_marker_detected
            classification_map = {c.id: c.model_dump() for c in validated_result.classifications}
        except Exception as ve:
            logging.error(f"Pydantic validation failed for CurationResult: {ve}")
            sys.exit(1)

        for item in kept_candidates:
            orig_id = item["original_index"]
            c = classification_map.get(orig_id)
            if not c:
                logging.warning(f"No classification returned for candidate ID {orig_id}: {item.get('title')}")
                continue

            item["slug"] = c["slug"]
            item["title_english"] = c["title"]
            item["final_verdict"] = c["verdict"]
            item["why_this_verdict"] = c["why_this_verdict"]
            item["touches"] = c["touches"]
            item["severity"] = c["severity"]
            item["confidence"] = c["confidence"]
            item["tags"] = c["tags"]
            item["action_plan"] = c["action_plan"]

            verdict = c["verdict"].strip().lower()
            if verdict == "parking":
                verdict = "parking lot"

            if verdict == "do now":
                do_now_items.append(item)
                actionable_findings.append({
                    "slug": c["slug"],
                    "title": item.get("title", ""),
                    "verdict": "do now",
                    "confidence": c["confidence"],
                    "sources": item.get("component", ""),
                    "touches": c["touches"],
                    "url": item.get("url", ""),
                    "severity": c["severity"],
                    "candidate_data": json.dumps(item)
                })
            elif verdict == "experiment":
                experiment_items.append(item)
                actionable_findings.append({
                    "slug": c["slug"],
                    "title": item.get("title", ""),
                    "verdict": "experiment",
                    "confidence": c["confidence"],
                    "sources": item.get("component", ""),
                    "touches": c["touches"],
                    "url": item.get("url", ""),
                    "severity": c["severity"],
                    "candidate_data": json.dumps(item)
                })
            elif verdict == "parking lot":
                parking_items.append(item)
                actionable_findings.append({
                    "slug": c["slug"],
                    "title": item.get("title", ""),
                    "verdict": "parking",
                    "confidence": c["confidence"],
                    "sources": item.get("component", ""),
                    "touches": c["touches"],
                    "url": item.get("url", ""),
                    "severity": c["severity"],
                    "candidate_data": json.dumps(item)
                })
            elif verdict == "skip":
                skipped_kept_items.append(item)
    else:
        logging.info("No kept candidates to classify via Gemini.")

    # --- Step 2: Detail Generation for Actionable Findings in Batches ---
    logging.info(f"Found {len(actionable_findings)} actionable findings to curate.")
    findings = []
    memory_entries = []

    if actionable_findings:
        step2_schema = {
            "type": "OBJECT",
            "properties": {
                "findings": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "slug": {"type": "STRING"},
                            "finding_content": {"type": "STRING", "description": "The complete markdown content for the slug.md file following the template"},
                            "memory_entry_content": {"type": "STRING", "description": "The complete markdown content for the memory entry (if verdict is parking or experiment, otherwise empty string)"}
                        },
                        "required": ["slug", "finding_content", "memory_entry_content"]
                    }
                }
            },
            "required": ["findings"]
        }

        batch_size = 4
        total_findings = len(actionable_findings)

        for i in range(0, total_findings, batch_size):
            batch = actionable_findings[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_findings - 1) // batch_size + 1

            logging.info(f"Generating details for batch {batch_num}/{total_batches} ({len(batch)} findings)...")

            step2_prompt = f"""You are the Curation Agent for Stack Watch.
Generate the detailed findings content and memory entries (if needed) for the following tech stack updates:

Today's Date: {date_str}

=== Findings to Curate ===
{json.dumps(batch, indent=2)}

Tasks:
For each finding in the list:
1. Generate the detailed markdown content (finding_content).
   The content MUST follow this template EXACTLY:
   # [Title from finding]
   **Verdict:** [verdict from finding]
   **Confidence:** [confidence from finding]
   **Sources:** [sources from finding]
   **Source count:** 1
   **Touches:** [touches from finding]
   **Original URL:** [url from finding]
   **Verify URL:** ok
   **Date:** {date_str}

   ## Summary
   [Must be written in Russian. Provide an expanded, detailed summary structured into two clear parts:
   1. Что это такое: подробное и развернутое объяснение сути обновления, нового инструмента или фичи.
   2. Зачем мне это нужно: развернутое объяснение практической пользы, ценности для рабочего процесса оператора и применимости в его стеке.]

   ## What changes
   [Detailed description of technical changes and features in Russian]

2. If the verdict is 'parking' or 'experiment', generate the memory entry content (memory_entry_content).
   The memory entry content MUST follow this template EXACTLY:
   ---
   name: [verdict]-[slug]
   description: [Description in Russian, max 120 chars]
   metadata:
     type: project
   ---

   Memory entry for [title] identified {date_str} via Stack Watch.

   **Trigger to revisit:** [Concrete condition under which to revisit this, in Russian]

   **Why parked/experiment:** [2-3 sentences explaining why it was parked or set as experiment, in Russian]

   **Source(s):** [url]

   **Touches:** [touches]

Respond with a JSON object matching the requested schema. Ensure all Russian translations are precise and follow standard professional language.
"""

            try:
                if i > 0:
                    time.sleep(15) # Rate-limit guard delay (15s)

                step2_result = call_gemini(api_key, step2_prompt, step2_schema)
                
                try:
                    validated_details = CurationDetailsResult.model_validate(step2_result)
                    findings_list = [f.model_dump() for f in validated_details.findings]
                except Exception as ve:
                    logging.error(f"Pydantic validation failed for CurationDetailsResult: {ve}")
                    findings_list = step2_result.get("findings", [])

                for item in findings_list:
                    slug = item.get("slug")
                    matching_finding = next((f for f in batch if f.get("slug") == slug), None)
                    verdict = matching_finding.get("verdict") if matching_finding else "parking"

                    findings.append({
                        "filename": f"{slug}.md",
                        "content": item["finding_content"]
                    })

                    if item.get("memory_entry_content") and verdict in ["parking", "experiment"]:
                        prefix = "parked" if verdict == "parking" else "experiment"
                        memory_entries.append({
                            "filename": f"{prefix}_{slug}.md",
                            "content": item["memory_entry_content"]
                        })
            except Exception as e:
                logging.error(f"Failed to generate details for batch {batch_num}: {e}")
                continue

    # Compile files via programmatic rendering in Python
    logging.info("Compiling daily research and curation summaries...")

    # summary.md
    summary_lines = []
    summary_lines.append(f"# Обзор обновлений Stack Watch за {date_str}")
    summary_lines.append("")
    total_sources = len(updates)
    kept_count = len(do_now_items) + len(experiment_items) + len(parking_items)
    skipped_count = len(skipped_candidates) + len(skipped_kept_items)
    summary_lines.append(f"Сегодня было просканировано {total_sources} источников. Из них {kept_count} были признаны соответствующими нашим критериям отслеживания и {skipped_count} были пропущены. Доминирующая причина пропуска — нерелевантность инструментам нашего стека или общие отраслевые дискуссии.")
    summary_lines.append("")
    
    summary_lines.append("## Выводы, требующие немедленных действий (Do Now)")
    summary_lines.append("")
    if do_now_items:
        for idx, item in enumerate(do_now_items, 1):
            summary_lines.append(f"### {idx}. {item.get('title')}")
            summary_lines.append("")
            summary_lines.append(f"- Источник: {item.get('url')}")
            summary_lines.append(f"- Затрагивает: {item.get('touches')}")
            summary_lines.append(f"- Вердикт: do now")
            summary_lines.append(f"- Почему: {item.get('why_this_verdict')}")
            summary_lines.append(f"- Если do-now или experiment: {item.get('action_plan')}")
            summary_lines.append("")
    else:
        summary_lines.append("Нет критических обновлений, требующих немедленных действий.")
        summary_lines.append("")
        
    summary_lines.append("## Эксперименты (Experiment)")
    summary_lines.append("")
    if experiment_items:
        for idx, item in enumerate(experiment_items, 1):
            summary_lines.append(f"### {idx}. {item.get('title')}")
            summary_lines.append("")
            summary_lines.append(f"- Источник: {item.get('url')}")
            summary_lines.append(f"- Затрагивает: {item.get('touches')}")
            summary_lines.append(f"- Вердикт: experiment")
            summary_lines.append(f"- Почему: {item.get('why_this_verdict')}")
            summary_lines.append(f"- Если do-now или experiment: {item.get('action_plan')}")
            summary_lines.append("")
    else:
        summary_lines.append("Нет обновлений для экспериментов.")
        summary_lines.append("")
        
    summary_lines.append("## На парковке (Parking Lot)")
    summary_lines.append("")
    if parking_items:
        for idx, item in enumerate(parking_items, 1):
            summary_lines.append(f"### {idx}. {item.get('title')}")
            summary_lines.append("")
            summary_lines.append(f"- Источник: {item.get('url')}")
            summary_lines.append(f"- Затрагивает: {item.get('touches')}")
            summary_lines.append(f"- Вердикт: parking lot")
            summary_lines.append(f"- Почему: {item.get('why_this_verdict')}")
            summary_lines.append("")
    else:
        summary_lines.append("Нет припаркованных обновлений.")
        summary_lines.append("")
        
    summary_lines.append("## Пропущенные обновления (Skipped)")
    summary_lines.append("")
    summary_lines.append(f"Всего {skipped_count} элементов были пропущены из-за того, что они не соответствовали нашему стеку технологий или были общими дискуссиями без конкретных действий.")
    summary_lines.append("")
    
    summary_md_content = "\n".join(summary_lines)

    # REPORT.md
    report_lines = []
    report_lines.append(f"# Отчет о курировании Stack Watch за {date_str}")
    report_lines.append("")
    report_lines.append("## Audit Log")
    report_lines.append("")
    report_lines.append(f"### Просканировано {total_sources} кандидатов.")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    report_lines.append("## Выводы, требующие немедленных действий (Do Now)")
    report_lines.append("")
    if do_now_items:
        for idx, item in enumerate(do_now_items, 1):
            report_lines.append(f"### {idx}. {item.get('title')}")
            report_lines.append(f"- Source: {item.get('url')} ({item.get('date', date_str)})")
            report_lines.append(f"- Touches: {item.get('touches')}")
            report_lines.append(f"- Verdict: do now")
            report_lines.append(f"- Why this verdict: {item.get('why_this_verdict')}")
            report_lines.append(f"- If do-now or experiment: {item.get('action_plan')}")
            report_lines.append(f"- Severity: {item.get('severity')}")
            tags_str = ", ".join(item.get('tags', []))
            report_lines.append(f"- Tags: {tags_str}")
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")
    else:
        report_lines.append("Нет критических обновлений, требующих немедленных действий.")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        
    report_lines.append("## Эксперименты (Experiment)")
    report_lines.append("")
    if experiment_items:
        for idx, item in enumerate(experiment_items, 1):
            report_lines.append(f"### {idx}. {item.get('title')}")
            report_lines.append(f"- Source: {item.get('url')} ({item.get('date', date_str)})")
            report_lines.append(f"- Touches: {item.get('touches')}")
            report_lines.append(f"- Verdict: experiment")
            report_lines.append(f"- Why this verdict: {item.get('why_this_verdict')}")
            report_lines.append(f"- If do-now or experiment: {item.get('action_plan')}")
            report_lines.append(f"- Severity: {item.get('severity')}")
            tags_str = ", ".join(item.get('tags', []))
            report_lines.append(f"- Tags: {tags_str}")
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")
    else:
        report_lines.append("Нет обновлений для экспериментов.")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        
    report_lines.append("## На парковке (Parking Lot)")
    report_lines.append("")
    if parking_items:
        for idx, item in enumerate(parking_items, 1):
            report_lines.append(f"### {idx}. {item.get('title')}")
            report_lines.append(f"- Source: {item.get('url')} ({item.get('date', date_str)})")
            report_lines.append(f"- Touches: {item.get('touches')}")
            report_lines.append(f"- Verdict: parking lot")
            report_lines.append(f"- Why this verdict: {item.get('why_this_verdict')}")
            report_lines.append(f"- If parking lot: {item.get('action_plan')}")
            report_lines.append(f"- Severity: {item.get('severity')}")
            tags_str = ", ".join(item.get('tags', []))
            report_lines.append(f"- Tags: {tags_str}")
            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")
    else:
        report_lines.append("Нет припаркованных обновлений.")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        
    report_lines.append("## Пропущенные кандидаты (Screened Verdict: Skip)")
    report_lines.append("")
    skipped_all = []
    for item in skipped_candidates:
        skipped_all.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "date": item.get("date", date_str),
            "reason": item.get("screened_reason", "")
        })
    for item in skipped_kept_items:
        skipped_all.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "date": item.get("date", date_str),
            "reason": item.get("why_this_verdict", "")
        })
    if skipped_all:
        for idx, item in enumerate(skipped_all, 1):
            report_lines.append(f"### {idx}. {item.get('title')}")
            report_lines.append(f"- Source: {item.get('url')} ({item.get('date')})")
            report_lines.append(f"- Reason: {item.get('reason')}")
            report_lines.append("")
    else:
        report_lines.append("Нет пропущенных кандидатов.")
        report_lines.append("")
        
    report_md_content = "\n".join(report_lines)

    # auxiliary files data
    new_urls = []
    log_additions_lines = []
    memory_index_additions_lines = []
    
    for item in do_now_items + experiment_items + parking_items:
        new_urls.append(item.get("url", ""))
        log_additions_lines.append(f"| {item.get('slug')} | {item.get('final_verdict')} | {item.get('confidence')} | {item.get('touches')} | {item.get('date', date_str)} | {item.get('url')} |")
        
    for item in parking_items:
        memory_index_additions_lines.append(f"- [Parked: {item.get('title')}]({item.get('slug')}.md) — {item.get('why_this_verdict')}")

    # Write files
    logging.info("Writing curated files...")
    
    with open(os.path.join(daily_dir, "summary.md"), 'w', encoding='utf-8') as f:
        f.write(summary_md_content)
        
    with open(os.path.join(daily_dir, "REPORT.md"), 'w', encoding='utf-8') as f:
        f.write(report_md_content)
        
    with open(os.path.join(daily_dir, "new-urls.txt"), 'w', encoding='utf-8') as f:
        f.write("\n".join(new_urls) + "\n")
        
    if log_additions_lines:
        with open(os.path.join(daily_dir, "log-additions.md"), 'w', encoding='utf-8') as f:
            f.write("\n".join(log_additions_lines) + "\n")
            
    if memory_index_additions_lines:
        with open(os.path.join(daily_dir, "memory-index-additions.txt"), 'w', encoding='utf-8') as f:
            f.write("\n".join(memory_index_additions_lines) + "\n")
            
    if findings:
        research_dir = os.path.join(daily_dir, "external-research")
        os.makedirs(research_dir, exist_ok=True)
        for finding in findings:
            filepath = os.path.join(research_dir, finding["filename"])
            content = finding["content"]
            if '\\n' in content and '\n' not in content:
                content = content.replace('\\n', '\n')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
    if memory_entries:
        mem_dir = os.path.join(daily_dir, "memory-entries")
        os.makedirs(mem_dir, exist_ok=True)
        for entry in memory_entries:
            filepath = os.path.join(mem_dir, entry["filename"])
            content = entry["content"]
            if '\\n' in content and '\n' not in content:
                content = content.replace('\\n', '\n')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
    if breaking_marker_detected:
        logging.info("Breaking marker detected! Creating breaking-marker file.")
        with open(os.path.join(daily_dir, "breaking-marker"), 'w') as f:
            f.write("breaking")

    logging.info("Curation completed successfully!")

if __name__ == "__main__":
    main()
