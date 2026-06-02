import os
import subprocess
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

def ai(prompt):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

def page(title, body, back="/"):
    return f"<html><head><title>{title}</title><meta name='viewport' content='width=device-width,initial-scale=1'><style>body{{font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;background:#0a0a0a;color:#fff}}input,textarea{{width:100%;padding:12px;font-size:1em;border-radius:8px;border:none;margin:10px 0;box-sizing:border-box}}button{{width:100%;padding:14px;background:#ff4444;color:#fff;border:none;border-radius:8px;font-size:1.1em;cursor:pointer}}pre{{background:#1a1a1a;padding:15px;border-radius:8px;white-space:pre-wrap;color:#0f0}}a{{color:#ff4444;text-decoration:none}}.btn{{display:inline-block;padding:10px 20px;color:#fff;border-radius:5px;margin:5px}}</style></head><body>{body}<br><a href='{back}'>← Back</a></body></html>"

@app.route("/")
def home():
    body = "<h1>Cash.bot Machine</h1><p>Status: <strong>Online</strong></p><h2>Tools</h2>"
    body += "<a href='/generate' class='btn' style='background:#000'>Generate Posts</a>"
    body += "<a href='/terminal' class='btn' style='background:#1a1a2e'>Terminal</a>"
    body += "<a href='/files' class='btn' style='background:#16213e'>Files</a>"
    body += "<a href='/content' class='btn' style='background:#2d1b69'>Content</a>"
    body += "<a href='/dougbot' class='btn' style='background:#6b0000'>DougBot</a>"
    return page("Cash.bot", body, "/")

@app.route("/generate")
def generate():
    result = subprocess.run(["python", "content_engine.py"], capture_output=True, text=True)
    output = result.stdout or result.stderr
    return page("Generate", f"<h1>Generated Posts</h1><pre>{output}</pre>")

@app.route("/terminal")
def terminal():
    body = "<h1>Terminal</h1><form method='post' action='/run'><input name='cmd' placeholder='Enter command...'/><button type='submit'>Run</button></form>"
    return page("Terminal", body)

@app.route("/run", methods=["POST"])
def run():
    cmd = request.form.get("cmd", "")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout or result.stderr
    return page("Output", f"<h1>Output</h1><pre>{output}</pre>", "/terminal")

@app.route("/files")
def files():
    result = subprocess.run("ls /app", shell=True, capture_output=True, text=True)
    file_list = result.stdout.strip().split("\n")
    links = "".join([f"<li><a href='/files/{f}'>{f}</a></li>" for f in file_list])
    return page("Files", f"<h1>Files</h1><ul>{links}</ul>")

@app.route("/files/<path:filename>")
def view_file(filename):
    try:
        content = open(f"/app/{filename}").read()
        body = f"<h1>{filename}</h1><pre>{content}</pre><a href='/edit/{filename}' class='btn' style='background:#000'>Edit</a>"
        return page(filename, body, "/files")
    except Exception as e:
        return page("Error", f"<p>{e}</p>", "/files")

@app.route("/edit/<path:filename>")
def edit_file(filename):
    try:
        content = open(f"/app/{filename}").read()
        body = f"<h1>Edit: {filename}</h1><form method='post' action='/save/{filename}'><textarea name='content' style='height:60vh'>{content}</textarea><button type='submit'>Save</button></form>"
        return page(filename, body, f"/files/{filename}")
    except Exception as e:
        return page("Error", f"<p>{e}</p>", "/files")

@app.route("/save/<path:filename>", methods=["POST"])
def save_file(filename):
    try:
        open(f"/app/{filename}", "w").write(request.form.get("content", ""))
        return page("Saved", f"<h1>Saved</h1><p>{filename} saved.</p><a href='/files/{filename}'>View</a>", "/files")
    except Exception as e:
        return page("Error", f"<p>{e}</p>", "/files")

@app.route("/dougbot", methods=["GET", "POST"])
def dougbot():
    if request.method == "POST":
        topic = request.form.get("topic", "US politics")
        posts = ai(f"Generate 10 short funny biting political satire posts for X about: {topic}. Max 280 chars each. Numbered list.")
        return page("DougBot", f"<h1>DougBot</h1><pre>{posts}</pre><a href='/dougbot'>Generate More</a>")
    body = "<h1>DougBot</h1><p>Political satire posts, generated instantly.</p><form method='post'><input name='topic' placeholder='e.g. Trump, NATO, Congress...'/><button type='submit'>Generate 10 Posts</button></form>"
    return page("DougBot", body)

TOOLS = {
    "viralshorts": ("ViralShorts", "topic", "Write 3 TikTok/Reels style video scripts about: {i}. Each: hook (1 line), body (3-4 lines), CTA (1 line). Punchy and viral."),
    "marketingcopy": ("MarketingCopy", "product or service", "Write 3 marketing copy variations for: {i}. Each has headline, 2-3 body sentences, CTA."),
    "videohooks": ("VideoHooks", "topic", "Write 10 viral opening hooks for a video about: {i}. Max 2 sentences each. Grabs attention in 3 seconds."),
    "captions": ("Captions", "topic", "Write 5 social media captions for: {i}. Mix funny, thoughtful, punchy. Include hashtags."),
    "keywords": ("Keywords", "topic", "Generate 20 SEO keywords for: {i}. Mix short and long-tail. Numbered list."),
    "thumbnailidea": ("ThumbnailIdea", "video topic", "Generate 5 YouTube thumbnail ideas for: {i}. Describe visuals, text overlay, colors."),
    "imageprompt": ("ImagePrompt", "concept", "Generate 5 AI image prompts for: {i}. Include subject, style, lighting, mood, technical details.")
}

@app.route("/content")
def content():
    links = "".join([f"<a href='/content/{k}' style='display:block;padding:14px;background:#1a1a1a;color:#fff;border-radius:8px;margin:8px 0'>{v[0]}</a>" for k, v in TOOLS.items()])
    return page("Content Tools", f"<h1>Content Tools</h1>{links}")

@app.route("/content/<tool>", methods=["GET", "POST"])
def content_tool(tool):
    if tool not in TOOLS:
        return page("Error", "<p>Tool not found</p>", "/content")
    name, placeholder, prompt = TOOLS[tool]
    if request.method == "POST":
        user_input = request.form.get("input", "")
        output = ai(prompt.replace("{i}", user_input))
        return page(name, f"<h1>{name}</h1><pre>{output}</pre><a href='/content/{tool}'>Generate More</a>", "/content")
    body = f"<h1>{name}</h1><form method='post'><input name='input' placeholder='Enter {placeholder}...'/><button type='submit'>Generate</button></form>"
    return page(name, body, "/content")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
