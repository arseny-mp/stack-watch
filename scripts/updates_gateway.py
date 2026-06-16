#!/usr/bin/env python3
import os
import sys
import json
import time
import subprocess
import logging
import urllib.request
import urllib.parse

# Import NotebookLMClient
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from notebooklm_client import NotebookLMClient

# --- Configuration ---
WORKSPACE_DIR = "/Users/user/Projects/Stack Watch"
SUMMARY_DIR = "/Users/user/Projects/Project Instructions Template/project-status/_summary"
TOKEN_KEY = "TELEGRAM_TOKEN_UPDATES"
LOG_FILE = "/Users/user/Library/Logs/stack-watch-gateway.log"
STATE_FILE = "/Users/user/.hermes/state/gateway-offset.txt"

# --- Logging ---
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_telegram_token():
    try:
        result = subprocess.run(
            ['security', 'find-generic-password', '-a', 'hermes', '-s', TOKEN_KEY, '-w'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return result.stdout.decode('utf-8').strip()
    except Exception as e:
        logging.error(f"Failed to fetch Telegram token from Keychain: {e}")
        return None

def telegram_api_call(token, method, payload=None):
    url = f"https://api.telegram.org/bot{token}/{method}"
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        logging.error(f"Telegram API call {method} failed: {e}")
        return None

def load_offset():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return int(f.read().strip())
        except Exception:
            return 0
    return 0

def save_offset(offset):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    try:
        with open(STATE_FILE, 'w') as f:
            f.write(str(offset))
    except Exception as e:
        logging.error(f"Failed to save gateway offset: {e}")

def move_finding(summary_file_path, slug, target_verdict):
    headers = {
        'do_now': '## Do now (high confidence)',
        'experiment': '## Experiment',
        'park': '## Parking',
        'skip': '## Skipped'
    }
    
    if target_verdict not in headers:
        return False, "Invalid target verdict"
        
    target_header = headers[target_verdict]
    
    if not os.path.exists(summary_file_path):
        return False, f"File {summary_file_path} not found"
        
    with open(summary_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.splitlines()
    
    # Locate the finding line
    finding_line = None
    finding_index = -1
    for i, line in enumerate(lines):
        if line.strip().startswith(f"- {slug} —") or line.strip().startswith(f"- {slug} --") or line.strip() == f"- {slug}":
            finding_line = line
            finding_index = i
            break
            
    if not finding_line:
        for i, line in enumerate(lines):
            if line.strip().startswith(f"- {slug}"):
                finding_line = line
                finding_index = i
                break
                
    if not finding_line:
        return False, f"Finding {slug} not found in summary file"
        
    # Remove it
    lines.pop(finding_index)
    
    # Locate target header
    target_index = -1
    for i, line in enumerate(lines):
        if line.strip().startswith(target_header):
            target_index = i
            break
            
    if target_index == -1:
        lines.append(target_header)
        lines.append("")
        lines.append(finding_line)
    else:
        insert_pos = target_index + 1
        while insert_pos < len(lines) and (lines[insert_pos].strip() == "" or "none" in lines[insert_pos].lower()):
            if "none" in lines[insert_pos].lower():
                lines.pop(insert_pos)
                continue
            insert_pos += 1
        lines.insert(insert_pos, finding_line)
        
    # Re-save temp content
    temp_content = "\n".join(lines) + "\n"
    with open(summary_file_path, 'w', encoding='utf-8') as f:
        f.write(temp_content)
        
    # Ensure none placeholders on empty sections
    ensure_none_placeholders(summary_file_path)
    return True, "Success"

def ensure_none_placeholders(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.splitlines()
    
    sections = [
        "## Do now (high confidence)",
        "## Experiment",
        "## Parking",
        "## Unconfirmed / Single Domain (low confidence)",
        "## Skipped"
    ]
    
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        if any(line.strip().startswith(s) for s in sections):
            j = i + 1
            has_bullets = False
            while j < len(lines):
                next_line = lines[j]
                if next_line.strip().startswith("## "):
                    break
                if next_line.strip().startswith("- "):
                    has_bullets = True
                    break
                j += 1
            if not has_bullets:
                new_lines.append("")
                new_lines.append("_(none)_")
                while i + 1 < len(lines) and ("none" in lines[i+1].lower() or lines[i+1].strip() == ""):
                    i += 1
        i += 1
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(new_lines) + "\n")

def get_message_slugs(summary_file_path):
    # Parses the summary file to extract all remaining slugs that should have buttons
    if not os.path.exists(summary_file_path):
        return []
    slugs = []
    sections = ["## Do now (high confidence)", "## Experiment", "## Parking"]
    active = False
    with open(summary_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if any(line.startswith(s) for s in sections):
                active = True
                continue
            elif line.startswith("## "):
                active = False
            if active and line.strip().startswith("- "):
                parts = line.strip()[2:].split(" — ")
                if len(parts) >= 1:
                    slug = parts[0].strip()
                    if slug and not slug.startswith("_"):
                        slugs.append(slug)
    return slugs

def handle_callback(token, callback):
    callback_id = callback["id"]
    data = callback.get("data", "")
    message = callback.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")
    
    if not data or not chat_id or not message_id:
        return
        
    logging.info(f"Received callback: {data} from message {message_id}")
    
    # Parse callback: action:slug:date
    parts = data.split(":")
    if len(parts) < 3:
        telegram_api_call(token, "answerCallbackQuery", {"callback_query_id": callback_id, "text": "Ошибка: неверный формат данных"})
        return
        
    action, slug, date_str = parts[0], parts[1], parts[2]
    summary_file = os.path.join(SUMMARY_DIR, f"{date_str}-stack-watch.md")
    
    success, msg = move_finding(summary_file, slug, action)
    if not success:
        logging.error(f"Failed to move finding: {msg}")
        telegram_api_call(token, "answerCallbackQuery", {"callback_query_id": callback_id, "text": f"Ошибка: {msg}"})
        return
        
    # Answer query
    telegram_api_call(token, "answerCallbackQuery", {"callback_query_id": callback_id, "text": f"Выполнено: {action} для {slug}"})
    
    # Regenerate daily message using updates-news-deliver.sh in dry-run
    try:
        result = subprocess.run(
            [os.path.join(WORKSPACE_DIR, "scripts/updates-news-deliver.sh"), "--date", date_str, "--dry-run"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        dry_run_output = result.stdout.decode('utf-8')
        # Extract body between the dry run boundary lines
        lines = dry_run_output.splitlines()
        msg_body = []
        capture = False
        for line in lines:
            if line.startswith("===== DRY RUN"):
                if not capture:
                    capture = True
                    continue
                else:
                    capture = False
            if capture:
                msg_body.append(line)
        new_text = "\n".join(msg_body).strip()
    except Exception as e:
        logging.error(f"Failed to regenerate dry-run message: {e}")
        return
        
    # Build updated inline keyboard for remaining findings
    remaining_slugs = get_message_slugs(summary_file)
    rows = []
    for r_slug in remaining_slugs:
        rows.append([
            {"text": f"🅿️ Park: {r_slug}", "callback_data": f"park:{r_slug}:{date_str}"},
            {"text": f"❌ Skip: {r_slug}", "callback_data": f"skip:{r_slug}:{date_str}"}
        ])
    reply_markup = {"inline_keyboard": rows} if rows else None
    
    # Edit the Telegram message in-place
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": new_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
        
    telegram_api_call(token, "editMessageText", payload)

def handle_message(token, msg):
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "")
    message_id = msg.get("message_id")
    
    if not text or not chat_id:
        return
        
    if text.startswith("/research "):
        target = text[10:].strip()
        logging.info(f"Received research command for: {target}")
        
        # Send initial status message
        status_res = telegram_api_call(token, "sendMessage", {
            "chat_id": chat_id,
            "text": "🔍 <b>Запуск экспресс-исследования через NotebookLM...</b>\nЗагружаем источник и генерируем саммари.",
            "parse_mode": "HTML",
            "reply_to_message_id": message_id
        })
        status_msg_id = status_res.get("result", {}).get("message_id") if status_res else None
        
        client = NotebookLMClient()
        try:
            client.connect()
            notebook_id = client.find_or_create_notebook("On-Demand Research")
            
            # Check if it's a URL
            if target.startswith("http://") or target.startswith("https://"):
                client.add_url(notebook_id, target)
            else:
                client.add_text(notebook_id, f"Query Research - {int(time.time())}", target)
                
            # Wait for ingestion
            time.sleep(15)
            
            # Query the summary
            summary = client.query_notebook(
                notebook_id,
                "Сделай подробный структурированный конспект этого источника на русском языке. Выдели ключевые мысли, новые термины/фичи и практические выводы для разработчика."
            )
            
            # Send the final summary
            if status_msg_id:
                telegram_api_call(token, "editMessageText", {
                    "chat_id": chat_id,
                    "message_id": status_msg_id,
                    "text": f"📋 <b>Результаты исследования:</b>\n\n{summary}",
                    "parse_mode": "HTML"
                })
            else:
                telegram_api_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": f"📋 <b>Результаты исследования:</b>\n\n{summary}",
                    "parse_mode": "HTML",
                    "reply_to_message_id": message_id
                })
                
        except Exception as e:
            logging.error(f"On-demand research failed: {e}")
            error_msg = f"❌ <b>Ошибка исследования:</b> {str(e)}"
            if status_msg_id:
                telegram_api_call(token, "editMessageText", {
                    "chat_id": chat_id,
                    "message_id": status_msg_id,
                    "text": error_msg,
                    "parse_mode": "HTML"
                })
            else:
                telegram_api_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": error_msg,
                    "parse_mode": "HTML",
                    "reply_to_message_id": message_id
                })
        finally:
            client.disconnect()

def main():
    logging.info("Starting Stack Watch Telegram Callback Gateway...")
    token = get_telegram_token()
    if not token:
        logging.error("No Telegram token found. Exiting.")
        sys.exit(1)
        
    offset = load_offset()
    logging.info(f"Loaded offset: {offset}")
    
    while True:
        try:
            updates = telegram_api_call(token, "getUpdates", {
                "offset": offset,
                "timeout": 30,
                "allowed_updates": ["callback_query", "message"]
            })
            
            if updates and updates.get("ok"):
                for update in updates.get("result", []):
                    update_id = update["update_id"]
                    offset = update_id + 1
                    save_offset(offset)
                    
                    callback = update.get("callback_query")
                    if callback:
                        handle_callback(token, callback)
                        
                    msg = update.get("message")
                    if msg:
                        handle_message(token, msg)
            else:
                logging.debug("No updates received.")
        except KeyboardInterrupt:
            logging.info("Gateway daemon stopping...")
            break
        except Exception as e:
            logging.error(f"Error in main polling loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
