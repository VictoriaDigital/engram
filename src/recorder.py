#!/usr/bin/env python3
"""
Engram Recorder - Captures everything from OpenClaw sessions.

Usage:
    python recorder.py serve      # Run HTTP server to receive hooks
    python recorder.py search     # Query recorded history
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

ENGRAM_DIR = Path(__file__).parent.parent
DB_PATH = ENGRAM_DIR / "engram.db"
RAW_DIR = ENGRAM_DIR / "raw"

def init_db():
    """Initialize SQLite database."""
    RAW_DIR.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            session_key TEXT,
            direction TEXT,
            channel TEXT,
            sender TEXT,
            content TEXT,
            tool_calls TEXT,
            raw JSON
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON messages(session_key)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sender ON messages(sender)")
    conn.commit()
    conn.close()
    print(f"[engram] Database initialized at {DB_PATH}")

def record_message(data: dict):
    """Record a message to both raw log and SQLite."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Append to daily raw log
    today = datetime.utcnow().strftime("%Y-%m-%d")
    raw_file = RAW_DIR / f"{today}.jsonl"
    with open(raw_file, "a") as f:
        f.write(json.dumps({"timestamp": timestamp, **data}) + "\n")
    
    # Insert into SQLite
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO messages (timestamp, session_key, direction, channel, sender, content, tool_calls, raw)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp,
        data.get("session_key"),
        data.get("direction"),
        data.get("channel"),
        data.get("sender"),
        data.get("content"),
        json.dumps(data.get("tool_calls", [])),
        json.dumps(data)
    ))
    conn.commit()
    conn.close()
    print(f"[engram] Recorded: {data.get('direction', '?')} from {data.get('sender', '?')[:20]}")

class EngramHandler(BaseHTTPRequestHandler):
    """HTTP handler for receiving OpenClaw hooks."""
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            record_message(data)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "recorded"}')
        except Exception as e:
            print(f"[engram] Error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress default logging

def serve(port=9999):
    """Run the Engram HTTP server."""
    init_db()
    server = HTTPServer(('127.0.0.1', port), EngramHandler)
    print(f"[engram] Listening on http://127.0.0.1:{port}")
    print("[engram] Waiting for OpenClaw hooks...")
    server.serve_forever()

def search(query: str, limit: int = 20):
    """Search recorded messages."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("""
        SELECT timestamp, direction, sender, content 
        FROM messages 
        WHERE content LIKE ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (f"%{query}%", limit))
    
    for row in cursor:
        ts, direction, sender, content = row
        arrow = "→" if direction == "out" else "←"
        preview = (content or "")[:80].replace("\n", " ")
        print(f"{ts[:16]} {arrow} {sender or '?'}: {preview}")
    
    conn.close()

def stats():
    """Show recording statistics."""
    conn = sqlite3.connect(DB_PATH)
    
    total = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    by_dir = conn.execute(
        "SELECT direction, COUNT(*) FROM messages GROUP BY direction"
    ).fetchall()
    by_channel = conn.execute(
        "SELECT channel, COUNT(*) FROM messages GROUP BY channel"
    ).fetchall()
    first = conn.execute(
        "SELECT timestamp FROM messages ORDER BY timestamp ASC LIMIT 1"
    ).fetchone()
    last = conn.execute(
        "SELECT timestamp FROM messages ORDER BY timestamp DESC LIMIT 1"
    ).fetchone()
    
    print(f"[engram] Total messages: {total}")
    print(f"[engram] By direction: {dict(by_dir)}")
    print(f"[engram] By channel: {dict(by_channel)}")
    if first:
        print(f"[engram] First: {first[0]}")
    if last:
        print(f"[engram] Last: {last[0]}")
    
    conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python recorder.py [serve|search|stats]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "serve":
        serve()
    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        search(query)
    elif cmd == "stats":
        init_db()
        stats()
    else:
        print(f"Unknown command: {cmd}")
