#!/usr/bin/env python3
"""
Proxy server for Riya's Corner.
Serves static files and proxies /api/messages → Anthropic API.
"""

import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ── API KEY ──────────────────────────────────────────────
# Production: set ANTHROPIC_API_KEY as an environment variable.
# Local dev: create a key.txt file in this directory.
_key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "key.txt")
API_KEY = (
    os.environ.get("ANTHROPIC_API_KEY", "")
    or (open(_key_file).read().strip() if os.path.exists(_key_file) else "")
)

if not API_KEY:
    raise SystemExit("No API key found. Set ANTHROPIC_API_KEY or create a key.txt file.")

# ── APP ───────────────────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

@app.errorhandler(429)
def rate_limited(e):
    return jsonify({"error": {"message": "Too many requests. Please wait a moment and try again."}}), 429


# ── ROUTES ────────────────────────────────────────────────
@app.route("/")
@app.route("/index.html")
def index():
    return send_from_directory(HERE, "index.html")


@app.route("/api/messages", methods=["POST"])
@limiter.limit("10 per minute; 100 per day")
def proxy():
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
        },
        data=request.get_data(),
        timeout=30,
    )
    return resp.content, resp.status_code, {"Content-Type": "application/json"}


# ── LOCAL DEV ─────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    print(f"\n  Riya's Corner running at http://localhost:{port}/\n")
    app.run(host="0.0.0.0", port=port, debug=False)
