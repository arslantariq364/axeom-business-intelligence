"""
Tunnel daemon for Axeom Challenge public deployment verification.
Maintains a reverse SSH tunnel via localhost.run with automatic reconnect.
Saves the active hard-to-guess public URL to docs/live_link.txt.
"""

import re
import sys
import time
import subprocess
from pathlib import Path

URL_FILE = Path("docs/live_link.txt")

def run_tunnel():
    print("[Tunnel] Starting localhost.run tunnel for port 5050...")
    cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ServerAliveInterval=30",
        "-o", "ServerAliveCountMax=3",
        "-R", "80:127.0.0.1:5050",
        "nokey@localhost.run"
    ]
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    
    url_found = False
    for line in iter(proc.stdout.readline, ''):
        print(f"[SSH] {line.strip()}", flush=True)
        if not url_found:
            m = re.search(r'https://[a-zA-Z0-9.-]+\.lhr\.life', line)
            if m:
                url = m.group(0)
                url_found = True
                print(f"[Tunnel] Active public URL: {url}", flush=True)
                URL_FILE.parent.mkdir(parents=True, exist_ok=True)
                URL_FILE.write_text(url.strip())

    proc.wait()
    print(f"[Tunnel] SSH process exited with code {proc.returncode}. Reconnecting in 3s...", flush=True)

if __name__ == "__main__":
    while True:
        try:
            run_tunnel()
        except Exception as e:
            print(f"[Tunnel] Error: {e}", flush=True)
        time.sleep(3)
