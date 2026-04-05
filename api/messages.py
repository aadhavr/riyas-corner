import os
import requests
from flask import Flask, request, Response

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

app = Flask(__name__)


@app.route("/api/messages", methods=["POST", "OPTIONS"])
def messages():
    if request.method == "OPTIONS":
        r = Response()
        r.headers["Access-Control-Allow-Origin"] = "*"
        r.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        r.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return r

    if not API_KEY:
        return {"error": {"message": "API key not configured on server."}}, 500

    try:
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
        return Response(resp.content, status=resp.status_code, mimetype="application/json")
    except Exception as e:
        return {"error": {"message": f"Proxy error: {str(e)}"}}, 500
