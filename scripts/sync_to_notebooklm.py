#!/usr/bin/env python3
import os
import sys
import argparse
import logging
from datetime import datetime
from notebooklm_client import NotebookLMClient

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
LOG_FILE = os.path.join(WORKSPACE_DIR, "sync_notebooklm.log")

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] Sync-NotebookLM: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

def parse_args():
    parser = argparse.ArgumentParser(description="Sync daily findings to NotebookLM master KB.")
    parser.add_argument("--date", help="Date folder to sync (default: today's date)")
    return parser.parse_args()

def extract_metadata(filepath):
    # Extracts title and touches from findings markdown
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title = "Untitled"
    # Find first header: # Title
    for line in content.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
            
    return title, content

def main():
    args = parse_args()
    date_str = args.date or datetime.now().strftime('%Y-%m-%d')
    daily_dir = os.path.join(WORKSPACE_DIR, date_str)
    
    if not os.path.exists(daily_dir):
        logging.error(f"Daily directory {daily_dir} not found. Nothing to sync.")
        sys.exit(1)
        
    research_dir = os.path.join(daily_dir, "external-research")
    summary_file = os.path.join(daily_dir, "summary.md")
    
    # Initialize client
    client = NotebookLMClient()
    try:
        client.connect()
        notebook_id = client.find_or_create_notebook("Stack Watch Knowledge Base")
        logging.info(f"Using Knowledge Base notebook ID: {notebook_id}")
        
        # Get existing sources to avoid duplicates
        existing_sources_res = client.call_tool("source_list", {"notebook_id": notebook_id})
        existing_titles = set()
        for part in existing_sources_res.get("content", []):
            if part.get("type") == "text":
                text = part.get("text", "")
                # Parse title from lists (typically in text format)
                # Let's search for titles. In the list, it output items.
                # Since we don't know the exact format of source_list output, let's also search for slug/filename substrings
                existing_titles.add(text.lower())
                
        # 1. Sync Summary.md
        if os.path.exists(summary_file):
            summary_title = f"Summary - {date_str}"
            # Check if summary already exists
            is_dupe = False
            for t in existing_titles:
                if summary_title.lower() in t or date_str in t:
                    is_dupe = True
                    break
            
            if not is_dupe:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary_content = f.read()
                logging.info(f"Syncing summary: {summary_title}")
                client.add_text(notebook_id, summary_title, summary_content)
            else:
                logging.info(f"Summary for {date_str} already synced. Skipping.")
                
        # 2. Sync Findings in external-research/
        if os.path.exists(research_dir):
            for filename in os.listdir(research_dir):
                if filename.endswith(".md"):
                    filepath = os.path.join(research_dir, filename)
                    title, content = extract_metadata(filepath)
                    slug = filename[:-3]
                    
                    is_dupe = False
                    # Check if either title or slug appears in the existing sources
                    for t in existing_titles:
                        if title.lower() in t or slug.lower() in t:
                            is_dupe = True
                            break
                            
                    if not is_dupe:
                        logging.info(f"Syncing finding: {title} ({slug})")
                        client.add_text(notebook_id, f"{title} ({slug})", content)
                    else:
                        logging.info(f"Finding {slug} already synced. Skipping.")
                        
        logging.info("Sync process completed successfully.")
    except Exception as e:
        logging.error(f"Error during NotebookLM sync: {e}")
        sys.exit(1)
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
