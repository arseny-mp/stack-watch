#!/usr/bin/env python3
import os
import re
import sys
import json
import logging
import urllib.request
from datetime import datetime

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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={key}"
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
            with urllib.request.urlopen(req, timeout=90) as resp:
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

    prompt = f"""You are the autonomous Curation Agent for the Stack Watch news system.
Your job is to process today's daily updates, apply the rubric, consult active learnings exceptions, and generate the final curation files.

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
2. Generate all the standard output files:
   - `summary.md`: General statistics and categorized list of updates (Do now, Experiment, Parking, Unconfirmed, Skipped).
   - `REPORT.md`: Audit log of candidates, sources, and calibration decisions.
   - Detailed markdown files for keeps: Create the file contents for each actionable update (verdict: do now, experiment, parking lot). Place them under "findings" with a filename matching "<slug>.md".
   - Memory entries: For parked or experiment updates, generate a markdown file for the "memory_entries" array with a filename like "parked_<slug>.md" or "experiment_<slug>.md".
   - Log additions: Create rows to append to the master log file (piped columns format).
   - Memory index additions: Create lines to append to the master index.
3. Detect if a breaking-marker file is warranted (if any critical/breaking severity updates are verified).

Respond with a JSON object matching the requested schema. Ensure all Russian translations are precise and follow standard professional language.
"""

    response_schema = {
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
            "findings": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "filename": {"type": "STRING", "description": "The filename (e.g. slug.md)"},
                        "content": {"type": "STRING", "description": "The complete markdown content for this finding"}
                    },
                    "required": ["filename", "content"]
                }
            },
            "memory_entries": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "filename": {"type": "STRING", "description": "The filename (e.g. parked_slug.md or experiment_slug.md)"},
                        "content": {"type": "STRING", "description": "The complete markdown content for the memory entry"}
                    },
                    "required": ["filename", "content"]
                }
            },
            "breaking_marker_detected": {
                "type": "BOOLEAN",
                "description": "True if there is any critical/breaking severity finding that warrants a breaking-marker file"
            }
        },
        "required": [
            "summary_md", "report_md", "new_urls", "log_additions_lines",
            "memory_index_additions_lines", "findings", "memory_entries", "breaking_marker_detected"
        ]
    }

    logging.info("Querying Gemini for daily curation...")
    try:
        result = call_gemini(api_key, prompt, response_schema)
    except Exception as e:
        logging.error(f"Gemini Curation call failed: {e}")
        sys.exit(1)

    # Write files
    logging.info("Writing curated files...")
    
    # summary.md
    with open(os.path.join(daily_dir, "summary.md"), 'w', encoding='utf-8') as f:
        f.write(result["summary_md"])
        
    # REPORT.md
    with open(os.path.join(daily_dir, "REPORT.md"), 'w', encoding='utf-8') as f:
        f.write(result["report_md"])
        
    # new-urls.txt
    with open(os.path.join(daily_dir, "new-urls.txt"), 'w', encoding='utf-8') as f:
        f.write("\n".join(result["new_urls"]) + "\n")
        
    # log-additions.md
    if result["log_additions_lines"]:
        with open(os.path.join(daily_dir, "log-additions.md"), 'w', encoding='utf-8') as f:
            f.write("\n".join(result["log_additions_lines"]) + "\n")
            
    # memory-index-additions.txt
    if result["memory_index_additions_lines"]:
        with open(os.path.join(daily_dir, "memory-index-additions.txt"), 'w', encoding='utf-8') as f:
            f.write("\n".join(result["memory_index_additions_lines"]) + "\n")
            
    # findings (under external-research/)
    if result["findings"]:
        research_dir = os.path.join(daily_dir, "external-research")
        os.makedirs(research_dir, exist_ok=True)
        for finding in result["findings"]:
            filepath = os.path.join(research_dir, finding["filename"])
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(finding["content"])
                
    # memory_entries (under memory-entries/)
    if result["memory_entries"]:
        mem_dir = os.path.join(daily_dir, "memory-entries")
        os.makedirs(mem_dir, exist_ok=True)
        for entry in result["memory_entries"]:
            filepath = os.path.join(mem_dir, entry["filename"])
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(entry["content"])
                
    # breaking-marker
    if result["breaking_marker_detected"]:
        logging.info("Breaking marker detected! Creating breaking-marker file.")
        with open(os.path.join(daily_dir, "breaking-marker"), 'w') as f:
            f.write("breaking")

    logging.info("Curation completed successfully!")

if __name__ == "__main__":
    main()
