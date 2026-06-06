#!/usr/bin/env python3
import os
import sys
import json
import logging
import urllib.request
import subprocess
from datetime import datetime

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

# Resolve log file path based on platform directory availability
if os.path.exists("/Users/user/Library/Logs"):
    LOG_FILE = "/Users/user/Library/Logs/poll-feeds-research.stdout.log"
else:
    LOG_FILE = os.path.join(WORKSPACE_DIR, "poll-feeds-research.log")


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] AI-Screening: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

WATCH_LIST = [
    "ChatGPT", "Codex", "Claude Desktop", "Claude Cowork", "Claude Code CLI",
    "Kimi", "Hermes", "OpenClaw", "Ollama", "Gemini", "NotebookLM", "Pi Coding Agent",
    "GLM", "Minimax", "Qwen", "Wispr Flow", "Antigravity", "YouTube", "Telegram",
    "Obsidian", "Mem0", "Git", "GitHub", "Chrome", "Desktop Commander",
    "macOS", "Homebrew", "npm", "tmux", "iTerm2"
]

SKIP_LIST = [
    "AI tools we do not use (e.g. Cursor, Aider, Replit Agent, Devin, generic agent frameworks not on watch list)",
    "Growth marketing, sales, lead generation, cold email, CRM",
    "Personal productivity outside development (e.g. daily plan templates, journaling, newsletter writing)",
    "Onboarding or beginner tutorials for tools we already use",
    "Round-up videos/articles listing 10+ tools without depth",
    "Industry/market commentary (funding rounds, executive moves, model leaderboard rankings without feature changes)"
]

def get_api_key(name):
    # Try env first
    val = os.environ.get(name)
    if val:
        return val
    # Try Keychain only on macOS
    import sys
    if sys.platform == 'darwin':
        try:
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

def call_gemini(key, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    import time
    import urllib.error
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                text = res["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except urllib.error.HTTPError as e:
            if e.code in [429, 500, 503] and attempt < 3:
                sleep_time = attempt * 5
                logging.warning(f"Gemini API returned status {e.code}. Retrying in {sleep_time}s (attempt {attempt}/3)...")
                time.sleep(sleep_time)
            else:
                raise e


def screen_candidates(candidates):
    if not candidates:
        return []
        
    prompt = f"""You are a preliminary filter agent for the Stack Watch news system.
Your job is to screen a list of updates and classify each of them as "keep" or "skip".

Watch list (Keep if the update touches any of these components):
{json.dumps(WATCH_LIST)}

Skip list (Skip if the update is primarily about):
{json.dumps(SKIP_LIST)}

Input candidates:
{json.dumps(candidates, indent=2)}

Respond with a JSON array matching this format EXACTLY:
[
  {{"id": <candidate_id>, "screened_verdict": "keep" | "skip", "reason": "one-sentence explanation in Russian"}}
]
"""
    
    # Try Gemini
    gemini_key = get_api_key("GEMINI_API_KEY") or get_api_key("GOOGLE_API_KEY")
    if gemini_key:
        logging.info("Calling Gemini Flash Lite API...")
        try:
            return call_gemini(gemini_key, prompt)
        except Exception as e:
            logging.error(f"Gemini API call failed: {e}.")
            
    # Return fallback: keep all if Gemini fails/is unavailable
    logging.warning("Gemini unavailable. Keeping all candidates by default.")
    return [{"id": c["id"], "screened_verdict": "keep", "reason": "Gemini unavailable — kept by default"} for c in candidates]

def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    daily_dir = os.path.join(WORKSPACE_DIR, date_str)
    feed_file = os.path.join(daily_dir, "feed_updates.json")
    
    if not os.path.exists(feed_file):
        logging.info("No daily feed_updates.json found to screen.")
        sys.exit(0)
        
    with open(feed_file, 'r', encoding='utf-8') as f:
        updates = json.load(f)
        
    if not updates:
        logging.info("Daily feed_updates.json is empty. No screening needed.")
        sys.exit(0)
        
    # Prepare batch candidates
    candidates = []
    for idx, item in enumerate(updates):
        candidates.append({
            "id": idx,
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "component": item.get("component", "")
        })
        
    logging.info(f"Screening {len(candidates)} candidates...")
    results = screen_candidates(candidates)
    
    # Merge results
    result_map = {r["id"]: r for r in results if "id" in r}
    screened_out = 0
    
    for idx, item in enumerate(updates):
        res = result_map.get(idx, {"screened_verdict": "keep", "reason": "No screening result"})
        item["screened_verdict"] = res.get("screened_verdict", "keep")
        item["screened_reason"] = res.get("reason", "")
        if item["screened_verdict"] == "skip":
            screened_out += 1
            
    with open(feed_file, 'w', encoding='utf-8') as f:
        json.dump(updates, f, indent=2)
        
    logging.info(f"Screening completed! Screened out {screened_out}/{len(updates)} noisy updates.")

if __name__ == "__main__":
    main()
