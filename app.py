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
    <a href="/content" style="padding:10px 20px;background:#2d1b69;color:#fff;text-decoration:none;border-radius:5px;margin:5px;display:inline-block;">🎨 Content</a>
    <a href="/dougbot" style="padding:10px 20px;background:#6b0000;color:#fff;text-decoration:none;border-radius:5px;margin:5px;display:inline-block;">🤖 DougBot</a>
    """

@app.route("/generate")
def generate():
    result = subprocess.run(["python", "content_engine.py"], capture_output=True, text=True)
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
        <title>DougBot</title>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0a0a0a; color: #fff; }
            input { width: 100%; padding: 12px; font-size: 1em; border-radius: 8px; border: none; margin: 10px 0; }
            button { width: 100%; padding: 14px; background: #ff4444; color: #fff; border: none; border-radius: 8px; font-size: 1.1em; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>🤖 DougBot</h1>
        <p>Political satire posts, generated instantly.</p>
        <form method='post' action='/dougbot/generate'>
            <input name='topic' placeholder='e.g. Iran, Congress, Trump, NATO...' />
            <button type='submit'>⚡ Generate 10 Posts</button>
        </form>
        <br><a href='/' style='color:#ff4444;'>← Back</a>
    </body>
    </html>
    """

@app.route("/dougbot/generate", methods=["POST"])
def dougbot_generate():
    topic = request.form.get("topic", "US politics")
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Generate 10 short, funny, biting political satire posts for X (Twitter) about: {topic}. Each post max 280 characters. Numbered list. Dry humor, punchy, shareable."}]
    )
    posts = response.choices[0].message.content
    return f"<!DOCTYPE html><html><head><title>DougBot</title><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{{font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;background:#0a0a0a;color:#fff;}}pre{{background:#1a1a1a;padding:15px;border-radius:8px;white-space:pre-wrap;color:#0f0;}}a{{color:#ff4444;}}</style></head><body><h1>🤖 DougBot</h1><pre>{posts}</pre><br><a href='/dougbot'>← Generate More</a> | <a href='/'>← Home</a></body></html>"

@app.route("/content")
def content():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Content Tools</title>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0a0a0a; color: #fff; }
            a { display: block; padding: 14px; background: #1a1a1a; color: #fff; text-decoration: none; border-radius: 8px; margin: 8px 0; font-size: 1.1em; }
        </style>
    </head>
    <body>
        <h1>🎨 Content Tools</h1>
        <a href="/content/viralshorts">🎬 ViralShorts — Short video scripts</a>
        <a href="/content/marketingcopy">💼 MarketingCopy — Sales & ad copy</a>
        <a href="/content/videohooks">🎣 VideoHooks — Viral opening hooks</a>
        <a href="/content/captions">📝 Captions — Social media captions</a>
        <a href="/content/keywords">🔍 Keywords — SEO keywords</a>
        <a href="/content/thumbnailidea">🖼️ ThumbnailIdea — Thumbnail concepts</a>
        <a href="/content/imageprompt">🎨 ImagePrompt — AI image prompts</a>
        <br><a href="/" style="background:#000;">← Back</a>
    </body>
    </html>
    """

@app.route("/content/<tool>", methods=["GET", "POST"])
def content_tool(tool):
    tools = {
        "viralshorts": ("🎬 ViralShorts", "topic", "Write 3 short-form video scripts (TikTok/Reels style) about: {input}. Each script: hook (1 line), body (3-4 lines), CTA (1 line). Punchy, fast, viral."),
        "marketingcopy": ("💼 MarketingCopy", "product or service", "Write 3 variations of compelling marketing copy for: {input}. Include a headline, 2-3 body sentences, and a call to action. Persuasive and clear."),
        "videohooks": ("🎣 VideoHooks", "topic", "Write 10 viral opening hooks for a video about: {input}. Each hook max 2 sentences. Must grab attention in the first 3 seconds."),
        "captions": ("📝 Captions", "topic or description", "Write 5 engaging social media captions for: {input}. Mix of funny, thoughtful, and punchy. Include relevant hashtags."),
        "keywords": ("🔍 Keywords", "topic", "Generate 20 SEO keywords and phrases for: {input}. Mix of short-tail and long-tail keywords. Format as a numbered list."),
        "thumbnailidea": ("🖼️ ThumbnailIdea", "video topic", "Generate 5 thumbnail ideas for a video about: {input}. Describe the visual elements, text overlay, and color scheme for each."),
        "imageprompt": ("🎨 ImagePrompt", "concept or subject", "Generate 5 detailed AI image generation prompts for: {input}. Each prompt should include subject, style, lighting, mood, and technical details.")
    }
    if tool not in tools:
        return "<h1>Tool not found</h1><a href='/content'>← Back</a>"
    name, placeholder, prompt_template = tools[tool]
    if request.method == "POST":
        user_input = request.form.get("input", "")
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_template.replace("{input}", user_input)}]
        )
        output = response.choices[0].message.content
        return f"<!DOCTYPE html><html><head><title>{name}</title><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{{font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;background:#0a0a0a;color:#fff;}}pre{{background:#1a1a1a;padding:15px;border-radius:8px;white-space:pre-wrap;color:#0f0;}}a{{color:#ff4444;}}</style></head><body><h1>{name}</h1><pre>{output}</pre><br><a href='/content/{tool}'>← Generate More</a> | <a href='/content'>← All Tools</a></body></html>"
    return f"<!DOCTYPE html><html><head><title>{name}</title><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{{font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;background:#0a0a0a;color:#fff;}}input{{width:100%;padding:12px;font-size:1em;border-radius:8px;border:none;margin:10px 0;}}button{{width:100%;padding:14px;background:#ff4444;color:#fff;border:none;border-radius:8px;font-size:1.1em;cursor:pointer;}}</style></head><body><h1>{name}</h1><form method='post'><input name='input' placeholder='Enter {placeholder}...' /><button type='submit'>⚡ Generate</button></form><br><a href='/content' style='color:#ff4444;'>← Back</a></body></html>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    """    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
