import subprocess
import json
import time
import logging

class NotebookLMClient:
    def __init__(self, node_path="/Users/user/.local/bin/node", npx_path="/Users/user/.local/bin/npx"):
        self.node_path = node_path
        self.npx_path = npx_path
        self.proc = None
        self.msg_id = 1

    def connect(self):
        logging.info("Connecting to NotebookLM MCP Server...")
        self.proc = subprocess.Popen(
            [self.npx_path, "-y", "notebooklm-mcp-server", "server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Initialize handshake
        self._send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "python-mcp-client", "version": "1.0.0"}
        })
        init_res = self._recv()
        
        # Send initialized notification
        self._send_notification("notifications/initialized")
        logging.info("NotebookLM MCP Server initialized successfully.")
        return init_res

    def disconnect(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
            self.proc = None
            logging.info("Disconnected from NotebookLM MCP Server.")

    def _send(self, method, params=None):
        msg = {
            "jsonrpc": "2.0",
            "id": self.msg_id,
            "method": method,
            "params": params or {}
        }
        self.msg_id += 1
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()

    def _send_notification(self, method, params=None):
        msg = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()

    def _recv(self):
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("MCP server closed stdout stream unexpectedly.")
        try:
            return json.loads(line)
        except Exception as e:
            raise RuntimeError(f"Failed to parse JSON-RPC response: {line}. Error: {e}")

    def call_tool(self, name, arguments=None):
        # We need to loop because the server might send progress or notifications before returning the tool result
        self._send("tools/call", {
            "name": name,
            "arguments": arguments or {}
        })
        
        expected_id = self.msg_id - 1
        while True:
            resp = self._recv()
            if "id" in resp and resp["id"] == expected_id:
                if "error" in resp:
                    raise RuntimeError(f"Tool {name} failed: {resp['error']}")
                return resp.get("result", {})
            # If it's a notification, ignore or log it
            logging.debug(f"Received notification or unrelated message: {resp}")

    # --- Tool abstraction helpers ---

    def list_notebooks(self):
        res = self.call_tool("notebook_list")
        # Extract notebooks array from the content block if formatted as text, or return the raw array
        # Let's inspect typical tool return format: it is a list of content parts
        # The result from tools/call usually has: {"content": [{"type": "text", "text": "..."}]}
        # But if the server returns JSON data, it could be parsed.
        # Let's parse text response for JSON if possible, or return the content text.
        return res

    def find_or_create_notebook(self, title):
        # List notebooks
        res = self.list_notebooks()
        text_content = ""
        for part in res.get("content", []):
            if part.get("type") == "text":
                text_content += part.get("text", "")
        
        # Parse the notebooks from the text block.
        # Usually list_notebooks outputs a markdown table or text list:
        # e.g., "| ID | Title |" or "Title: Stack Watch (ID: abc)"
        # Let's search for the title and try to extract the ID.
        notebook_id = None
        
        # If it is formatted as json inside the text, try parsing
        try:
            notebooks = json.loads(text_content)
            for nb in notebooks:
                if nb.get("title", "").strip().lower() == title.strip().lower():
                    return nb.get("id")
        except Exception:
            # Fallback to regex matching in text representation
            # Match formats like: "Stack Watch (ID: xyz)" or "ID: xyz - Stack Watch"
            match = re.search(rf"([a-zA-Z0-9_-]+)\s*\|\s*{re.escape(title)}", text_content, re.IGNORECASE)
            if match:
                notebook_id = match.group(1).strip()
            else:
                match2 = re.search(rf"{re.escape(title)}\s*\((?:ID:\s*)?([a-zA-Z0-9_-]+)\)", text_content, re.IGNORECASE)
                if match2:
                    notebook_id = match2.group(1).strip()
                else:
                    # Let's search for lines containing both title and ID
                    for line in text_content.splitlines():
                        if title.lower() in line.lower():
                            # Extract something that looks like a notebook ID: 20-30 character string
                            words = re.findall(r'[a-zA-Z0-9_-]{10,40}', line)
                            for w in words:
                                if w.lower() != title.lower() and w.lower() != "id":
                                    notebook_id = w
                                    break
        
        if notebook_id:
            logging.info(f"Found existing notebook '{title}' with ID {notebook_id}")
            return notebook_id

        # Create new one if not found
        logging.info(f"Notebook '{title}' not found. Creating a new one...")
        create_res = self.call_tool("notebook_create", {"title": title})
        create_text = ""
        for part in create_res.get("content", []):
            if part.get("type") == "text":
                create_text += part.get("text", "")
        
        # Extract ID from creation message: e.g. "Notebook 'Stack Watch' created with ID: xyz"
        words = re.findall(r'[a-zA-Z0-9_-]{10,40}', create_text)
        for w in words:
            if w.lower() != "notebook" and w.lower() != "created" and w.lower() != "title":
                return w
                
        # Fallback: list notebooks again to find the newly created one
        time.sleep(2)
        res = self.list_notebooks()
        # Find by title match in list
        return self._extract_id_by_title_from_text(title, res)

    def _extract_id_by_title_from_text(self, title, res):
        text_content = ""
        for part in res.get("content", []):
            if part.get("type") == "text":
                text_content += part.get("text", "")
        # Find first match
        words = re.findall(r'[a-zA-Z0-9_-]{15,45}', text_content)
        if words:
            return words[0]
        return None

    def add_url(self, notebook_id, url):
        logging.info(f"Adding URL to notebook {notebook_id}: {url}")
        return self.call_tool("notebook_add_url", {
            "notebook_id": notebook_id,
            "url": url
        })

    def add_text(self, notebook_id, title, content):
        logging.info(f"Adding text source to notebook {notebook_id}: {title}")
        return self.call_tool("notebook_add_text", {
            "notebook_id": notebook_id,
            "title": title,
            "text": content
        })

    def query_notebook(self, notebook_id, query):
        logging.info(f"Querying notebook {notebook_id}: {query}")
        res = self.call_tool("notebook_query", {
            "notebook_id": notebook_id,
            "query": query
        })
        text_content = ""
        for part in res.get("content", []):
            if part.get("type") == "text":
                text_content += part.get("text", "")
        return text_content

    def create_audio_overview(self, notebook_id):
        logging.info(f"Triggering Audio Overview for notebook {notebook_id}...")
        res = self.call_tool("audio_overview_create", {
            "notebook_id": notebook_id
        })
        return res

    def poll_studio(self, notebook_id):
        logging.info(f"Polling studio status for notebook {notebook_id}...")
        res = self.call_tool("studio_poll", {
            "notebook_id": notebook_id
        })
        return res

import re
