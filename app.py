import os
import subprocess
from flask import Flask, request
app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>💰 Cash.bot Machine</h1>
    <p>Status: <strong>Online</strong></p>
    <h2>Modules</h2>
    <ul>
        <li>🟢 Honeygain: Running</li>
        <li>🟢 Content Engine: Active</li>
    </ul>
    <h2>Tools</h2>
    <a href="/generate" style="padding:10px 20px;background:#000;color:#fff;text-decoration:none;border-radius:5px;margin:5px;display:inline-block;">⚡ Generate Posts</a>
    <a href="/terminal" style="padding:10px 20px;background:#1a1a2e;color:#fff;text-decoration:none;border-radius:5px;margin:5px;display:inline-block;">💻 Terminal</a>
    <a href="/files" style="padding:10px 20px;background:#16213e;color:#fff;text-decoration:none;border-radius:5px;margin:5px;display:inline-block;">📁 Files</a>
    """

@app.route("/generate")
def generate():
    result = subprocess.run(
        ["python", "content_engine.py"],
        capture_output=True, text=True
    )
    output = result.stdout or result.stderr
    return f"<h1>Generated Posts</h1><pre>{output}</pre><br><a href='/'>← Back</a>"

@app.route("/terminal")
def terminal():
    return """
    <h1>💻 Terminal</h1>
    <form method='post' action='/run'>
        <input name='cmd' style='width:80%;padding:10px;font-family:monospace;' placeholder='Enter command...' />
        <button type='submit' style='padding:10px 20px;background:#000;color:#fff;border:none;'>Run</button>
    </form>
    <br><a href='/'>← Back</a>
    """

@app.route("/run", methods=["POST"])
def run():
    cmd = request.form.get("cmd", "")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout or result.stderr
    return f"<h1>Output</h1><pre>{output}</pre><br><a href='/terminal'>← Terminal</a>"

@app.route("/files")
def files():
    result = subprocess.run("ls /app", shell=True, capture_output=True, text=True)
    file_list = result.stdout.strip().split("\n")
    links = "".join([f"<li><a href='/files/{f}'>{f}</a></li>" for f in file_list])
    return f"<h1>📁 Files</h1><ul>{links}</ul><br><a href='/'>← Back</a>"

@app.route("/files/<path:filename>")
def view_file(filename):
    try:
        with open(f"/app/{filename}", "r") as f:
            content = f.read()
        return f"<h1>📄 {filename}</h1><pre>{content}</pre><br><a href='/edit/{filename}' style='padding:10px 20px;background:#000;color:#fff;text-decoration:none;border-radius:5px;'>✏️ Edit</a> <a href='/files'>← Files</a>"
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p><br><a href='/files'>← Files</a>"

@app.route("/edit/<path:filename>")
def edit_file(filename):
    try:
        with open(f"/app/{filename}", "r") as f:
            content = f.read()
        return f"<h1>✏️ Edit: {filename}</h1><form method='post' action='/save/{filename}'><textarea name='content' style='width:100%;height:60vh;font-family:monospace;padding:10px;'>{content}</textarea><br><br><button type='submit' style='padding:10px 20px;background:#000;color:#fff;border:none;border-radius:5px;'>💾 Save</button> <a href='/files/{filename}' style='padding:10px 20px;background:#666;color:#fff;text-decoration:none;border-radius:5px;'>Cancel</a></form>"
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p><br><a href='/files'>← Files</a>"

@app.route("/save/<path:filename>", methods=["POST"])
def save_file(filename):
    try:
        content = request.form.get("content", "")
        with open(f"/app/{filename}", "w") as f:
            f.write(content)
        return f"<h1>✅ Saved</h1><p>{filename} saved successfully.</p><br><a href='/files/{filename}'>View File</a> | <a href='/files'>← Files</a>"
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p><br><a href='/files'>← Files</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
