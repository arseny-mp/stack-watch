#!/usr/bin/env python3
import os
import sys
import time
import logging
import urllib.request
import urllib.parse
import json
import subprocess
from notebooklm_client import NotebookLMClient

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
LOG_FILE = os.path.join(WORKSPACE_DIR, "generate_audio.log")
TOKEN_KEY = "TELEGRAM_TOKEN_UPDATES"

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] Audio-Overview: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_telegram_creds():
    token = os.environ.get("TELEGRAM_TOKEN_UPDATES")
    if not token:
        try:
            result = subprocess.run(
                ['security', 'find-generic-password', '-a', 'hermes', '-s', TOKEN_KEY, '-w'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            token = result.stdout.decode('utf-8').strip()
        except Exception as e:
            logging.warning(f"Could not fetch TELEGRAM_TOKEN_UPDATES from Keychain: {e}")
            
    chat_id = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_HOME_CHANNEL")
    if not chat_id:
        try:
            result = subprocess.run(
                ['security', 'find-generic-password', '-a', 'hermes', '-s', 'TELEGRAM_HOME_CHANNEL', '-w'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            chat_id = result.stdout.decode('utf-8').strip()
        except Exception:
            chat_id = "7656475139"
            
    return token, chat_id

def send_audio_to_telegram(token, chat_id, filepath, caption):
    url = f"https://api.telegram.org/bot{token}/sendAudio"
    
    # Boundary for multipart form upload
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    # Read file content
    with open(filepath, 'rb') as f:
        file_content = f.read()
        
    filename = os.path.basename(filepath)
    
    parts = []
    
    # Add chat_id field
    parts.append(f"--{boundary}".encode('utf-8'))
    parts.append(f'Content-Disposition: form-data; name="chat_id"'.encode('utf-8'))
    parts.append(b"")
    parts.append(str(chat_id).encode('utf-8'))
    
    # Add caption field
    parts.append(f"--{boundary}".encode('utf-8'))
    parts.append(f'Content-Disposition: form-data; name="caption"'.encode('utf-8'))
    parts.append(b"")
    parts.append(caption.encode('utf-8'))
    
    # Add title field
    parts.append(f"--{boundary}".encode('utf-8'))
    parts.append(f'Content-Disposition: form-data; name="title"'.encode('utf-8'))
    parts.append(b"")
    parts.append("Stack Watch Audio Summary".encode('utf-8'))
    
    # Add performer field
    parts.append(f"--{boundary}".encode('utf-8'))
    parts.append(f'Content-Disposition: form-data; name="performer"'.encode('utf-8'))
    parts.append(b"")
    parts.append("NotebookLM".encode('utf-8'))
    
    # Add audio file field
    parts.append(f"--{boundary}".encode('utf-8'))
    parts.append(f'Content-Disposition: form-data; name="audio"; filename="{filename}"'.encode('utf-8'))
    parts.append(b"Content-Type: audio/mpeg")
    parts.append(b"")
    parts.append(file_content)
    
    parts.append(f"--{boundary}--".encode('utf-8'))
    parts.append(b"")
    
    body = b"\r\n".join(parts)
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            if res.get("ok"):
                logging.info("Audio overview sent to Telegram successfully.")
                return True
            else:
                logging.error(f"Telegram returned error: {res}")
    except Exception as e:
        logging.error(f"Failed to upload audio to Telegram: {e}")
    return False

def main():
    token, chat_id = get_telegram_creds()
    if not token or not chat_id:
        logging.error("Telegram credentials missing. Exiting.")
        sys.exit(1)
        
    client = NotebookLMClient()
    try:
        client.connect()
        notebook_id = client.find_or_create_notebook("Stack Watch Knowledge Base")
        logging.info(f"Triggering Audio Overview for notebook: {notebook_id}")
        
        # Start audio overview creation
        client.create_audio_overview(notebook_id)
        
        # Poll studio status
        # Ingestion and podcast generation can take up to 2-3 minutes
        logging.info("Audio Overview triggered. Polling for completion...")
        download_url = None
        max_attempts = 30
        for attempt in range(max_attempts):
            time.sleep(10)
            res = client.poll_studio(notebook_id)
            
            # Extract text from poll output
            text = ""
            for part in res.get("content", []):
                if part.get("type") == "text":
                    text += part.get("text", "")
            
            # Search for completed audio urls or status
            # Typically looks like: [Audio Overview] Status: COMPLETED, Url: https://...
            logging.info(f"Poll status: {text.strip()}")
            if "COMPLETED" in text or "SUCCESS" in text or "audio" in text.lower():
                # Extract URL
                urls = re.findall(r'https?://[^\s\)]+', text)
                for u in urls:
                    if ".wav" in u.lower() or ".mp3" in u.lower() or "audio" in u.lower():
                        download_url = u.strip()
                        break
                if download_url:
                    break
        
        if not download_url:
            logging.error("Failed to retrieve Audio Overview download URL after polling.")
            sys.exit(1)
            
        logging.info(f"Downloading Audio Overview from: {download_url}")
        local_file = "/tmp/stack_watch_overview.wav"
        
        # Download the audio file
        urllib.request.urlretrieve(download_url, local_file)
        logging.info(f"Downloaded audio to {local_file}")
        
        # Send to Telegram
        caption = f"🎙 <b>Stack Watch Audio Summary (NotebookLM Podcast)</b>\nСгенерировано автоматически на основе базы знаний."
        send_audio_to_telegram(token, chat_id, local_file, caption)
        
        # Clean up local file
        if os.path.exists(local_file):
            os.remove(local_file)
            
    except Exception as e:
        logging.error(f"Error during Audio Overview generation: {e}")
        sys.exit(1)
    finally:
        client.disconnect()

import re
if __name__ == "__main__":
    main()
