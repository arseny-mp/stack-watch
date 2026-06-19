#!/usr/bin/env python3
import os
import sys
import json
import logging
import argparse
import urllib.request
from datetime import datetime

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
LOG_FILE = os.path.join(WORKSPACE_DIR, "deliver.log")

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] Failure-Deliver: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

def parse_args():
    parser = argparse.ArgumentParser(description="Deliver pipeline failure alert to Telegram.")
    parser.add_argument("--run-id", required=True, help="GitHub Action Run ID")
    return parser.parse_args()

def call_telegram_api(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    body = json.dumps(payload).encode('utf-8')
    headers = {"Content-Type": "application/json"}
    
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result.get("ok", False)
    except Exception as e:
        logging.error(f"Failed to call Telegram API: {e}")
        return False

def main():
    args = parse_args()
    
    token = os.environ.get("TELEGRAM_TOKEN_UPDATES")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        logging.error("Missing TELEGRAM_TOKEN_UPDATES or TELEGRAM_CHAT_ID env variables.")
        sys.exit(1)
        
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    text = (
        f"❌ <b>Stack Watch Cloud Pipeline — Сбой!</b>\n\n"
        f"📅 Время: {date_str} (UTC)\n"
        f"⚠️ Шаг конвейера завершился с ошибкой.\n\n"
        f"🔍 Логи и детали запуска:\n"
        f"https://github.com/arseny-mp/stack-watch/actions/runs/{args.run_id}"
    )
    
    logging.info(f"Sending failure alert for run {args.run_id} to Telegram chat {chat_id}...")
    success = call_telegram_api(token, chat_id, text)
    if success:
        logging.info("Failure alert sent successfully.")
    else:
        logging.error("Failed to send failure alert.")
        sys.exit(1)

if __name__ == "__main__":
    main()
