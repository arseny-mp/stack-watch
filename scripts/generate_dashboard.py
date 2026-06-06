#!/usr/bin/env python3
import os
import re
import json
import sys
from datetime import datetime

# --- Configuration ---
WORKSPACE_DIR = "/Users/user/Projects/Stack Watch"
PROCESSED_DIR = os.path.join(WORKSPACE_DIR, "processed")
OUTPUT_HTML = os.path.join(WORKSPACE_DIR, "index.html")
LEARNINGS_FILE = os.path.join(WORKSPACE_DIR, "learnings.md")
RUBRIC_FILE = os.path.join(WORKSPACE_DIR, "_rubric.md")

def parse_summary_file(file_path):
    if not os.path.exists(file_path):
        return None
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.split('\n')
    
    data = {
        "date": "",
        "sources": "",
        "candidates": 0,
        "new_findings": 0,
        "verdicts": {"do-now": 0, "experiment": 0, "parking": 0, "skip": 0},
        "validation_rate": "",
        "sections": {
            "do_now": [],
            "experiment": [],
            "parking": [],
            "unconfirmed": [],
            "skipped": []
        }
    }
    
    # Extract Title / Date
    title_match = re.search(r'#\s+Stack\s+Watch\s+—\s+(\d{4}-\d{2}-\d{2})', content)
    if title_match:
        data["date"] = title_match.group(1)
        
    # Parse metadata lines
    for line in lines:
        line_strip = line.strip()
        if line_strip.startswith("**Sources processed:**"):
            data["sources"] = line_strip.replace("**Sources processed:**", "").strip()
        elif line_strip.startswith("**Candidates considered (across all sources):**"):
            try:
                data["candidates"] = int(line_strip.replace("**Candidates considered (across all sources):**", "").strip())
            except ValueError:
                pass
        elif line_strip.startswith("**New findings:**"):
            try:
                data["new_findings"] = int(line_strip.replace("**New findings:**", "").strip())
            except ValueError:
                pass
        elif line_strip.startswith("**By verdict:**"):
            verdict_str = line_strip.replace("**By verdict:**", "").strip()
            # e.g., do-now 0, experiment 2, parking 2, skip 4
            parts = verdict_str.split(',')
            for p in parts:
                p = p.strip()
                match = re.match(r'([a-zA-Z\-]+)\s+(\d+)', p)
                if match:
                    key = match.group(1).lower()
                    # Map parking lot or other names to std keys
                    if "park" in key:
                        key = "parking"
                    elif "do" in key:
                        key = "do-now"
                    data["verdicts"][key] = int(match.group(2))
        elif line_strip.startswith("**Cross-Domain Validation rate:**"):
            data["validation_rate"] = line_strip.replace("**Cross-Domain Validation rate:**", "").strip()

    # Parse sections
    current_section = None
    section_mapping = {
        "do now (high confidence)": "do_now",
        "experiment": "experiment",
        "parking": "parking",
        "unconfirmed / single domain (low confidence)": "unconfirmed",
        "skipped": "skipped"
    }
    
    for line in lines:
        line_strip = line.strip()
        if line_strip.startswith("## "):
            section_name = line_strip.replace("## ", "").strip().lower()
            current_section = section_mapping.get(section_name)
        elif current_section and line_strip.startswith("- "):
            item_text = line_strip[2:].strip()
            if item_text and item_text != "(none)" and item_text != "_(none)_":
                data["sections"][current_section].append(item_text)
                
    return data

def parse_learnings(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by active rules section
    rules_sec = re.split(r'##\s+Active\s+Rules\s+&\s+Exclusions', content, flags=re.IGNORECASE)
    if len(rules_sec) < 2:
        return []
    
    content_rules = rules_sec[1]
    
    # Split rules by numbered lists (e.g. 1. **Title**)
    items = re.split(r'\n\s*\d+\.\s+\*\*', content_rules)
    rules = []
    
    for item in items[1:]:
        lines = item.split('\n')
        title_line = lines[0].strip()
        title = title_line.replace('**:', '').replace('**', '').strip()
        body = []
        for line in lines[1:]:
            line_str = line.strip()
            if line_str.startswith('* ') or line_str.startswith('- '):
                body.append(line_str[2:].strip())
            elif line_str:
                body.append(line_str)
        rules.append({
            "title": title,
            "rules": body
        })
    return rules

def parse_rubric(file_path):
    if not os.path.exists(file_path):
        return {"watchlist": [], "autoskip": []}
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    watchlist = []
    sections = [
        ("AI Execution Tools", r"\*\*AI execution tools\s*\(\d+\):\*\*([\s\S]*?)(?=\*\*(?:Input / output channels|Infra layer|Out of scope|3\.)|##)"),
        ("Input / Output Channels", r"\*\*Input / output channels\s*\(\d+\):\*\*([\s\S]*?)(?=\*\*(?:Infra layer|Out of scope|3\.)|##)"),
        ("Infra Layer", r"\*\*Infra layer\s*\(\d+\):\*\*([\s\S]*?)(?=\*\*(?:Out of scope|3\.)|##)")
    ]
    
    for sec_title, pattern in sections:
        match = re.search(pattern, content)
        if match:
            items_str = match.group(1)
            items = []
            for line in items_str.split('\n'):
                line = line.strip()
                item_match = re.match(r'^\d+\.\s+\*\*([^*]+)\*\*(?:\s+—\s+(.+)|(?:\s+\((.+)\))?\s*—?\s*(.*))', line)
                if item_match:
                    name = item_match.group(1).strip()
                    desc = (item_match.group(2) or item_match.group(4) or "").strip()
                    items.append({"name": name, "description": desc})
                elif line.startswith('- ') or line.startswith('* '):
                    items.append({"name": line[2:].strip(), "description": ""})
            if items:
                watchlist.append({"category": sec_title, "items": items})
                
    # Parse auto-skip rules
    autoskip = []
    skip_match = re.search(r'##\s*3\.\s+Out\s+of\s+scope\s+\(auto-skip\)([\s\S]*?)(?=##|\Z)', content, flags=re.IGNORECASE)
    if skip_match:
        items_str = skip_match.group(1)
        for line in items_str.split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                parts = line[2:].split('—')
                if len(parts) >= 2:
                    title = parts[0].replace('**', '').strip()
                    desc = '—'.join(parts[1:]).strip()
                    autoskip.append({"title": title, "description": desc})
                else:
                    autoskip.append({"title": line[2:].strip(), "description": ""})
                    
    return {"watchlist": watchlist, "autoskip": autoskip}

def main():
    print("Parsing Stack Watch processed daily summaries...")
    
    if not os.path.exists(PROCESSED_DIR):
        print(f"Processed directory not found: {PROCESSED_DIR}", file=sys.stderr)
        sys.exit(1)
        
    daily_runs = []
    
    # Scan processed dir
    for folder_name in sorted(os.listdir(PROCESSED_DIR), reverse=True):
        folder_path = os.path.join(PROCESSED_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue
            
        # Try to match date
        date_match = re.match(r'^(\d{4}-\d{2}-\d{2})', folder_name)
        if not date_match:
            continue
            
        date_str = date_match.group(1)
        summary_path = os.path.join(folder_path, "summary.md")
        
        if os.path.exists(summary_path):
            data = parse_summary_file(summary_path)
            if data:
                # Ensure date field matches
                data["date"] = date_str
                data["status"] = "success"
                daily_runs.append(data)
        else:
            # Empty day or skipped run
            daily_runs.append({
                "date": date_str,
                "status": "empty" if "empty" in folder_name else "unreliable",
                "sources": "N/A",
                "candidates": 0,
                "new_findings": 0,
                "verdicts": {"do-now": 0, "experiment": 0, "parking": 0, "skip": 0},
                "validation_rate": "0%",
                "sections": {"do_now": [], "experiment": [], "parking": [], "unconfirmed": [], "skipped": []}
            })
            
    # Sort by date descending
    daily_runs.sort(key=lambda x: x["date"], reverse=True)
    
    # Parse Learnings
    print("Parsing learnings.md...")
    learnings = parse_learnings(LEARNINGS_FILE)
    
    # Parse Rubrics
    print("Parsing _rubric.md...")
    rubrics = parse_rubric(RUBRIC_FILE)
    
    # Write to HTML template
    print(f"Compiling dashboard to {OUTPUT_HTML}...")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stack Watch — Premium Status Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #09090b;
            --bg-surface: #121215;
            --bg-card: #18181b;
            --border-color: #27272a;
            --border-hover: #3f3f46;
            --text-primary: #fafafa;
            --text-secondary: #a1a1aa;
            --text-muted: #71717a;
            
            /* Neon Glows & Accents */
            --color-indigo: #6366f1;
            --color-indigo-glow: rgba(99, 102, 241, 0.15);
            --color-emerald: #10b981;
            --color-emerald-glow: rgba(16, 185, 129, 0.15);
            --color-violet: #8b5cf6;
            --color-violet-glow: rgba(139, 92, 246, 0.15);
            --color-amber: #f59e0b;
            --color-amber-glow: rgba(245, 158, 11, 0.15);
            --color-rose: #f43f5e;
            --color-rose-glow: rgba(244, 63, 94, 0.15);
            --color-cyan: #06b6d4;
            
            --radius-lg: 12px;
            --radius-md: 8px;
            --radius-sm: 4px;
            
            --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-base);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            overflow-x: hidden;
            display: flex;
            min-height: 100vh;
        }}

        /* Scrollbar styles */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: var(--bg-base);
        }}
        ::-webkit-scrollbar-thumb {{
            background: var(--border-color);
            border-radius: var(--radius-sm);
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--border-hover);
        }}

        /* App Container */
        .app-container {{
            display: flex;
            width: 100%;
            height: 100vh;
            overflow: hidden;
        }}

        /* Sidebar - Navigation of dates */
        .sidebar {{
            width: 320px;
            background-color: var(--bg-surface);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
            height: 100%;
        }}

        .sidebar-header {{
            padding: 24px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .sidebar-header h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #fff 30%, var(--text-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .sidebar-header .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--color-emerald);
            box-shadow: 0 0 12px var(--color-emerald);
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }}
            70% {{ box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
        }}

        .sidebar-menu {{
            display: flex;
            padding: 12px 24px 0 24px;
            gap: 8px;
            border-bottom: 1px solid var(--border-color);
        }}

        .menu-tab {{
            padding: 8px 12px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            color: var(--text-secondary);
            border-bottom: 2px solid transparent;
            transition: var(--transition-smooth);
        }}

        .menu-tab.active {{
            color: var(--text-primary);
            border-bottom: 2px solid var(--color-indigo);
        }}

        .date-list {{
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .date-item {{
            padding: 14px 16px;
            border-radius: var(--radius-md);
            cursor: pointer;
            border: 1px solid transparent;
            background-color: transparent;
            transition: var(--transition-smooth);
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .date-item:hover {{
            background-color: rgba(255, 255, 255, 0.02);
            border-color: var(--border-color);
        }}

        .date-item.active {{
            background-color: rgba(99, 102, 241, 0.08);
            border-color: rgba(99, 102, 241, 0.3);
        }}

        .date-item-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .date-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 15px;
            font-weight: 600;
            color: var(--text-primary);
        }}

        .date-badge {{
            font-size: 11px;
            padding: 2px 6px;
            border-radius: 10px;
            font-weight: 600;
        }}

        .date-badge.success {{
            background-color: var(--color-emerald-glow);
            color: var(--color-emerald);
        }}

        .date-badge.empty {{
            background-color: var(--border-color);
            color: var(--text-muted);
        }}

        .date-badge.unreliable {{
            background-color: var(--color-rose-glow);
            color: var(--color-rose);
        }}

        .date-item-stats {{
            display: flex;
            gap: 8px;
            font-size: 12px;
            color: var(--text-secondary);
        }}

        /* Main Content Panel */
        .main-panel {{
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
            overflow-y: auto;
            padding: 32px 40px;
            background-image: radial-gradient(circle at 80% 10%, rgba(99, 102, 241, 0.04) 0%, transparent 60%);
        }}

        /* Navigation Header */
        .main-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 28px;
        }}

        .main-title-section h2 {{
            font-family: 'Outfit', sans-serif;
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -0.03em;
        }}

        .main-title-section p {{
            color: var(--text-secondary);
            font-size: 14px;
            margin-top: 4px;
        }}

        /* Hero Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }}

        .stats-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            position: relative;
            overflow: hidden;
            transition: var(--transition-smooth);
        }}

        .stats-card::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background-color: transparent;
        }}

        .stats-card.indigo::after {{ background-color: var(--color-indigo); }}
        .stats-card.emerald::after {{ background-color: var(--color-emerald); }}
        .stats-card.amber::after {{ background-color: var(--color-amber); }}
        .stats-card.rose::after {{ background-color: var(--color-rose); }}

        .stats-card:hover {{
            transform: translateY(-2px);
            border-color: var(--border-hover);
        }}

        .stats-label {{
            font-size: 12px;
            font-weight: 500;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .stats-value {{
            font-family: 'Outfit', sans-serif;
            font-size: 28px;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .stats-desc {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        /* Filter Controls & Search */
        .controls-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            margin-bottom: 24px;
        }}

        .filter-tabs {{
            display: flex;
            gap: 8px;
            background-color: var(--bg-surface);
            padding: 4px;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-color);
        }}

        .filter-tab {{
            padding: 6px 14px;
            font-size: 13px;
            font-weight: 500;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            border-radius: calc(var(--radius-md) - 2px);
            cursor: pointer;
            transition: var(--transition-smooth);
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .filter-tab:hover {{
            color: var(--text-primary);
        }}

        .filter-tab.active {{
            background-color: var(--bg-card);
            color: var(--text-primary);
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
            border: 1px solid var(--border-color);
        }}

        .filter-badge {{
            font-size: 11px;
            padding: 1px 5px;
            border-radius: 8px;
            background-color: var(--border-color);
            color: var(--text-secondary);
        }}

        .search-container {{
            position: relative;
            width: 300px;
        }}

        .search-input {{
            width: 100%;
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            border-radius: var(--radius-md);
            padding: 8px 16px 8px 36px;
            font-size: 14px;
            transition: var(--transition-smooth);
        }}

        .search-input:focus {{
            outline: none;
            border-color: var(--color-indigo);
            box-shadow: 0 0 0 2px var(--color-indigo-glow);
        }}

        .search-icon {{
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            pointer-events: none;
        }}

        /* Findings Cards Layout */
        .findings-list {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .finding-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            transition: var(--transition-smooth);
            animation: fadeIn 0.4s ease-out;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .finding-card:hover {{
            border-color: var(--border-hover);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        }}

        .finding-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
        }}

        .finding-title-section {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .finding-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
        }}

        .finding-meta {{
            display: flex;
            gap: 12px;
            font-size: 12px;
            color: var(--text-secondary);
        }}

        .finding-badge {{
            font-size: 11px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 12px;
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }}

        .finding-badge.do_now {{
            background-color: var(--color-emerald-glow);
            color: var(--color-emerald);
            border: 1px solid rgba(16, 185, 129, 0.2);
        }}

        .finding-badge.experiment {{
            background-color: var(--color-violet-glow);
            color: var(--color-violet);
            border: 1px solid rgba(139, 92, 246, 0.2);
        }}

        .finding-badge.parking {{
            background-color: var(--color-amber-glow);
            color: var(--color-amber);
            border: 1px solid rgba(245, 158, 11, 0.2);
        }}

        .finding-badge.unconfirmed {{
            background-color: rgba(6, 182, 212, 0.1);
            color: var(--color-cyan);
            border: 1px solid rgba(6, 182, 212, 0.2);
        }}

        .finding-badge.skipped {{
            background-color: rgba(255, 255, 255, 0.05);
            color: var(--text-muted);
            border: 1px solid var(--border-color);
        }}

        .finding-body {{
            font-size: 14px;
            line-height: 1.6;
            color: var(--text-secondary);
        }}

        .finding-body strong {{
            color: var(--text-primary);
            font-weight: 500;
        }}

        .finding-link {{
            color: var(--color-indigo);
            text-decoration: none;
            font-weight: 500;
            transition: var(--transition-smooth);
        }}

        .finding-link:hover {{
            text-decoration: underline;
            color: #818cf8;
        }}

        /* Empty State */
        .empty-state {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 80px 40px;
            border: 2px dashed var(--border-color);
            border-radius: var(--radius-lg);
            text-align: center;
            color: var(--text-secondary);
            gap: 16px;
        }}

        .empty-state h3 {{
            font-family: 'Outfit', sans-serif;
            font-size: 20px;
            font-weight: 600;
            color: var(--text-primary);
        }}

        .empty-state p {{
            max-width: 400px;
            font-size: 14px;
            color: var(--text-muted);
        }}

        /* Rules View Details */
        .rules-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
        }}

        .rule-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            transition: var(--transition-smooth);
        }}

        .rule-card:hover {{
            border-color: var(--border-hover);
        }}

        .rule-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 18px;
            font-weight: 600;
            color: var(--color-indigo);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
        }}

        .rule-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .rule-list li {{
            font-size: 14px;
            line-height: 1.5;
            color: var(--text-secondary);
            position: relative;
            padding-left: 20px;
        }}

        .rule-list li::before {{
            content: '✦';
            position: absolute;
            left: 0;
            color: var(--color-indigo);
        }}

        /* Watch List & Rubrics styles */
        .rubric-sec-header {{
            font-family: 'Outfit', sans-serif;
            font-size: 22px;
            font-weight: 700;
            margin: 32px 0 16px 0;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .rubric-sec-header::after {{
            content: '';
            flex: 1;
            height: 1px;
            background-color: var(--border-color);
        }}

        .watchlist-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 16px;
        }}

        .watchlist-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            transition: var(--transition-smooth);
        }}

        .watchlist-card:hover {{
            border-color: var(--border-hover);
            transform: translateY(-1px);
        }}

        .watchlist-name {{
            font-family: 'Outfit', sans-serif;
            font-size: 15px;
            font-weight: 600;
            color: var(--text-primary);
        }}

        .watchlist-desc {{
            font-size: 12px;
            color: var(--text-muted);
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="status-dot"></div>
                <h1>STACK WATCH</h1>
            </div>
            <div class="sidebar-menu">
                <div class="menu-tab active" onclick="switchMainTab('digests')">Digests</div>
                <div class="menu-tab" onclick="switchMainTab('learnings')">Learnings</div>
                <div class="menu-tab" onclick="switchMainTab('rubric')">Rubric</div>
            </div>
            <div class="date-list" id="date-list-container">
                <!-- Date items injected here -->
            </div>
        </aside>

        <!-- Main Panel -->
        <main class="main-panel" id="main-panel-content">
            <!-- Dynamic Content Injected Here -->
        </main>
    </div>

    <!-- Inject data directly -->
    <script>
        const STACK_WATCH_DATA = {json.dumps(daily_runs)};
        const LEARNINGS_DATA = {json.dumps(learnings)};
        const RUBRIC_DATA = {json.dumps(rubrics)};

        let currentActiveTab = 'digests';
        let currentSelectedDateIndex = 0;
        let currentFindingFilter = 'all';
        let searchQuery = '';

        // Helper to format Date
        function formatDateReadable(dateStr) {{
            const options = {{ year: 'numeric', month: 'long', day: 'numeric' }};
            return new Date(dateStr).toLocaleDateString('en-US', options);
        }}

        // Helper to render markdown bold & links
        function parseMarkdown(text) {{
            if (!text) return '';
            return text
                .replace(/\\*\\*([^\\*]+)\\*\\*/g, '<strong>$1</strong>')
                .replace(/`([^`]+)`/g, '<code>$1</code>')
                .replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" target="_blank" class="finding-link">$1</a>');
        }}

        function switchMainTab(tab) {{
            currentActiveTab = tab;
            document.querySelectorAll('.menu-tab').forEach((el, idx) => {{
                el.classList.toggle('active', el.textContent.toLowerCase().includes(tab.slice(0,4)));
            }});
            renderMainContent();
        }}

        function selectDate(index) {{
            currentSelectedDateIndex = index;
            currentFindingFilter = 'all';
            searchQuery = '';
            
            // Update active states in sidebar
            document.querySelectorAll('.date-item').forEach((el, idx) => {{
                el.classList.toggle('active', idx === index);
            }});
            
            renderMainContent();
        }}

        function setFindingFilter(filter) {{
            currentFindingFilter = filter;
            document.querySelectorAll('.filter-tab').forEach(el => {{
                el.classList.toggle('active', el.dataset.filter === filter);
            }});
            renderFindingsList();
        }}

        function handleSearch(val) {{
            searchQuery = val.toLowerCase();
            renderFindingsList();
        }}

        // Render Sidebar Dates List
        function renderSidebar() {{
            const container = document.getElementById('date-list-container');
            container.innerHTML = '';
            
            if (currentActiveTab !== 'digests') {{
                container.innerHTML = `<div style="padding: 16px; color: var(--text-muted); font-size: 13px; text-align: center;">Click on the top tabs to view static system configuration or operator corrections.</div>`;
                return;
            }}
            
            STACK_WATCH_DATA.forEach((run, index) => {{
                const item = document.createElement('div');
                item.className = `date-item ${{index === currentSelectedDateIndex ? 'active' : ''}}`;
                item.onclick = () => selectDate(index);
                
                let badgeClass = 'success';
                let badgeText = 'SUCCESS';
                if (run.status === 'empty') {{
                    badgeClass = 'empty';
                    badgeText = 'EMPTY';
                }} else if (run.status === 'unreliable') {{
                    badgeClass = 'unreliable';
                    badgeText = 'UNRELIABLE';
                }}
                
                item.innerHTML = `
                    <div class="date-item-header">
                        <span class="date-title">${{run.date}}</span>
                        <span class="date-badge ${{badgeClass}}">${{badgeText}}</span>
                    </div>
                    <div class="date-item-stats">
                        <span>🔍 ${{run.candidates}} candidates</span>
                        <span>💎 ${{run.new_findings}} findings</span>
                    </div>
                `;
                container.appendChild(item);
            }});
        }}

        // Render Findings List under Digests tab
        function renderFindingsList() {{
            const run = STACK_WATCH_DATA[currentSelectedDateIndex];
            const listContainer = document.getElementById('findings-list-container');
            if (!listContainer) return;
            
            listContainer.innerHTML = '';
            
            if (run.status !== 'success') {{
                listContainer.innerHTML = `
                    <div class="empty-state">
                        <h3>No findings to show</h3>
                        <p>This run is marked as ${{run.status.toUpperCase()}} (no news findings were processed or the run encountered validation errors).</p>
                    </div>
                `;
                return;
            }}
            
            // Gather all items with their verdict type
            let allFindings = [];
            
            Object.keys(run.sections).forEach(sectionKey => {{
                run.sections[sectionKey].forEach(itemText => {{
                    allFindings.push({{
                        verdict: sectionKey,
                        text: itemText
                    }});
                }});
            }});
            
            // Filter findings by tab & search query
            let filtered = allFindings;
            if (currentFindingFilter !== 'all') {{
                filtered = filtered.filter(f => f.verdict === currentFindingFilter);
            }}
            if (searchQuery) {{
                filtered = filtered.filter(f => f.text.toLowerCase().includes(searchQuery));
            }}
            
            if (filtered.length === 0) {{
                listContainer.innerHTML = `
                    <div class="empty-state">
                        <h3>No matching findings found</h3>
                        <p>Try clearing your search query or choosing a different filter tab.</p>
                    </div>
                `;
                return;
            }}
            
            filtered.forEach(f => {{
                const card = document.createElement('div');
                card.className = 'finding-card';
                
                // Parse slug/title out of finding text if it contains e.g. "chatgpt-dreaming-v3-memory — Audit ChatGPT..."
                let title = f.text;
                let desc = '';
                const parts = f.text.split(' — ');
                if (parts.length >= 2) {{
                    title = parts[0];
                    desc = parts.slice(1).join(' — ');
                }}
                
                let badgeLabel = f.verdict.replace('_', ' ');
                if (badgeLabel === 'do now') badgeLabel = 'do now';
                
                card.innerHTML = `
                    <div class="finding-header">
                        <div class="finding-title-section">
                            <span class="finding-title">${{parseMarkdown(title)}}</span>
                        </div>
                        <span class="finding-badge ${{f.verdict}}">${{badgeLabel}}</span>
                    </div>
                    ${{desc ? `<div class="finding-body">${{parseMarkdown(desc)}}</div>` : ''}}
                `;
                listContainer.appendChild(card);
            }});
        }}

        // Render main content based on tab selection
        function renderMainContent() {{
            const mainPanel = document.getElementById('main-panel-content');
            renderSidebar();
            
            if (currentActiveTab === 'digests') {{
                const run = STACK_WATCH_DATA[currentSelectedDateIndex];
                if (!run) {{
                    mainPanel.innerHTML = '<div class="empty-state"><h3>No digests available</h3></div>';
                    return;
                }}
                
                // Count filters sizes
                const doNowCount = run.sections.do_now.length;
                const expCount = run.sections.experiment.length;
                const parkCount = run.sections.parking.length;
                const skipCount = run.sections.skipped.length;
                const unconfirmedCount = run.sections.unconfirmed.length;
                const totalCount = doNowCount + expCount + parkCount + skipCount + unconfirmedCount;
                
                mainPanel.innerHTML = `
                    <div class="main-header">
                        <div class="main-title-section">
                            <h2>Digest for ${{formatDateReadable(run.date)}}</h2>
                            <p>Processed from: <strong>${{run.sources}}</strong></p>
                        </div>
                    </div>
                    
                    <div class="stats-grid">
                        <div class="stats-card indigo">
                            <span class="stats-label">Candidates Considered</span>
                            <span class="stats-value">${{run.candidates}}</span>
                            <span class="stats-desc">Total raw signals ingested</span>
                        </div>
                        <div class="stats-card emerald">
                            <span class="stats-label">New Actionable Findings</span>
                            <span class="stats-value">${{run.new_findings}}</span>
                            <span class="stats-desc">Do-Now & Experiment items</span>
                        </div>
                        <div class="stats-card amber">
                            <span class="stats-label">Validation Rate</span>
                            <span class="stats-value">${{run.validation_rate.split(' ')[0]}}</span>
                            <span class="stats-desc">Verified across domains</span>
                        </div>
                    </div>
                    
                    <div class="controls-row">
                        <div class="filter-tabs">
                            <button class="filter-tab ${{currentFindingFilter === 'all' ? 'active' : ''}}" data-filter="all" onclick="setFindingFilter('all')">
                                All <span class="filter-badge">${{totalCount}}</span>
                            </button>
                            <button class="filter-tab ${{currentFindingFilter === 'do_now' ? 'active' : ''}}" data-filter="do_now" onclick="setFindingFilter('do_now')">
                                Do Now <span class="filter-badge">${{doNowCount}}</span>
                            </button>
                            <button class="filter-tab ${{currentFindingFilter === 'experiment' ? 'active' : ''}}" data-filter="experiment" onclick="setFindingFilter('experiment')">
                                Experiment <span class="filter-badge">${{expCount}}</span>
                            </button>
                            <button class="filter-tab ${{currentFindingFilter === 'parking' ? 'active' : ''}}" data-filter="parking" onclick="setFindingFilter('parking')">
                                Parking <span class="filter-badge">${{parkCount}}</span>
                            </button>
                            <button class="filter-tab ${{currentFindingFilter === 'skipped' ? 'active' : ''}}" data-filter="skipped" onclick="setFindingFilter('skipped')">
                                Skipped <span class="filter-badge">${{skipCount}}</span>
                            </button>
                        </div>
                        
                        <div class="search-container">
                            <span class="search-icon">🔍</span>
                            <input type="text" class="search-input" placeholder="Search this digest..." oninput="handleSearch(this.value)" value="${{searchQuery}}">
                        </div>
                    </div>
                    
                    <div class="findings-list" id="findings-list-container">
                        <!-- Findings list injected here -->
                    </div>
                `;
                renderFindingsList();
                
            }} else if (currentActiveTab === 'learnings') {{
                // Render learnings.md content
                let rulesHTML = '';
                if (LEARNINGS_DATA.length === 0) {{
                    rulesHTML = '<div class="empty-state"><h3>No active rules recorded</h3><p>Guidelines are updated automatically when feedback loops occur.</p></div>';
                }} else {{
                    LEARNINGS_DATA.forEach(rule => {{
                        let ruleListHTML = '';
                        rule.rules.forEach(r => {{
                            ruleListHTML += `<li>${{parseMarkdown(r)}}</li>`;
                        }});
                        
                        rulesHTML += `
                            <div class="rule-card">
                                <h4 class="rule-title">${{rule.title}}</h4>
                                <ul class="rule-list">
                                    ${{ruleListHTML}}
                                </ul>
                            </div>
                        `;
                    }});
                }}
                
                mainPanel.innerHTML = `
                    <div class="main-header">
                        <div class="main-title-section">
                            <h2>Self-Improving Learnings Log</h2>
                            <p>Corrections and classification exceptions automatically appended from operator feedback.</p>
                        </div>
                    </div>
                    
                    <div class="rules-grid">
                        ${{rulesHTML}}
                    </div>
                `;
                
            }} else if (currentActiveTab === 'rubric') {{
                // Render _rubric.md details
                let watchlistHTML = '';
                RUBRIC_DATA.watchlist.forEach(sec => {{
                    let itemsHTML = '';
                    sec.items.forEach(it => {{
                        itemsHTML += `
                            <div class="watchlist-card">
                                <span class="watchlist-name">${{it.name}}</span>
                                <p class="watchlist-desc">${{it.description}}</p>
                            </div>
                        `;
                    }});
                    
                    watchlistHTML += `
                        <div class="rubric-sec-header">${{sec.category}}</div>
                        <div class="watchlist-grid">
                            ${{itemsHTML}}
                        </div>
                    `;
                }});
                
                let autoskipHTML = '';
                RUBRIC_DATA.autoskip.forEach(rule => {{
                    autoskipHTML += `
                        <li><strong>${{rule.title}}</strong> — ${{rule.description}}</li>
                    `;
                }});
                
                mainPanel.innerHTML = `
                    <div class="main-header">
                        <div class="main-title-section">
                            <h2>System Knowledge & Rubric Rules</h2>
                            <p>Standard classification guidelines used for daily screening filters.</p>
                        </div>
                    </div>
                    
                    ${{watchlistHTML}}
                    
                    <div class="rubric-sec-header">Automatic Skip Rubric (Out of Scope)</div>
                    <ul class="rule-list" style="padding: 16px; background-color: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--border-color); display: flex; flex-direction: column; gap: 12px;">
                        ${{autoskipHTML}}
                    </ul>
                `;
            }}
        }}

        // Initial Page Bootstrapping
        renderSidebar();
        renderMainContent();
    </script>
</body>
</html>
"""
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print("Dashboard created successfully!")

if __name__ == "__main__":
    main()
