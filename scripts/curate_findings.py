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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
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
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=180) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                text = res["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except urllib.error.HTTPError as e:
            if e.code in [429, 500, 503] and attempt < 3:
                sleep_time = attempt * 10
                logging.warning(f"Gemini Curation returned status {e.code}. Retrying in {sleep_time}s (attempt {attempt}/3)...")
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

    # Call Gemini API
    api_key = get_api_key("GEMINI_API_KEY") or get_api_key("GOOGLE_API_KEY")
    if not api_key:
        logging.error("No GEMINI_API_KEY or GOOGLE_API_KEY found.")
        sys.exit(1)

    # --- Step 1: Classification & Summarization ---
    step1_prompt = f"""You are the autonomous Curation Agent for the Stack Watch news system.
Your job is to process today's daily updates, apply the rubric, consult active learnings exceptions, and generate the final curation summaries.

Today's Date: {date_str}

=== Rubric Guidelines ===
{rubric_content}

=== Active Learnings & Corrections ===
{learnings_content}

=== Raw Candidate Feeds ===
{json.dumps(updates, indent=2)}

Tasks:
1. For each candidate in the feed:
   - If `"screened_verdict"` is `"skip"`, add it to the list of skipped updates with its skip reason.
   - If `"screened_verdict"` is `"keep"`, evaluate it against the watch list components and classification heuristics. Determine the final verdict: "do now", "experiment", "parking lot", or "skip".
2. Generate the summary files and log additions:
   - `summary.md`: General statistics and categorized list of updates (Do now, Experiment, Parking, Unconfirmed, Skipped).
   - `REPORT.md`: Audit log of candidates, sources, and calibration decisions.
   - `new_urls`: List of all unique URLs processed.
   - `log_additions_lines`: Lines to append to external-research-log.md, each line formatted as: | slug | verdict | confidence | touches | date | url |
   - `memory_index_additions_lines`: Lines to append to MEMORY.md, e.g., - [Parked: title](parked_slug.md) — reason.
3. Identify all actionable findings (verdict: do now, experiment, parking lot) and extract their metadata (slug, title, verdict, confidence, sources, touches, url, severity). Provide their raw candidate data in candidate_data.
4. Detect if a breaking-marker file is warranted (if any critical/breaking severity updates are verified).

Respond with a JSON object matching the requested schema. Ensure all Russian translations are precise and follow standard professional language.
"""

    step1_schema = {
        "type": "OBJECT",
        "properties": {
            "summary_md": {"type": "STRING", "description": "The complete markdown content for summary.md"},
            "report_md": {"type": "STRING", "description": "The complete text content for REPORT.md"},
            "new_urls": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "List of all unique URLs processed/cited during the run"
            },
            "log_additions_lines": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "Lines to append to external-research-log.md, each line formatted as: | slug | verdict | confidence | touches | date | url |"
            },
            "memory_index_additions_lines": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "Lines to append to MEMORY.md, e.g. - [Parked: title](parked_slug.md) — reason"
            },
            "actionable_findings": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "slug": {"type": "STRING", "description": "The finding slug (e.g., lowercase-title-slug)"},
                        "title": {"type": "STRING"},
                        "verdict": {"type": "STRING", "description": "do now | experiment | parking"},
                        "confidence": {"type": "STRING", "description": "high | medium | low"},
                        "sources": {"type": "STRING"},
                        "touches": {"type": "STRING"},
                        "url": {"type": "STRING"},
                        "severity": {"type": "STRING"},
                        "candidate_data": {"type": "STRING", "description": "The raw JSON or description of the candidate from the input feed"}
                    },
                    "required": ["slug", "title", "verdict", "confidence", "sources", "touches", "url", "severity", "candidate_data"]
                },
                "description": "Metadata for findings with do now, experiment, or parking verdicts"
            },
            "breaking_marker_detected": {
                "type": "BOOLEAN",
                "description": "True if there is any critical/breaking severity finding that warrants a breaking-marker file"
            }
        },
        "required": [
            "summary_md", "report_md", "new_urls", "log_additions_lines",
            "memory_index_additions_lines", "actionable_findings", "breaking_marker_detected"
        ]
    }

    logging.info("Querying Gemini for daily curation (Step 1: Classification & Summary)...")
    try:
        step1_result = call_gemini(api_key, step1_prompt, step1_schema)
    except Exception as e:
        logging.error(f"Gemini Curation Step 1 failed: {e}")
        sys.exit(1)

    # --- Step 2: Detail Generation for Actionable Findings ---
    actionable_findings = step1_result.get("actionable_findings", [])
    logging.info(f"Step 1 completed. Found {len(actionable_findings)} actionable findings to curate.")

    findings = []
    memory_entries = []

    step2_schema = {
        "type": "OBJECT",
        "properties": {
            "finding_content": {"type": "STRING", "description": "The complete markdown content for the slug.md file following the template"},
            "memory_entry_content": {"type": "STRING", "description": "The complete markdown content for the memory entry (if verdict is parking or experiment, otherwise empty string)"}
        },
        "required": ["finding_content", "memory_entry_content"]
    }

    for idx, finding in enumerate(actionable_findings):
        slug = finding.get("slug")
        verdict = finding.get("verdict")
        logging.info(f"Generating details for finding {idx+1}/{len(actionable_findings)}: {slug} ({verdict})...")

        step2_prompt = f"""You are the Curation Agent for Stack Watch.
Generate the detailed findings content and memory entry (if needed) for the following tech stack update:

Today's Date: {date_str}
Finding Title: {finding['title']}
Verdict: {verdict}
Confidence: {finding['confidence']}
Sources: {finding['sources']}
Touches: {finding['touches']}
Original URL: {finding['url']}
Severity: {finding['severity']}
Candidate Raw Data: {finding['candidate_data']}

Tasks:
1. Generate the detailed markdown content for this finding.
   The content MUST follow this template EXACTLY:
   # {finding['title']}
   **Verdict:** {verdict}
   **Confidence:** {finding['confidence']}
   **Sources:** {finding['sources']}
   **Source count:** {len(finding['sources'].split(','))}
   **Touches:** {finding['touches']}
   **Original URL:** {finding['url']}
   **Verify URL:** ok
   **Date:** {date_str}

   ## Summary
   [Must be written in Russian. Provide an expanded, detailed summary structured into two clear parts:
   1. Что это такое: подробное и развернутое объяснение сути обновления, нового инструмента или фичи.
   2. Зачем мне это нужно: развернутое объяснение практической пользы, ценности для рабочего процесса оператора и применимости в его стеке.]

   ## What changes
   [Detailed description of technical changes and features in Russian]

2. If the verdict is 'parking' or 'experiment', generate the memory entry content.
   The memory entry content MUST follow this template EXACTLY:
   ---
   name: {verdict}-{slug}
   description: [Description in Russian, max 120 chars]
   metadata:
     type: project
   ---

   Memory entry for {finding['title']} identified {date_str} via Stack Watch.

   **Trigger to revisit:** [Concrete condition under which to revisit this, in Russian]

   **Why parked/experiment:** [2-3 sentences explaining why it was parked or set as experiment, in Russian]

   **Source(s):** {finding['url']}

   **Touches:** {finding['touches']}

Respond with a JSON object matching the requested schema. Ensure all Russian translations are precise and follow standard professional language.
"""

        try:
            if idx > 0:
                time.sleep(1) # Small rate-limit guard delay
            
            step2_result = call_gemini(api_key, step2_prompt, step2_schema)
            
            findings.append({
                "filename": f"{slug}.md",
                "content": step2_result["finding_content"]
            })
            
            if step2_result.get("memory_entry_content") and verdict in ["parking", "experiment"]:
                prefix = "parked" if verdict == "parking" else "experiment"
                memory_entries.append({
                    "filename": f"{prefix}_{slug}.md",
                    "content": step2_result["memory_entry_content"]
                })
        except Exception as e:
            logging.error(f"Failed to generate details for finding {slug}: {e}")
            continue

    # Write files
    logging.info("Writing curated files...")
    
    # summary.md
    with open(os.path.join(daily_dir, "summary.md"), 'w', encoding='utf-8') as f:
        f.write(step1_result["summary_md"])
        
    # REPORT.md
    with open(os.path.join(daily_dir, "REPORT.md"), 'w', encoding='utf-8') as f:
        f.write(step1_result["report_md"])
        
    # new-urls.txt
    with open(os.path.join(daily_dir, "new-urls.txt"), 'w', encoding='utf-8') as f:
        f.write("\n".join(step1_result["new_urls"]) + "\n")
        
    # log-additions.md
    if step1_result["log_additions_lines"]:
        with open(os.path.join(daily_dir, "log-additions.md"), 'w', encoding='utf-8') as f:
            f.write("\n".join(step1_result["log_additions_lines"]) + "\n")
            
    # memory-index-additions.txt
    if step1_result["memory_index_additions_lines"]:
        with open(os.path.join(daily_dir, "memory-index-additions.txt"), 'w', encoding='utf-8') as f:
            f.write("\n".join(step1_result["memory_index_additions_lines"]) + "\n")
            
    # findings (under external-research/)
    if findings:
        research_dir = os.path.join(daily_dir, "external-research")
        os.makedirs(research_dir, exist_ok=True)
        for finding in findings:
            filepath = os.path.join(research_dir, finding["filename"])
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(finding["content"])
                
    # memory_entries (under memory-entries/)
    if memory_entries:
        mem_dir = os.path.join(daily_dir, "memory-entries")
        os.makedirs(mem_dir, exist_ok=True)
        for entry in memory_entries:
            filepath = os.path.join(mem_dir, entry["filename"])
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(entry["content"])
                
    # breaking-marker
    if step1_result["breaking_marker_detected"]:
        logging.info("Breaking marker detected! Creating breaking-marker file.")
        with open(os.path.join(daily_dir, "breaking-marker"), 'w') as f:
            f.write("breaking")

    logging.info("Curation completed successfully!")

if __name__ == "__main__":
    main()
