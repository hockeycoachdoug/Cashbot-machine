import os
import subprocess
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>💰 Cash.bot Machine</h1>
    <p>Status: <strong>Online</strong></p>
    <ul>
        <li>Honeygain: Running</li>
        <li>Content: Political Satire → X</li>
    </ul>
    <br>
    <a href="/generate" style="padding:10px 20px;background:#000;color:#fff;text-decoration:none;border-radius:5px;">
        ⚡ Generate 10 Posts
    </a>
    """

@app.route("/generate")
def generate():
    result = subprocess.run(
        ["python", "content_engine.py"],
        capture_output=True, text=True
    )
    output = result.stdout or result.stderr
    return f"<h1>Generated Posts</h1><pre>{output}</pre><br><a href='/'>← Back</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
