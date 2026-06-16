#!/usr/bin/env python3
import subprocess
import json
import os
import re
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
import urllib.parse

# --- Configuration ---
# Resolve workspace relative to script location for cloud/local portability
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SEEN_CACHE_FILE = os.path.join(WORKSPACE_DIR, "processed/seen_releases.json")
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Feeds to poll
GITHUB_RELEASES = {
    "Ollama": "https://github.com/ollama/ollama/releases.atom",
    "Claude Code": "https://github.com/anthropics/claude-code/releases.atom",
    "Mem0": "https://github.com/mem0ai/mem0/releases.atom",
    "tmux": "https://github.com/tmux/tmux/releases.atom",
    "iTerm2": "https://github.com/gnachman/iTerm2/releases.atom",
    "OpenClaw": "https://github.com/openclaw/openclaw/releases.atom",
    "OpenHuman": "https://github.com/tinyhumansai/openhuman/releases.atom"
}

GITHUB_COMMITS = {
    "Desktop Commander (MCP Servers)": "https://github.com/modelcontextprotocol/servers/commits/main.atom"
}

YOUTUBE_CHANNELS = {
    "Andrej Karpathy": "https://www.youtube.com/feeds/videos.xml?channel_id=UCXUPKJO5MZQN11PqgIvyuvQ"
}

HN_KEYWORDS = ["ollama", "claude code", "notebooklm", "wispr flow", "mem0"]

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def http_get(url):
    try:
        result = subprocess.run(
            ['curl', '-sS', '-L', '--max-time', '12', '-A', USER_AGENT, url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return result.stdout, 200
    except subprocess.CalledProcessError as e:
        stderr_msg = e.stderr.decode('utf-8', errors='ignore').strip()
        log(f"Curl error for {url}: {stderr_msg}")
        return None, 500
    except Exception as e:
        log(f"Error executing curl for {url}: {e}")
        return None, 500

def check_url_ok(url):
    try:
        # Check HTTP status code using curl -I
        result = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-I', '-L', '-w', '%{http_code}', '--max-time', '6', '-A', USER_AGENT, url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        status_code = result.stdout.decode('utf-8').strip()
        return status_code == "200"
    except Exception:
        return False

def parse_iso_date(date_str):
    date_str = date_str.replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(date_str)
    except Exception:
        match = re.match(r'^(\d{4})-(\d{2})-(\d{2})', date_str)
        if match:
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), tzinfo=timezone.utc)
        return datetime.now(timezone.utc)

def parse_atom_releases(xml_data, component_name, limit_days=7):
    findings = []
    now = datetime.now(timezone.utc)
    threshold = now - timedelta(days=limit_days)
    
    try:
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        for entry in root.findall('atom:entry', ns):
            title_el = entry.find('atom:title', ns)
            link_el = entry.find('atom:link', ns)
            updated_el = entry.find('atom:updated', ns)
            
            if title_el is not None and link_el is not None and updated_el is not None:
                title = title_el.text.strip()
                url = link_el.attrib.get('href', '').strip()
                updated_str = updated_el.text.strip()
                updated_date = parse_iso_date(updated_str)
                
                if updated_date >= threshold:
                    version_match = re.search(r'(v?\d+\.\d+\.\d+[\w\-\.]*)', title)
                    version = version_match.group(1) if version_match else title
                    
                    findings.append({
                        "title": f"Release {title}",
                        "url": url,
                        "date": updated_date.strftime('%Y-%m-%d'),
                        "component": component_name,
                        "version": version,
                        "type": "release"
                    })
    except Exception as e:
        log(f"Error parsing Atom XML for {component_name}: {e}")
    return findings

def parse_atom_commits(xml_data, component_name, limit_days=7):
    findings = []
    now = datetime.now(timezone.utc)
    threshold = now - timedelta(days=limit_days)
    
    try:
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        for entry in root.findall('atom:entry', ns):
            title_el = entry.find('atom:title', ns)
            link_el = entry.find('atom:link', ns)
            updated_el = entry.find('atom:updated', ns)
            
            if title_el is not None and link_el is not None and updated_el is not None:
                title = title_el.text.strip()
                url = link_el.attrib.get('href', '').strip()
                updated_str = updated_el.text.strip()
                updated_date = parse_iso_date(updated_str)
                
                if updated_date >= threshold:
                    findings.append({
                        "title": f"Commit: {title}",
                        "url": url,
                        "date": updated_date.strftime('%Y-%m-%d'),
                        "component": component_name,
                        "version": url.split('/')[-1][:7],
                        "type": "commit"
                    })
    except Exception as e:
        log(f"Error parsing commits XML for {component_name}: {e}")
    return findings

def poll_hn(keywords, limit_days=7):
    findings = []
    now = datetime.now(timezone.utc)
    threshold = int((now - timedelta(days=limit_days)).timestamp())
    
    for kw in keywords:
        try:
            log(f"Polling HN for: {kw}")
            url = f"https://hn.algolia.com/api/v1/search_by_date?tags=story&numericFilters=created_at_i%3E{threshold}&query={urllib.parse.quote(kw)}"
            data_bytes, status = http_get(url)
            if status == 200 and data_bytes:
                try:
                    res = json.loads(data_bytes.decode('utf-8'))
                    for hit in res.get('hits', []):
                        title = hit.get('title')
                        story_url = hit.get('url')
                        object_id = hit.get('objectID')
                        created_at = hit.get('created_at')
                        
                        if title and object_id:
                            hn_url = f"https://news.ycombinator.com/item?id={object_id}"
                            target_url = story_url if story_url else hn_url
                            
                            findings.append({
                                "title": f"HN: {title}",
                                "url": target_url,
                                "date": parse_iso_date(created_at).strftime('%Y-%m-%d'),
                                "component": "HN Discovery",
                                "version": object_id,
                                "type": "discovery",
                                "hn_discussion": hn_url
                            })
                except Exception as e:
                    log(f"Error parsing HN JSON for {kw}: {e}")
        except Exception as e:
            log(f"Timeout or network error polling HN for keyword {kw}: {e}")
    return findings

def parse_youtube_feed(xml_data, channel_name, limit_days=7):
    findings = []
    now = datetime.now(timezone.utc)
    threshold = now - timedelta(days=limit_days)
    
    try:
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        for entry in root.findall('atom:entry', ns):
            title_el = entry.find('atom:title', ns)
            link_el = entry.find('atom:link', ns)
            published_el = entry.find('atom:published', ns)
            
            if title_el is not None and link_el is not None and published_el is not None:
                title = title_el.text.strip()
                url = link_el.attrib.get('href', '').strip()
                published_str = published_el.text.strip()
                published_date = parse_iso_date(published_str)
                
                if published_date >= threshold:
                    findings.append({
                        "title": f"YouTube: {title} ({channel_name})",
                        "url": url,
                        "date": published_date.strftime('%Y-%m-%d'),
                        "component": "YouTube Discovery",
                        "version": url.split('=')[-1],
                        "type": "discovery"
                    })
    except Exception as e:
        log(f"Error parsing YouTube XML for {channel_name}: {e}")
    return findings

def load_seen_cache():
    if os.path.exists(SEEN_CACHE_FILE):
        try:
            with open(SEEN_CACHE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_seen_cache(cache):
    os.makedirs(os.path.dirname(SEEN_CACHE_FILE), exist_ok=True)
    try:
        with open(SEEN_CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        log(f"Error saving seen cache: {e}")

def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_dir = os.path.join(WORKSPACE_DIR, date_str)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "feed_updates.json")
    
    seen_cache = load_seen_cache()
    new_findings = []
    
    # 1. Poll GitHub Releases
    for comp, url in GITHUB_RELEASES.items():
        try:
            log(f"Polling releases for {comp}...")
            xml_data, status = http_get(url)
            if status == 200 and xml_data:
                findings = parse_atom_releases(xml_data, comp)
                for f in findings:
                    comp_key = f["component"].lower()
                    version = f["version"]
                    if comp_key not in seen_cache:
                        seen_cache[comp_key] = []
                    if version not in seen_cache[comp_key]:
                        if check_url_ok(f["url"]):
                            new_findings.append(f)
                            seen_cache[comp_key].append(version)
                            log(f"Found new release: {comp} {version}")
        except Exception as e:
            log(f"Timeout or network error polling releases for {comp}: {e}")
    
    # 2. Poll GitHub Commits (MCP Servers)
    for comp, url in GITHUB_COMMITS.items():
        try:
            log(f"Polling commits for {comp}...")
            xml_data, status = http_get(url)
            if status == 200 and xml_data:
                findings = parse_atom_commits(xml_data, comp)
                for f in findings:
                    comp_key = f["component"].lower()
                    version = f["version"]
                    if comp_key not in seen_cache:
                        seen_cache[comp_key] = []
                    if version not in seen_cache[comp_key]:
                        if check_url_ok(f["url"]):
                            new_findings.append(f)
                            seen_cache[comp_key].append(version)
                            log(f"Found new commit: {comp} {version}")
        except Exception as e:
            log(f"Timeout or network error polling commits for {comp}: {e}")

    # 3. Poll HN Discovery
    try:
        hn_findings = poll_hn(HN_KEYWORDS)
        for f in hn_findings:
            comp_key = "hn_discovery"
            version = f["version"]
            if comp_key not in seen_cache:
                seen_cache[comp_key] = []
            if version not in seen_cache[comp_key]:
                new_findings.append(f)
                seen_cache[comp_key].append(version)
                log(f"Found new HN discussion: {f['title']}")
    except Exception as e:
        log(f"Error executing HN discovery: {e}")

    # 4. Poll YouTube Channels
    for channel, url in YOUTUBE_CHANNELS.items():
        try:
            log(f"Polling YouTube channel for {channel}...")
            xml_data, status = http_get(url)
            if status == 200 and xml_data:
                findings = parse_youtube_feed(xml_data, channel)
                for f in findings:
                    comp_key = "youtube_discovery"
                    version = f["version"]
                    if comp_key not in seen_cache:
                        seen_cache[comp_key] = []
                    if version not in seen_cache[comp_key]:
                        new_findings.append(f)
                        seen_cache[comp_key].append(version)
                        log(f"Found new video by {channel}: {f['title']}")
        except Exception as e:
            log(f"Timeout or network error polling YouTube for {channel}: {e}")

    # Save outputs
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(new_findings, f, indent=2)
        
    save_seen_cache(seen_cache)
    log(f"Completed! Written {len(new_findings)} updates to {output_file}")

if __name__ == "__main__":
    main()
