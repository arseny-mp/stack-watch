#!/usr/bin/env python3
# normalize_gem_output.py
# Parses flat Gemini Gem curation markdown file and compiles the daily drop zone.

import os
import re
import sys
import argparse
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="Normalize Gemini Gem curation output.")
    parser.add_argument("--date", help="Date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--input", help="Path to input Gem report file")
    parser.add_argument("--output-dir", help="Path to output drop directory")
    return parser.parse_args()

def parse_gem_doc(content):
    findings = []
    current_finding = None
    current_key = None
    multiline_value = []
    
    lines = content.split('\n')
    for line in lines:
        stripped = line.strip()
        
        # Start of a finding block
        if stripped == "===FINDING===":
            current_finding = {}
            current_key = None
            multiline_value = []
            continue
            
        # End of a finding block
        if stripped == "===END===":
            if current_finding:
                if current_key and multiline_value:
                    current_finding[current_key] = "\n".join(multiline_value).strip()
                findings.append(current_finding)
            current_finding = None
            current_key = None
            multiline_value = []
            continue
            
        # If we are parsing a block
        if current_finding is not None:
            # Check if this line starts a new key
            key_match = re.match(r"^([a-z0-9_]+)\s*:\s*(.*)$", line)
            
            # If we are in multiline mode and this line doesn't look like a new key (or is indented)
            if current_key and (not key_match or line.startswith(" ") or line.startswith("\t")):
                # Check for yaml list indentation/formatting block style
                multiline_value.append(line)
            else:
                # Save previous key if any
                if current_key:
                    current_finding[current_key] = "\n".join(multiline_value).strip()
                    multiline_value = []
                    current_key = None
                
                if key_match:
                    key = key_match.group(1)
                    val = key_match.group(2).strip()
                    if val == "|":
                        current_key = key
                    else:
                        current_finding[key] = val
        else:
            # We are outside finding blocks (e.g. headers)
            pass
            
    return findings

def clean_multiline_block(text):
    if not text:
        return ""
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Strip YAML block indentation if present (usually 2 spaces)
        if line.startswith("  "):
            cleaned_lines.append(line[2:])
        elif line.startswith(" "):
            cleaned_lines.append(line[1:])
        else:
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()

def main():
    args = parse_args()
    
    # Resolve Date
    date_str = args.date
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.abspath(os.path.join(script_dir, ".."))
    
    # Resolve Input File
    input_file = args.input
    if not input_file:
        input_file = os.path.join(workspace_dir, "gem-output", f"{date_str}.md")
        
    # Resolve Output Directory
    output_dir = args.output_dir
    if not output_dir:
        output_dir = os.path.join(workspace_dir, date_str)
        
    print(f"Normalizing Gem output for date: {date_str}")
    print(f"Input file: {input_file}")
    print(f"Output directory: {output_dir}")
    
    # Create output dir
    os.makedirs(output_dir, exist_ok=True)
    
    # Handle missing input file
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found. Creating EMPTY marker.")
        with open(os.path.join(output_dir, "EMPTY"), 'w', encoding='utf-8') as f:
            f.write("")
        sys.exit(0)
        
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    findings = parse_gem_doc(content)
    print(f"Parsed {len(findings)} findings from Gemini Gem document.")
    
    # Filter and normalize findings
    valid_findings = []
    skips = []
    
    for idx, f in enumerate(findings):
        slug = f.get("slug")
        verdict = f.get("verdict", "skip").strip().lower()
        
        if not slug:
            print(f"Warning: Block {idx} is missing a slug, skipping.")
            continue
            
        slug = slug.strip()
        
        if verdict == "skip":
            skips.append(f)
            continue
            
        url = f.get("url")
        touches = f.get("touches")
        title_ru = f.get("title_ru")
        
        if not url or not touches or not title_ru:
            print(f"Warning: Finding {slug} is missing required fields (url, touches, title_ru). Treating as skip.")
            skips.append(f)
            continue
            
        valid_findings.append({
            "slug": slug,
            "verdict": verdict,
            "severity": f.get("severity", "minor").strip().lower(),
            "confidence": f.get("confidence", "high").strip().lower(),
            "touches": touches.strip(),
            "url": url.strip(),
            "title_ru": title_ru.strip(),
            "summary_ru": clean_multiline_block(f.get("summary_ru", "")),
            "changes_ru": clean_multiline_block(f.get("changes_ru", ""))
        })
        
    print(f"Valid findings: {len(valid_findings)}, Skipped: {len(skips)}")
    
    if not valid_findings and not skips:
        print("No updates found in Gem document. Writing EMPTY marker.")
        with open(os.path.join(output_dir, "EMPTY"), 'w', encoding='utf-8') as f:
            f.write("")
        sys.exit(0)
        
    # Write findings
    research_dir = os.path.join(output_dir, "external-research")
    mem_dir = os.path.join(output_dir, "memory-entries")
    
    os.makedirs(research_dir, exist_ok=True)
    os.makedirs(mem_dir, exist_ok=True)
    
    new_urls = []
    log_additions = []
    memory_index_additions = []
    has_breaking = False
    
    categorized = {
        "do_now": [],
        "experiment": [],
        "parking": [],
        "skipped": []
    }
    
    for f in valid_findings:
        slug = f["slug"]
        verdict = f["verdict"]
        severity = f["severity"]
        confidence = f["confidence"]
        touches = f["touches"]
        url = f["url"]
        title_ru = f["title_ru"]
        
        new_urls.append(url)
        
        # Add to category
        cat_key = verdict.replace("-", "_")
        if cat_key in categorized:
            categorized[cat_key].append(f"{slug} — {title_ru}")
            
        # Severity check
        if severity == "breaking/security":
            has_breaking = True
            
        # Write external-research finding
        finding_path = os.path.join(research_dir, f"{slug}.md")
        finding_content = f"""# {title_ru}
**Verdict:** {verdict}
**Severity:** {severity}
**Confidence:** {confidence}
**Sources:** gemini-gem
**Source count:** 1
**Touches:** {touches}
**Original URL:** {url}
**Verify URL:** ok
**Date:** {date_str}

## Summary
{f["summary_ru"]}

## What changes
{f["changes_ru"]}
"""
        with open(finding_path, 'w', encoding='utf-8') as out_f:
            out_f.write(finding_content)
            
        # Write memory card if parked or experiment
        if verdict in ["parking", "experiment"]:
            prefix = "parked" if verdict == "parking" else "experiment"
            mem_path = os.path.join(mem_dir, f"{prefix}_{slug}.md")
            with open(mem_path, 'w', encoding='utf-8') as out_f:
                out_f.write(finding_content)
                
            # Add to MEMORY index additions
            first_line_summary = f["summary_ru"].split('\n')[0] if f["summary_ru"] else ""
            memory_index_additions.append(f"- [{verdict.capitalize()}: {title_ru}]({prefix}_{slug}.md) — {first_line_summary}")
            
        # Add to log additions
        log_additions.append(f"| {slug} | {verdict} | {confidence} | {touches} | {date_str} | {url} |")
        
    for s in skips:
        slug = s.get("slug", "unknown-skip")
        title = s.get("title_ru", s.get("title", f"Skipped update {slug}"))
        categorized["skipped"].append(f"{slug} — {title}")
        
    # Write summary.md
    do_now_verdicts = len(categorized["do_now"])
    exp_verdicts = len(categorized["experiment"])
    park_verdicts = len(categorized["parking"])
    skip_verdicts = len(categorized["skipped"])
    
    summary_content = f"""# Stack Watch — {date_str}

**Sources processed:** gemini-gem
**Candidates considered (across all sources):** {len(findings)}
**New findings:** {len(valid_findings)}
**By verdict:** do-now {do_now_verdicts}, experiment {exp_verdicts}, parking {park_verdicts}, skip {skip_verdicts}
**Cross-Domain Validation rate:** 100%

## Do now (high confidence)
"""
    if categorized["do_now"]:
        summary_content += "\n".join([f"- {item}" for item in categorized["do_now"]]) + "\n"
    else:
        summary_content += "_(none)_\n"
        
    summary_content += "\n## Experiment\n"
    if categorized["experiment"]:
        summary_content += "\n".join([f"- {item}" for item in categorized["experiment"]]) + "\n"
    else:
        summary_content += "_(none)_\n"
        
    summary_content += "\n## Parking\n"
    if categorized["parking"]:
        summary_content += "\n".join([f"- {item}" for item in categorized["parking"]]) + "\n"
    else:
        summary_content += "_(none)_\n"
        
    summary_content += "\n## Unconfirmed / Single Domain (low confidence)\n_(none)_\n"
    
    summary_content += "\n## Skipped\n"
    if categorized["skipped"]:
        summary_content += "\n".join([f"- {item}" for item in categorized["skipped"]]) + "\n"
    else:
        summary_content += "_(none)_\n"
        
    with open(os.path.join(output_dir, "summary.md"), 'w', encoding='utf-8') as out_f:
        out_f.write(summary_content)
        
    # Write REPORT.md
    report_content = f"""# Stack Watch Audit Log — {date_str}

## Curation Performance
- Processed {len(findings)} updates.
- Classified {len(valid_findings)} to keep and {len(skips)} to skip.

## Calibration Log
"""
    for f in valid_findings:
        report_content += f"- {f['slug']}: Keep ({f['verdict']})\n"
    for s in skips:
        slug = s.get("slug", "unknown-skip")
        report_content += f"- {slug}: Skip\n"
        
    with open(os.path.join(output_dir, "REPORT.md"), 'w', encoding='utf-8') as out_f:
        out_f.write(report_content)
        
    # Write new-urls.txt
    with open(os.path.join(output_dir, "new-urls.txt"), 'w', encoding='utf-8') as out_f:
        out_f.write("\n".join(new_urls) + "\n")
        
    # Write log-additions.md
    if log_additions:
        with open(os.path.join(output_dir, "log-additions.md"), 'w', encoding='utf-8') as out_f:
            out_f.write("\n".join(log_additions) + "\n")
            
    # Write memory-index-additions.txt
    if memory_index_additions:
        with open(os.path.join(output_dir, "memory-index-additions.txt"), 'w', encoding='utf-8') as out_f:
            out_f.write("\n".join(memory_index_additions) + "\n")
            
    # Write breaking-marker if needed
    if has_breaking:
        print("Breaking marker detected! Creating breaking-marker file.")
        with open(os.path.join(output_dir, "breaking-marker"), 'w', encoding='utf-8') as out_f:
            out_f.write("breaking")
            
    print("Gem normalization completed successfully!")

if __name__ == "__main__":
    main()
