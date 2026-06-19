#!/usr/bin/env python3
import os
import re
import sys
import glob
import logging
import argparse
import subprocess
from datetime import datetime

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
LOG_FILE = os.path.join(WORKSPACE_DIR, "bridge-antigravity-research.log")

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] Weekly-Rollup: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

def parse_args():
    parser = argparse.ArgumentParser(description="Compile Stack Watch weekly rollup.")
    parser.add_argument("--date", help="Date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--dry-run", action="store_true", help="Compile and print without writing or delivering")
    return parser.parse_args()

def parse_daily_summary_sections(filepath):
    if not os.path.exists(filepath):
        return "", ""
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.split('\n')
    current_section = None
    sections = {
        "do_now": [],
        "experiment": []
    }
    
    has_subheadings = {
        "do_now": False,
        "experiment": False
    }
    
    current_finding = None
    
    # First pass: look for ### headings
    for line in lines:
        line_strip = line.strip()
        if line_strip.startswith("## "):
            header = line_strip[3:].lower()
            if "do now" in header or "немедленных действий" in header:
                current_section = "do_now"
            elif "experiment" in header or "эксперименты" in header:
                current_section = "experiment"
            else:
                current_section = None
            current_finding = None
            
        elif current_section and line_strip.startswith("### "):
            has_subheadings[current_section] = True
            title = re.sub(r'^\d+\.\s*', '', line_strip[4:]).strip()
            current_finding = {
                "title": title,
                "action_plan": ""
            }
            sections[current_section].append(current_finding)
            
        elif current_finding and (line_strip.startswith("- Если do-now") or line_strip.startswith("- Если experiment") or line_strip.startswith("- Если do-now или experiment:")):
            plan = line_strip.split(":", 1)[1].strip()
            current_finding["action_plan"] = plan

    # Second pass: if a section has no subheadings, parse it as old format bullet points
    current_section = None
    for line in lines:
        line_strip = line.strip()
        if line_strip.startswith("## "):
            header = line_strip[3:].lower()
            if "do now" in header or "немедленных действий" in header:
                current_section = "do_now"
            elif "experiment" in header or "эксперименты" in header:
                current_section = "experiment"
            else:
                current_section = None
                
        elif current_section and line_strip.startswith("- ") and not has_subheadings[current_section]:
            item_text = line_strip[2:].strip()
            if item_text and item_text != "(none)" and item_text != "_(none)_":
                sections[current_section].append({
                    "title": item_text,
                    "action_plan": ""
                })
                
    # Format the outputs
    do_now_lines = []
    for f in sections["do_now"]:
        if f["action_plan"]:
            do_now_lines.append(f"  • {f['title']} — {f['action_plan']}")
        else:
            do_now_lines.append(f"  • {f['title']}")
            
    exp_lines = []
    for f in sections["experiment"]:
        if f["action_plan"]:
            exp_lines.append(f"  • {f['title']} — {f['action_plan']}")
        else:
            exp_lines.append(f"  • {f['title']}")
            
    return "\n".join(do_now_lines), "\n".join(exp_lines)

def main():
    args = parse_args()
    
    date_str = args.date
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
        
    logging.info(f"Weekly rollup compilation starting for date: {date_str}")
    
    # Resolve paths
    summary_dir = os.path.join(WORKSPACE_DIR, "project-status", "_summary")
    rollup_file = os.path.join(WORKSPACE_DIR, "processed", "weekly_rollup.txt")
    
    # Find last 7 daily summaries
    pattern = os.path.join(summary_dir, "*-stack-watch.*")
    summary_files = sorted(glob.glob(pattern))
    last_7_files = summary_files[-7:] if len(summary_files) >= 7 else summary_files
    
    if not last_7_files:
        logging.warning("No daily summary files found. Cannot compile rollup.")
        sys.exit(0)
        
    logging.info(f"Found {len(last_7_files)} daily summaries to process.")
    
    rollup_lines = []
    rollup_lines.append("📅 <b>Stack Watch — Итоги недели (Weekly Rollup)</b>")
    rollup_lines.append("Период: за последние 7 дней")
    rollup_lines.append("")
    
    has_any_updates = False
    
    for fpath in last_7_files:
        fname = os.path.basename(fpath)
        # Extract date YYYY-MM-DD
        fdate = fname.replace("-stack-watch.md", "")
        
        do_now, exp = parse_daily_summary_sections(fpath)
        
        if do_now or exp:
            rollup_lines.append(f"📅 <b>{fdate}:</b>")
            if do_now:
                rollup_lines.append("  <b>Do now:</b>")
                rollup_lines.append(do_now)
            if exp:
                rollup_lines.append("  <b>Experiment:</b>")
                rollup_lines.append(exp)
            rollup_lines.append("")
            has_any_updates = True
            
    if not has_any_updates:
        rollup_lines.append("<i>За прошедшую неделю обновлений не найдено.</i>")
        
    rollup_content = "\n".join(rollup_lines) + "\n"
    
    if args.dry_run:
        logging.info("===== DRY RUN WEEKLY ROLLUP =====")
        print(rollup_content)
        logging.info("===== END DRY RUN WEEKLY ROLLUP =====")
        sys.exit(0)
        
    # Write rollup file
    os.makedirs(os.path.dirname(rollup_file), exist_ok=True)
    with open(rollup_file, 'w', encoding='utf-8') as f:
        f.write(rollup_content)
        
    logging.info(f"Successfully compiled weekly rollup to {rollup_file}")
    
    # Deliver Telegram
    deliver_script = os.path.join(SCRIPT_DIR, "deliver.py")
    logging.info("Triggering Telegram delivery of weekly rollup...")
    try:
        res = subprocess.run(
            [sys.executable, deliver_script, "--weekly-rollup", rollup_file],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info("Telegram weekly delivery output:")
        logging.info(res.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to deliver weekly rollup to Telegram: {e}")
        logging.error(e.stderr)
        
    # Generate Audio Overview
    audio_script = os.path.join(SCRIPT_DIR, "generate_audio_overview.py")
    logging.info("Triggering NotebookLM weekly Audio Overview (podcast) generation...")
    try:
        res = subprocess.run(
            [sys.executable, audio_script],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info("Audio Overview generation output:")
        logging.info(res.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to generate weekly Audio Overview: {e}")
        logging.error(e.stderr)

if __name__ == "__main__":
    main()
