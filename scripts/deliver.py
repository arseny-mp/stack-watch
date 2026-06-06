#!/usr/bin/env python3
# deliver.py
# Cloud-ready Telegram delivery script for Stack Watch daily digest.
# Parses summary and findings to build formatted HTML updates, chunks them,
# sends via Telegram API, and uploads detail documents.

import os
import re
import sys
import time
import urllib.request
import urllib.parse
import json
import logging
import argparse
from datetime import datetime

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
LOG_FILE = os.path.join(WORKSPACE_DIR, "deliver.log")

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] Deliver: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

def parse_args():
    parser = argparse.ArgumentParser(description="Deliver Stack Watch daily digest to Telegram.")
    parser.add_argument("--date", help="Date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--weekly-rollup", help="Path to weekly rollup file to send instead of daily digest")
    parser.add_argument("--dry-run", action="store_true", help="Format and print message without sending")
    parser.add_argument("--force", action="store_true", help="Force send even if already sent today")
    parser.add_argument("--immediate", action="store_true", help="Immediate alert mode (only send breaking/security findings)")
    return parser.parse_args()

def html_escape(text):
    if not text:
        return ""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def get_component_layer(touches):
    touches_upper = touches.upper()
    
    # Layer 1: AI Agents & LLMs
    ai_components = [
        "CHATGPT", "CODEX", "CLAUDE", "KIMI", "HERMES", "OPENCLAW", "OLLAMA",
        "GEMINI", "NOTEBOOKLM", "PI", "GLM", "MINIMAX", "QWEN", "WISPR", "ANTIGRAVITY"
    ]
    if any(comp in touches_upper for comp in ai_components):
        return 1
        
    # Layer 2: Local Dev Environment
    dev_components = ["OBSIDIAN", "CHROME", "MACOS", "HOMEBREW", "NPM", "TMUX", "ITERM"]
    if any(comp in touches_upper for comp in dev_components):
        return 2
        
    # Layer 3: System Memory & CLI
    sys_components = ["MEM0", "DESKTOP", "GIT", "GITHUB"]
    if any(comp in touches_upper for comp in sys_components):
        return 3
        
    return 4

def parse_summary_findings(summary_file, section_name):
    if not os.path.exists(summary_file):
        return []
        
    with open(summary_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find the requested section (e.g., "## Do now" or "## Experiment")
    pattern = rf"## {re.escape(section_name)}[\s\S]*?(?=## |\Z)"
    match = re.search(pattern, content)
    if not match:
        return []
        
    section_content = match.group(0)
    findings = []
    
    # Match bullet lines like "- slug — Title"
    for line in section_content.split('\n'):
        line = line.strip()
        if line.startswith("- "):
            line = line[2:].strip()
            # Split on em-dash or double-dash surrounded by spaces
            parts = re.split(r'\s+(?:—|--)\s+', line, 1)
            if len(parts) >= 2:
                slug = parts[0].strip()
                title = parts[1].strip()
                if slug and not slug.startswith("_") and slug.lower() != "(none)" and slug.lower() != "(none)_":
                    findings.append((slug, title))
                    
    return findings

def lookup_metadata(research_dir, slug):
    fpath = os.path.join(research_dir, f"{slug}.md")
    metadata = {
        "url": "",
        "touches": "",
        "severity": "minor"
    }
    
    if not os.path.exists(fpath):
        return metadata
        
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    url_match = re.search(r'\*\*Original URL:\*\*\s*(.*)', content)
    if url_match:
        metadata["url"] = url_match.group(1).strip()
        
    touches_match = re.search(r'\*\*Touches:\*\*\s*(.*)', content)
    if touches_match:
        metadata["touches"] = touches_match.group(1).strip()
        
    severity_match = re.search(r'\*\*Severity:\*\*\s*(.*)', content, re.IGNORECASE)
    if severity_match:
        metadata["severity"] = severity_match.group(1).strip().lower()
        
    return metadata

def format_findings_group(findings_list, research_dir, immediate_mode):
    layers = {1: [], 2: [], 3: [], 4: []}
    minor_items = []
    slugs_to_send = []
    
    for slug, title in findings_list:
        meta = lookup_metadata(research_dir, slug)
        
        # In immediate mode, only send breaking/security findings
        if immediate_mode and meta["severity"] != "breaking/security":
            continue
            
        slugs_to_send.append(slug)
        
        emoji = "•"
        if meta["severity"] == "breaking/security":
            emoji = "🚨"
        elif meta["severity"] == "performance":
            emoji = "⚡"
        elif meta["severity"] == "integration":
            emoji = "🧩"
            
        title_esc = html_escape(title)
        touches_esc = html_escape(meta["touches"])
        
        if meta["url"]:
            item = f"  {emoji} <b>{title_esc}</b> ({touches_esc}) — <a href=\"{meta['url']}\">источник</a>"
        else:
            item = f"  {emoji} <b>{title_esc}</b> ({touches_esc}) — <i>ссылка не найдена</i>"
            
        if meta["severity"] == "minor":
            if meta["url"]:
                minor_items.append(f"• {title_esc} ({touches_esc}) — <a href=\"{meta['url']}\">источник</a>")
            else:
                minor_items.append(f"• {title_esc} ({touches_esc})")
            continue
            
        layer_id = get_component_layer(meta["touches"])
        layers[layer_id].append(item)
        
    # Compile text
    output = []
    
    layer_headers = {
        1: "🤖 <b>AI Agents & LLMs:</b>",
        2: "💻 <b>Local Dev Environment:</b>",
        3: "🗄️ <b>System Memory & CLI:</b>",
        4: "📦 <b>Other Components:</b>"
    }
    
    for l_id in [1, 2, 3, 4]:
        if layers[l_id]:
            output.append(layer_headers[l_id])
            output.extend(layers[l_id])
            
    if minor_items:
        output.append("<i>Мелкие обновления (Minor):</i>")
        output.extend(minor_items)
        
    return "\n".join(output), slugs_to_send

def build_message(summary_file, research_dir, date_str, immediate_mode):
    stats = ""
    if os.path.exists(summary_file):
        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'\*\*By verdict:\*\*\s*(.*)', content, re.IGNORECASE)
            if match:
                stats = match.group(1).strip()
                
    body = []
    if immediate_mode:
        body.append(f"🚨 <b>CRITICAL ALERT: Stack Watch — {date_str}</b>\n")
    else:
        if stats:
            body.append(f"📰 <b>Stack Watch — {date_str}</b> [{stats}]\n")
        else:
            body.append(f"📰 <b>Stack Watch — {date_str}</b>\n")
            
    slugs_sent = []
    
    sections = [
        ("Do now (high confidence)", "Внедрить сейчас (Do now):"),
        ("Experiment", "Эксперименты (Experiment):"),
        ("Parking", "Отложено (Parking):")
    ]
    
    has_keeps = False
    for sec_header, display_name in sections:
        sec_findings = parse_summary_findings(summary_file, sec_header)
        if sec_findings:
            formatted, s_sent = format_findings_group(sec_findings, research_dir, immediate_mode)
            if formatted:
                body.append(f"<b>{display_name}</b>")
                body.append(formatted + "\n")
                slugs_sent.extend(s_sent)
                has_keeps = True
                
    if not has_keeps:
        if immediate_mode:
            return "", []
        else:
            body.append("<i>Сегодня ничего не появилось — summary пустой.</i>")
            
    return "\n".join(body), slugs_sent

def call_telegram_api(token, method, payload, files=None):
    url = f"https://api.telegram.org/bot{token}/{method}"
    
    if files:
        # Multipart form data for sendDocument
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        parts = []
        for name, value in payload.items():
            parts.append(f"--{boundary}")
            parts.append(f'Content-Disposition: form-data; name="{name}"')
            parts.append("")
            parts.append(str(value))
            
        for name, file_info in files.items():
            filename, file_content = file_info
            parts.append(f"--{boundary}")
            parts.append(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"')
            parts.append("Content-Type: text/markdown")
            parts.append("")
            parts.append(file_content)
            
        parts.append(f"--{boundary}--")
        parts.append("")
        body = "\n".join(parts).encode('utf-8')
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    else:
        # standard json payload
        body = json.dumps(payload).encode('utf-8')
        headers = {"Content-Type": "application/json"}
        
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                if result.get("ok"):
                    return True, result
                else:
                    logging.warning(f"Telegram API response error: {result}")
        except Exception as e:
            logging.warning(f"Attempt {attempt} to call Telegram failed: {e}")
            if attempt < 3:
                time.sleep(attempt * 5)
                
    return False, None

def send_telegram_chunked(token, chat_id, message_text):
    chunks = []
    current_chunk = []
    current_length = 0
    
    lines = message_text.split('\n')
    for line in lines:
        if current_length + len(line) + 1 > 4000:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(line)
        current_length += len(line) + 1
        
    if current_chunk:
        chunks.append("\n".join(current_chunk))
        
    for idx, chunk in enumerate(chunks):
        logging.info(f"Sending message chunk {idx+1}/{len(chunks)}...")
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        success, _ = call_telegram_api(token, "sendMessage", payload)
        if not success:
            return False
        time.sleep(1)
        
    return True

def send_finding_document(token, chat_id, research_dir, slug):
    fpath = os.path.join(research_dir, f"{slug}.md")
    if not os.path.exists(fpath):
        return
        
    logging.info(f"Uploading document details for {slug}...")
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    payload = {
        "chat_id": chat_id,
        "caption": f"Детали исследования: {slug}"
    }
    files = {
        "document": (f"{slug}.md", content)
    }
    
    call_telegram_api(token, "sendDocument", payload, files)

def check_already_sent(state_file, date_str):
    if not os.path.exists(state_file):
        return False
    with open(state_file, 'r', encoding='utf-8') as f:
        dates = f.read().splitlines()
    return date_str in dates

def mark_as_sent(state_file, date_str):
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    dates = []
    if os.path.exists(state_file):
        with open(state_file, 'r', encoding='utf-8') as f:
            dates = f.read().splitlines()
            
    if date_str not in dates:
        dates.append(date_str)
        dates.sort()
        with open(state_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(dates) + "\n")

def main():
    args = parse_args()
    
    date_str = args.date
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
        
    logging.info(f"Delivery run starting for date: {date_str}")
    
    # Resolve directories
    processed_dir = os.path.join(WORKSPACE_DIR, "processed")
    daily_drop_dir = os.path.join(WORKSPACE_DIR, date_str)
    
    # Read state files inside workspace (committed back to git)
    state_file = os.path.join(processed_dir, "updates-last-sent.txt")
    state_file_immediate = os.path.join(processed_dir, "updates-immediate-sent.txt")
    state_file_weekly = os.path.join(processed_dir, "updates-weekly-sent.txt")
    
    # Setup context
    if args.weekly_rollup:
        summary_file = args.weekly_rollup
        research_dir = os.path.join(processed_dir, date_str, "external-research")
        target_state_file = state_file_weekly
    else:
        # Read from processed/date if drop has been bridged, or fall back to daily drop directory
        processed_daily_dir = os.path.join(processed_dir, date_str)
        if os.path.exists(processed_daily_dir):
            summary_file = os.path.join(processed_daily_dir, "summary.md")
            research_dir = os.path.join(processed_daily_dir, "external-research")
        else:
            summary_file = os.path.join(daily_drop_dir, "summary.md")
            research_dir = os.path.join(daily_drop_dir, "external-research")
            
        target_state_file = state_file_immediate if args.immediate else state_file
        
    logging.info(f"Summary file path: {summary_file}")
    logging.info(f"Research dir path: {research_dir}")
    
    # Guard against double delivery
    if not args.force and not args.dry_run:
        if check_already_sent(target_state_file, date_str):
            logging.info(f"Already sent updates for {date_str}. Use --force to override. Exiting.")
            sys.exit(0)
            
    # Resolve message
    if args.weekly_rollup:
        if not os.path.exists(summary_file):
            logging.error(f"Weekly rollup file not found: {summary_file}")
            sys.exit(1)
        with open(summary_file, 'r', encoding='utf-8') as f:
            msg_text = f.read()
        slugs_to_send = []
    else:
        if not os.path.exists(summary_file):
            logging.warning(f"Summary file not found: {summary_file}. Nothing to send.")
            sys.exit(0)
        msg_text, slugs_to_send = build_message(summary_file, research_dir, date_str, args.immediate)
        
    if not msg_text:
        logging.info("No messages compiled (possibly no breaking alerts in immediate mode). Exiting.")
        sys.exit(0)
        
    # Dry run outputs
    if args.dry_run:
        logging.info("===== DRY RUN =====")
        print(msg_text)
        logging.info(f"Detail document slugs to send: {slugs_to_send}")
        logging.info("===== END DRY RUN =====")
        sys.exit(0)
        
    # Resolve credentials
    token = os.environ.get("TELEGRAM_TOKEN_UPDATES")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        logging.error("TELEGRAM_TOKEN_UPDATES or TELEGRAM_CHAT_ID environment variables are missing.")
        sys.exit(1)
        
    # Deliver Message
    success = send_telegram_chunked(token, chat_id, msg_text)
    
    if success:
        logging.info("Main notification delivered successfully.")
        # Mark as sent
        mark_as_sent(target_state_file, date_str)
        
        # Upload detail documents
        for slug in slugs_to_send:
            send_finding_document(token, chat_id, research_dir, slug)
            time.sleep(1)
            
        logging.info("Delivery process completed.")
    else:
        logging.error("Failed to deliver notification to Telegram.")
        sys.exit(1)

if __name__ == "__main__":
    main()
