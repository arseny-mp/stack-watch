import os
import re

def html_escape(text):
    if not text:
        return ""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def get_component_layer(touches):
    touches_upper = touches.upper()
    
    # Layer 1: AI Agents & LLMs
    ai_components = [
        "CHATGPT", "CODEX", "CLAUDE", "KIMI", "HERMES", "OPENCLAW", "OLLAMA",
        "GEMINI", "NOTEBOOKLM", "PI", "GLM", "MINIMAX", "QWEN", "WISPR", "ANTIGRAVITY", "GHOSTEX"
    ]
    if any(comp in touches_upper for comp in ai_components):
        return 1
        
    # Layer 2: Local Dev Environment
    dev_components = ["OBSIDIAN", "CHROME", "MACOS", "HOMEBREW", "NPM", "TMUX", "ITERM", "GHOSTTY"]
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
        
    desc_match = re.search(r'\*\*Что это такое:\*\*\s*(.*)', content)
    if desc_match:
        metadata["description"] = desc_match.group(1).strip()
        
    return metadata
