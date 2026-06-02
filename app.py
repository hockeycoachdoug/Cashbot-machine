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
@app.route("/dougbot")
def dougbot():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DougBot — Political Satire Generator</title>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0a0a0a; color: #fff; }
            h1 { color: #fff; font-size: 2em; }
            p { color: #aaa; }
            input { width: 100%; padding: 12px; font-size: 1em; border-radius: 8px; border: none; margin: 10px 0; }
            button { width: 100%; padding: 14px; background: #ff4444; color: #fff; border: none; border-radius: 8px; font-size: 1.1em; cursor: pointer; }
            pre { background: #1a1a1a; padding: 15px; border-radius: 8px; white-space: pre-wrap; color: #0f0; }
        </style>
    </head>
    <body>
        <h1>🤖 DougBot</h1>
        <p>Political satire posts, generated instantly. Enter any topic.</p>
        <form method='post' action='/dougbot/generate'>
            <input name='topic' placeholder='e.g. Iran, Congress, Trump, NATO...' />
            <button type='submit'>⚡ Generate 10 Posts</button>
        </form>
    </body>
    </html>
    """

@app.route("/dougbot/generate", methods=["POST"])
def dougbot_generate():
    topic = request.form.get("topic", "US politics")
    import os
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"Generate 10 short, funny, biting political satire posts for X (Twitter) about: {topic}. Each post max 280 characters. Numbered list. Dry humor, punchy, shareable."
        }]
    )
    posts = response.choices[0].message.content
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DougBot Results</title>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0a0a0a; color: #fff; }}
            pre {{ background: #1a1a1a; padding: 15px; border-radius: 8px; white-space: pre-wrap; color: #0f0; }}
            a {{ color: #ff4444; }}
        </style>
    </head>
    <body>
        <h1>🤖 DougBot</h1>
        <pre>{posts}</pre>
        <br><a href='/dougbot'>← Generate More</a>
    </body>
    </html>
    """
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
