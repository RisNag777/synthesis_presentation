"""Serve the game and store each player's name and score."""

import json
import sqlite3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "scores.db"


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL,
            played_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    return conn


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/scores":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self.respond(400, {"error": "Send a name and a score."})
            return
        name = " ".join(str(payload.get("name", "")).split())
        score = payload.get("score")
        if not name or len(name) > 60 or not isinstance(score, int) or not 0 <= score <= 5:
            self.respond(400, {"error": "Send a name and a score from 0 to 5."})
            return
        conn = connect()
        try:
            cur = conn.execute(
                "INSERT INTO scores (name, score) VALUES (?, ?)",
                (name, score),
            )
            conn.commit()
            saved_id = cur.lastrowid
        finally:
            conn.close()
        self.respond(201, {"id": saved_id, "name": name, "score": score})

    def respond(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    connect()
    server = ThreadingHTTPServer(("127.0.0.1", 8899), Handler)
    print("http://127.0.0.1:8899/", flush=True)
    server.serve_forever()
