#!/usr/bin/env python3
# deliver_email.py
# Cloud-ready Email delivery script for Stack Watch daily digest.
# Parses summary and findings to build a beautifully styled HTML email,
# and sends it via Gmail SMTP using a Google Workspace account.

import os
import re
import sys
import time
import smtplib
import logging
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
LOG_FILE = os.path.join(WORKSPACE_DIR, "deliver_email.log")

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] Email-Deliver: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

def parse_args():
    parser = argparse.ArgumentParser(description="Deliver Stack Watch daily digest via Email.")
    parser.add_argument("--date", help="Date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--weekly-rollup", help="Path to weekly rollup file to send instead of daily digest")
    parser.add_argument("--dry-run", action="store_true", help="Format and print HTML email without sending")
    parser.add_argument("--force", action="store_true", help="Force send even if already sent today")
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
    daily_dir = os.path.dirname(summary_file)
    log_additions_file = os.path.join(daily_dir, "log-additions.md")
    
    if os.path.exists(log_additions_file):
        findings = []
        with open(log_additions_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line.startswith("|"):
                    continue
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) < 2:
                    continue
                slug = parts[0]
                verdict = parts[1].lower()
                
                # Check mapping
                match = False
                if section_name == "Do now (high confidence)" and verdict == "do now":
                    match = True
                elif section_name == "Experiment" and verdict == "experiment":
                    match = True
                elif section_name == "Parking" and verdict in ["parking", "parking lot"]:
                    match = True
                    
                if match:
                    # Lookup title in external-research/{slug}.md
                    research_dir = os.path.join(daily_dir, "external-research")
                    fpath = os.path.join(research_dir, f"{slug}.md")
                    title = slug
                    if os.path.exists(fpath):
                        with open(fpath, 'r', encoding='utf-8') as rf:
                            for r_line in rf:
                                r_line = r_line.strip()
                                if not r_line:
                                    continue
                                if '\\n' in r_line:
                                    r_line = r_line.split('\\n')[0].strip()
                                if r_line.startswith("#"):
                                    title = r_line[1:].strip()
                                break
                    findings.append((slug, title))
        return findings
    else:
        if not os.path.exists(summary_file):
            return []
            
        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        pattern = rf"## {re.escape(section_name)}[\s\S]*?(?=## |\Z)"
        match = re.search(pattern, content)
        if not match:
            return []
            
        section_content = match.group(0)
        findings = []
        
        for line in section_content.split('\n'):
            line = line.strip()
            if line.startswith("- "):
                line = line[2:].strip()
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
        "severity": "minor",
        "description": ""
    }
    
    if not os.path.exists(fpath):
        return metadata
        
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if '\\n' in content and '\n' not in content:
        content = content.replace('\\n', '\n')
        
    url_match = re.search(r'\*\*Original URL:\*\*\s*(.*)', content)
    if url_match:
        metadata["url"] = url_match.group(1).strip()
        
    touches_match = re.search(r'\*\*Touches:\*\*\s*(.*)', content)
    if touches_match:
        metadata["touches"] = touches_match.group(1).strip()
        
    severity_match = re.search(r'\*\*Severity:\*\*\s*(.*)', content, re.IGNORECASE)
    if severity_match:
        metadata["severity"] = severity_match.group(1).strip().lower()
 
    # Try to extract the first paragraph or description
    desc_match = re.search(r'\*\*Что это такое:\*\*\s*(.*)', content)
    if desc_match:
        metadata["description"] = desc_match.group(1).strip()
        
    return metadata

def get_severity_style(severity):
    if severity == "breaking/security":
        return "background-color: #ef4444; color: #ffffff;" # Red
    elif severity == "performance":
        return "background-color: #f59e0b; color: #ffffff;" # Yellow
    elif severity == "integration":
        return "background-color: #3b82f6; color: #ffffff;" # Blue
    else:
        return "background-color: #64748b; color: #ffffff;" # Grey/Slate

def format_findings_to_html(findings_list, research_dir):
    layers = {1: [], 2: [], 3: [], 4: []}
    minor_items = []
    
    for slug, title in findings_list:
        meta = lookup_metadata(research_dir, slug)
        
        severity_badge = f'<span style="padding: 2px 6px; font-size: 11px; font-weight: bold; border-radius: 4px; margin-right: 8px; {get_severity_style(meta["severity"])}">{meta["severity"].upper()}</span>'
        
        touches_pills = ""
        if meta["touches"]:
            pills = [f'<span style="background-color: #334155; color: #94a3b8; padding: 2px 6px; font-size: 11px; border-radius: 4px; margin-right: 4px;">{t.strip()}</span>' for t in meta["touches"].split(',')]
            touches_pills = "".join(pills)
            
        source_link = ""
        if meta["url"]:
            source_link = f'<a href="{meta["url"]}" style="color: #38bdf8; text-decoration: none; font-size: 13px; font-weight: 500; margin-left: 8px;">Источник &rarr;</a>'
            
        desc_text = ""
        if meta["description"]:
            desc_text = f'<div style="color: #94a3b8; font-size: 13px; margin-top: 6px; line-height: 1.5;">{html_escape(meta["description"])}</div>'

        item_html = f"""
        <div style="background-color: #1e293b; border-radius: 8px; padding: 12px; margin-bottom: 12px; border-left: 4px solid #38bdf8;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
                <div style="font-size: 15px; font-weight: 600; color: #f8fafc; margin-bottom: 4px;">
                    {severity_badge}{html_escape(title)}
                </div>
            </div>
            <div style="margin-top: 6px;">
                {touches_pills}{source_link}
            </div>
            {desc_text}
        </div>
        """
        
        if meta["severity"] == "minor":
            minor_items.append(f"""
            <li style="margin-bottom: 6px; color: #cbd5e1; font-size: 13px;">
                <strong>{html_escape(title)}</strong> ({html_escape(meta["touches"])})
                {f'- <a href="{meta["url"]}" style="color: #38bdf8; text-decoration: none;">Источник</a>' if meta["url"] else ''}
            </li>
            """)
            continue
            
        layer_id = get_component_layer(meta["touches"])
        layers[layer_id].append(item_html)
        
    output = []
    
    layer_headers = {
        1: "🤖 AI Agents & LLMs",
        2: "💻 Local Dev Environment",
        3: "🗄️ System Memory & CLI",
        4: "📦 Other Components"
    }
    
    for l_id in [1, 2, 3, 4]:
        if layers[l_id]:
            output.append(f'<h3 style="color: #38bdf8; font-size: 16px; border-bottom: 1px solid #334155; padding-bottom: 4px; margin-top: 20px; margin-bottom: 10px;">{layer_headers[l_id]}</h3>')
            output.extend(layers[l_id])
            
    if minor_items:
        output.append('<h3 style="color: #94a3b8; font-size: 15px; border-bottom: 1px solid #334155; padding-bottom: 4px; margin-top: 20px; margin-bottom: 10px;">Мелкие обновления (Minor)</h3>')
        output.append('<ul style="padding-left: 20px; margin-top: 8px;">' + "".join(minor_items) + '</ul>')
        
    return "\n".join(output)

def build_html_email(summary_file, research_dir, date_str):
    stats = ""
    daily_dir = os.path.dirname(summary_file)
    log_additions_file = os.path.join(daily_dir, "log-additions.md")
    
    if os.path.exists(log_additions_file):
        do_now_count = 0
        experiment_count = 0
        parking_count = 0
        with open(log_additions_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line.startswith("|"):
                    continue
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) < 2:
                    continue
                verdict = parts[1].lower()
                if verdict == "do now":
                    do_now_count += 1
                elif verdict == "experiment":
                    experiment_count += 1
                elif verdict in ["parking", "parking lot"]:
                    parking_count += 1
        stats_parts = []
        if do_now_count > 0:
            stats_parts.append(f"do-now {do_now_count}")
        if experiment_count > 0:
            stats_parts.append(f"experiment {experiment_count}")
        if parking_count > 0:
            stats_parts.append(f"parking {parking_count}")
        stats = ", ".join(stats_parts)
    elif os.path.exists(summary_file):
        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'\*\*By verdict:\*\*\s*(.*)', content, re.IGNORECASE)
            if match:
                stats = match.group(1).strip()
                
    # Style statistics as badges
    stats_html = ""
    if stats:
        parts = stats.split(',')
        p_html = []
        for p in parts:
            p = p.strip()
            if 'do-now' in p:
                val = p.split()[-1]
                p_html.append(f'<span style="background-color: #ef4444; color: #ffffff; padding: 3px 8px; font-size: 12px; border-radius: 12px; font-weight: bold; margin-right: 6px;">Do Now: {val}</span>')
            elif 'experiment' in p:
                val = p.split()[-1]
                p_html.append(f'<span style="background-color: #f59e0b; color: #ffffff; padding: 3px 8px; font-size: 12px; border-radius: 12px; font-weight: bold; margin-right: 6px;">Experiment: {val}</span>')
            elif 'parking' in p:
                val = p.split()[-1]
                p_html.append(f'<span style="background-color: #64748b; color: #ffffff; padding: 3px 8px; font-size: 12px; border-radius: 12px; font-weight: bold; margin-right: 6px;">Parking: {val}</span>')
        stats_html = "".join(p_html)

    body_html = []
    
    sections = [
        ("Do now (high confidence)", "Внедрить сейчас (Do now)"),
        ("Experiment", "Эксперименты (Experiment)"),
        ("Parking", "Отложено (Parking)")
    ]
    
    has_keeps = False
    for sec_header, display_name in sections:
        sec_findings = parse_summary_findings(summary_file, sec_header)
        if sec_findings:
            formatted = format_findings_to_html(sec_findings, research_dir)
            if formatted:
                body_html.append(f'<h2 style="color: #ffffff; font-size: 18px; margin-top: 24px; margin-bottom: 8px; border-bottom: 2px solid #38bdf8; padding-bottom: 4px;">{display_name}</h2>')
                body_html.append(formatted)
                has_keeps = True
                
    if not has_keeps:
        body_html.append('<div style="text-align: center; color: #94a3b8; padding: 20px; font-style: italic;">Сегодня никаких обновлений не зафиксировано. Пайплайн пуст.</div>')

    full_body = "\n".join(body_html)

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Stack Watch — {date_str}</title>
    </head>
    <body style="background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; color: #f8fafc;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #0f172a; border-radius: 12px; border: 1px solid #1e293b; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);">
            <tr>
                <td style="padding: 24px; background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%); border-bottom: 1px solid #1e293b;">
                    <table width="100%">
                        <tr>
                            <td>
                                <h1 style="margin: 0; font-size: 24px; font-weight: 800; letter-spacing: -0.5px; color: #ffffff;">Stack Watch</h1>
                                <div style="color: #38bdf8; font-size: 14px; font-weight: bold; margin-top: 4px;">Сводка обновлений за {date_str}</div>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding-top: 12px;">
                                {stats_html}
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td style="padding: 24px; background-color: #0f172a;">
                    {full_body}
                </td>
            </tr>
            <tr>
                <td style="padding: 16px 24px; background-color: #0b0f19; border-top: 1px solid #1e293b; text-align: center; font-size: 12px; color: #475569;">
                    Репозиторий проекта: <a href="https://github.com/arseny-mp/stack-watch" style="color: #38bdf8; text-decoration: none;">arseny-mp/stack-watch</a><br>
                    Этот дайджест сформирован автоматически облачным пайплайном Stack Watch.
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html_template

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
        
    logging.info(f"Email delivery run starting for date: {date_str}")
    
    processed_dir = os.path.join(WORKSPACE_DIR, "processed")
    daily_drop_dir = os.path.join(WORKSPACE_DIR, date_str)
    state_file = os.path.join(processed_dir, "email-last-sent.txt")
    
    # Resolve file paths
    if args.weekly_rollup:
        summary_file = args.weekly_rollup
        research_dir = os.path.join(processed_dir, date_str, "external-research")
    else:
        processed_daily_dir = os.path.join(processed_dir, date_str)
        if os.path.exists(processed_daily_dir):
            summary_file = os.path.join(processed_daily_dir, "summary.md")
            research_dir = os.path.join(processed_daily_dir, "external-research")
        else:
            summary_file = os.path.join(daily_drop_dir, "summary.md")
            research_dir = os.path.join(daily_drop_dir, "external-research")
            
    # Guard against double delivery
    if not args.force and not args.dry_run:
        if check_already_sent(state_file, date_str):
            logging.info(f"Already sent email updates for {date_str}. Use --force to override. Exiting.")
            sys.exit(0)
            
    if not os.path.exists(summary_file):
        logging.warning(f"Summary file not found: {summary_file}. Nothing to send.")
        sys.exit(0)
        
    html_content = build_html_email(summary_file, research_dir, date_str)
    
    if args.dry_run:
        logging.info("===== DRY RUN EMAIL =====")
        # Print HTML preview snippet
        print(html_content[:1000] + "\n...[TRUNCATED IN PREVIEW]...")
        logging.info("===== END DRY RUN EMAIL =====")
        sys.exit(0)
        
    # Retrieve SMTP credentials
    smtp_server = os.environ.get("EMAIL_SMTP_SERVER", "smtp.gmail.com")
    try:
        smtp_port = int(os.environ.get("EMAIL_SMTP_PORT", "587"))
    except ValueError:
        smtp_port = 587
        
    sender_email = os.environ.get("EMAIL_SENDER", "admin@myprtech.org")
    email_password = os.environ.get("EMAIL_SMTP_PASSWORD")
    recipients_str = os.environ.get("EMAIL_RECIPIENTS", "admin@myprtech.org")
    
    if not email_password:
        logging.error("EMAIL_SMTP_PASSWORD environment variable is missing. Cannot send email.")
        sys.exit(1)
        
    recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]
    if not recipients:
        logging.error("No email recipients specified in EMAIL_RECIPIENTS.")
        sys.exit(1)
        
    # Construct email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Stack Watch — {date_str}"
    msg['From'] = f"Stack Watch Curation <{sender_email}>"
    msg['To'] = ", ".join(recipients)
    
    # Text fallback
    text_fallback = f"Сводка обновлений Stack Watch за {date_str}. Пожалуйста, откройте это письмо в почтовом клиенте с поддержкой HTML."
    msg.attach(MIMEText(text_fallback, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    # Connect and Send
    try:
        logging.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        logging.info(f"Logging in as {sender_email}...")
        server.login(sender_email, email_password)
        logging.info(f"Sending email to {recipients}...")
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        logging.info("Email delivered successfully!")
        
        # Mark as sent
        mark_as_sent(state_file, date_str)
    except Exception as e:
        logging.error(f"Failed to deliver email: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
