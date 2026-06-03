import os
import subprocess
from flask import Flask, request, session, redirect
from openai import OpenAI

app = Flask(__name__)
app.secret_key = os.environ.get("DASHBOARD_PASSWORD", "changeme")
PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "changeme")

def ai(prompt):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

def page(title, body, back="/"):
    return f"<html><head><title>{title}</title><meta name='viewport' content='width=device-width,initial-scale=1'><style>body{{font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;background:#0a0a0a;color:#fff}}input,textarea,select{{width:100%;padding:12px;font-size:1em;border-radius:8px;border:none;margin:10px 0;box-sizing:border-box}}button{{width:100%;padding:14px;background:#ff4444;color:#fff;border:none;border-radius:8px;font-size:1.1em;cursor:pointer}}pre{{background:#1a1a1a;padding:15px;border-radius:8px;white-space:pre-wrap;color:#0f0}}a{{color:#ff4444;text-decoration:none}}.btn{{display:inline-block;padding:10px 20px;color:#fff;border-radius:5px;margin:5px}}.card{{background:#1a1a1a;padding:20px;border-radius:8px;border:1px solid #333;margin:10px 0}}</style></head><body>{body}<br><a href='{back}'>← Back</a></body></html>"

def auth_required():
    return session.get("authenticated") != True

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session["authenticated"] = True
            return redirect("/")
        return page("Login", "<h1>Login</h1><p style='color:#ff4444'>Wrong password. Try again.</p><form method='post'><input name='password' type='password' placeholder='Password'/><button type='submit'>Login</button></form>", "/login")
    return page("Login", "<h1>Cash.bot Machine</h1><p>Enter your password to continue.</p><form method='post'><input name='password' type='password' placeholder='Password'/><button type='submit'>Login</button></form>", "/login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/dougbot", methods=["GET", "POST"])
def dougbot():
    if request.method == "POST":
        topic = request.form.get("topic", "US politics")
        posts = ai(f"Generate 10 short funny biting political satire posts for X about: {topic}. Max 280 chars each. Numbered list.")
        return page("DougBot", f"<h1>DougBot</h1><pre>{posts}</pre><a href='/dougbot'>Generate More</a>")
    body = "<h1>DougBot</h1><p>Political satire posts, generated instantly.</p><form method='post'><input name='topic' placeholder='e.g. Trump, NATO, Congress...'/><button type='submit'>Generate 10 Posts</button></form>"
    return page("DougBot", body)

@app.route("/")
def home():
    if auth_required(): return redirect("/login")
    body = "<h1>Cash.bot Machine</h1><p>Status: <strong>Online</strong></p><h2>Tools</h2>"
    body += "<a href='/generate' class='btn' style='background:#000'>Generate Posts</a>"
    body += "<a href='/terminal' class='btn' style='background:#1a1a2e'>Terminal</a>"
    body += "<a href='/files' class='btn' style='background:#16213e'>Files</a>"
    body += "<a href='/content' class='btn' style='background:#2d1b69'>Content</a>"
    body += "<a href='/dougbot' class='btn' style='background:#6b0000'>DougBot</a>"
    body += "<a href='/reach' class='btn' style='background:#0a3d0a'>REACH</a>"
    body += "<a href='/brain' class='btn' style='background:#3d2800'>BRAIN</a>"
    body += "<a href='/earn' class='btn' style='background:#1a4a1a'>EARN</a>"
    body += "<a href='/ebay' class='btn' style='background:#0064d2'>eBay Lister</a>"
    body += "<br><br><a href='/logout' style='color:#666;font-size:0.9em'>Logout</a>"
    return page("Cash.bot", body, "/")

@app.route("/generate")
def generate():
    if auth_required(): return redirect("/login")
    result = subprocess.run(["python", "content_engine.py"], capture_output=True, text=True)
    output = result.stdout or result.stderr
    return page("Generate", f"<h1>Generated Posts</h1><pre>{output}</pre>")

@app.route("/terminal")
def terminal():
    if auth_required(): return redirect("/login")
    body = "<h1>Terminal</h1><form method='post' action='/run'><input name='cmd' placeholder='Enter command...'/><button type='submit'>Run</button></form>"
    return page("Terminal", body)

@app.route("/run", methods=["POST"])
def run():
    if auth_required(): return redirect("/login")
    cmd = request.form.get("cmd", "")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout or result.stderr
    return page("Output", f"<h1>Output</h1><pre>{output}</pre>", "/terminal")

@app.route("/files")
def files():
    if auth_required(): return redirect("/login")
    result = subprocess.run("ls /app", shell=True, capture_output=True, text=True)
    file_list = result.stdout.strip().split("\n")
    links = "".join([f"<li><a href='/files/{f}'>{f}</a></li>" for f in file_list])
    return page("Files", f"<h1>Files</h1><ul>{links}</ul>")

@app.route("/files/<path:filename>")
def view_file(filename):
    if auth_required(): return redirect("/login")
    try:
        content = open(f"/app/{filename}").read()
        body = f"<h1>{filename}</h1><pre>{content}</pre><a href='/edit/{filename}' class='btn' style='background:#000'>Edit</a>"
        return page(filename, body, "/files")
    except Exception as e:
        return page("Error", f"<p>{e}</p>", "/files")

@app.route("/edit/<path:filename>")
def edit_file(filename):
    if auth_required(): return redirect("/login")
    try:
        content = open(f"/app/{filename}").read()
        body = f"<h1>Edit: {filename}</h1><form method='post' action='/save/{filename}'><textarea name='content' style='height:60vh'>{content}</textarea><button type='submit'>Save</button></form>"
        return page(filename, body, f"/files/{filename}")
    except Exception as e:
        return page("Error", f"<p>{e}</p>", "/files")

@app.route("/save/<path:filename>", methods=["POST"])
def save_file(filename):
    if auth_required(): return redirect("/login")
    try:
        open(f"/app/{filename}", "w").write(request.form.get("content", ""))
        return page("Saved", f"<h1>Saved</h1><p>{filename} saved.</p><a href='/files/{filename}'>View</a>", "/files")
    except Exception as e:
        return page("Error", f"<p>{e}</p>", "/files")

@app.route("/ebay", methods=["GET", "POST"])
def ebay():
    if auth_required(): return redirect("/login")
    if request.method == "POST":
        item = request.form.get("item", "")
        condition = request.form.get("condition", "")
        details = request.form.get("details", "")
        output = ai(f"""You are an expert eBay seller. Create a complete eBay listing for this item:
Item: {item}
Condition: {condition}
Details: {details}

Provide:
1. TITLE (80 chars max, keyword-rich)
2. DESCRIPTION (compelling, bullet points, includes condition and what's included)
3. SUGGESTED PRICE (research typical sold prices, give a range and recommended listing price)
4. CATEGORY (eBay category path)
5. SHIPPING (recommended shipping method and estimated cost)
6. PRO TIPS (2-3 tips to sell this item faster)

Be specific and realistic.""")
        return page("eBay Listing", f"<h1>eBay Listing Ready</h1><pre>{output}</pre><a href='/ebay'>List Another Item</a>", "/ebay")
    body = """<h1>🛒 eBay Listing Generator</h1>
    <p>Describe your item and get a complete ready-to-paste eBay listing.</p>
    <form method='post'>
        <input name='item' placeholder='Item name (e.g. Magical Butter Machine MB2e)'/>
        <select name='condition'>
            <option value='Like New'>Like New</option>
            <option value='Very Good'>Very Good</option>
            <option value='Good'>Good</option>
            <option value='Acceptable'>Acceptable</option>
            <option value='For Parts'>For Parts / Not Working</option>
        </select>
        <textarea name='details' placeholder='Extra details: what is included, any defects, original box, accessories, age of item...' style='height:120px'></textarea>
        <button type='submit'>Generate eBay Listing</button>
    </form>"""
    return page("eBay Lister", body, "/")

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
    if auth_required(): return redirect("/login")
    links = "".join([f"<a href='/content/{k}' style='display:block;padding:14px;background:#1a1a1a;color:#fff;border-radius:8px;margin:8px 0'>{v[0]}</a>" for k, v in TOOLS.items()])
    return page("Content Tools", f"<h1>Content Tools</h1>{links}")

@app.route("/content/<tool>", methods=["GET", "POST"])
def content_tool(tool):
    if auth_required(): return redirect("/login")
    if tool not in TOOLS:
        return page("Error", "<p>Tool not found</p>", "/content")
    name, placeholder, prompt = TOOLS[tool]
    if request.method == "POST":
        user_input = request.form.get("input", "")
        output = ai(prompt.replace("{i}", user_input))
        return page(name, f"<h1>{name}</h1><pre>{output}</pre><a href='/content/{tool}'>Generate More</a>", "/content")
    body = f"<h1>{name}</h1><form method='post'><input name='input' placeholder='Enter {placeholder}...'/><button type='submit'>Generate</button></form>"
    return page(name, body, "/content")

REACH_TOOLS = {
    "leads": ("Leads", "target audience or niche", "Generate 10 specific types of potential customers for someone selling: {i}. For each: who they are, where to find them online, and their main pain point."),
    "community": ("Community", "topic or product", "List 10 online communities (subreddits, Discord, Facebook groups, forums) for people interested in: {i}. For each: name, platform, size estimate, and one engagement tip."),
    "email": ("Email", "product and target customer", "Write 3 cold outreach email variations for: {i}. Each: subject line, 3-4 sentence body, CTA. Friendly, not spammy, value-focused."),
    "inbox": ("Inbox Reply", "message you received", "Write 3 reply options for this message: {i}. One formal, one friendly, one brief. Ready to send."),
    "analytics": ("Analytics", "platform and content type", "Create an analytics tracking plan for: {i}. List 5 key metrics, how to measure each, and what good vs bad numbers look like."),
    "research": ("Research", "topic or question", "Research and summarize: {i}. Key facts, trends, opportunities, risks, and 3 actionable insights."),
    "autopost": ("AutoPost Plan", "platform and niche", "Create a 7-day social media posting plan for: {i}. Each day: best time, post type, sample caption, hashtags.")
}

@app.route("/reach")
def reach():
    if auth_required(): return redirect("/login")
    links = "".join([f"<a href='/reach/{k}' style='display:block;padding:14px;background:#1a1a1a;color:#fff;border-radius:8px;margin:8px 0'>{v[0]}</a>" for k, v in REACH_TOOLS.items()])
    return page("REACH", f"<h1>REACH Tools</h1>{links}")

@app.route("/reach/<tool>", methods=["GET", "POST"])
def reach_tool(tool):
    if auth_required(): return redirect("/login")
    if tool not in REACH_TOOLS:
        return page("Error", "<p>Tool not found</p>", "/reach")
    name, placeholder, prompt = REACH_TOOLS[tool]
    if request.method == "POST":
        user_input = request.form.get("input", "")
        output = ai(prompt.replace("{i}", user_input))
        return page(name, f"<h1>{name}</h1><pre>{output}</pre><a href='/reach/{tool}'>Generate More</a>", "/reach")
    body = f"<h1>{name}</h1><form method='post'><input name='input' placeholder='Enter {placeholder}...'/><button type='submit'>Generate</button></form>"
    return page(name, body, "/reach")

BRAIN_TOOLS = {
    "research": ("Deep Research", "topic or question", "You are an expert researcher. Give a thorough, accurate, well-structured report on: {i}. Include: overview, key facts, current state, opportunities, risks, and 5 actionable insights. Be specific."),
    "summarize": ("Summarize", "text or article to summarize", "Summarize this clearly and concisely, keeping all key points: {i}"),
    "explain": ("Explain It", "concept to explain", "Explain this in simple plain English as if to a smart 15-year-old: {i}. Use examples and analogies."),
    "plan": ("Action Plan", "goal or problem", "Create a detailed step-by-step action plan to achieve: {i}. Include timeline, resources needed, potential obstacles, and how to overcome them."),
    "brainstorm": ("Brainstorm", "topic or challenge", "Generate 20 creative ideas for: {i}. Range from practical to wild. No filtering. Numbered list."),
    "debate": ("Debate Both Sides", "topic or question", "Give the strongest possible arguments FOR and AGAINST: {i}. Be balanced, fair, and thorough. Then give a neutral summary."),
    "decision": ("Decision Helper", "decision you need to make", "Help me decide: {i}. List pros and cons of each option, the key factors to consider, and a recommended path with reasoning.")
}

@app.route("/brain")
def brain():
    if auth_required(): return redirect("/login")
    links = "".join([f"<a href='/brain/{k}' style='display:block;padding:14px;background:#1a1a1a;color:#fff;border-radius:8px;margin:8px 0'>{v[0]}</a>" for k, v in BRAIN_TOOLS.items()])
    return page("BRAIN", f"<h1>BRAIN Tools</h1>{links}")

@app.route("/brain/<tool>", methods=["GET", "POST"])
def brain_tool(tool):
    if auth_required(): return redirect("/login")
    if tool not in BRAIN_TOOLS:
        return page("Error", "<p>Tool not found</p>", "/brain")
    name, placeholder, prompt = BRAIN_TOOLS[tool]
    if request.method == "POST":
        user_input = request.form.get("input", "")
        output = ai(prompt.replace("{i}", user_input))
        return page(name, f"<h1>{name}</h1><pre>{output}</pre><a href='/brain/{tool}'>Ask Again</a>", "/brain")
    body = f"<h1>{name}</h1><form method='post'><input name='input' placeholder='Enter {placeholder}...'/><button type='submit'>Generate</button></form>"
    return page(name, body, "/brain")

@app.route("/earn")
def earn():
    if auth_required(): return redirect("/login")
    body = "<h1>EARN</h1>"
    body += "<a href='/earn/pay' style='display:block;padding:14px;background:#1a1a1a;color:#fff;border-radius:8px;margin:8px 0'>💳 Pay — Invoice generator</a>"
    body += "<a href='/earn/wallet' style='display:block;padding:14px;background:#1a1a1a;color:#fff;border-radius:8px;margin:8px 0'>👛 Wallet — Track your crypto addresses</a>"
    body += "<a href='/earn/faucet' style='display:block;padding:14px;background:#1a1a1a;color:#fff;border-radius:8px;margin:8px 0'>🚰 FaucetHub — Find free crypto faucets</a>"
    body += "<a href='/earn/trade' style='display:block;padding:14px;background:#1a1a1a;color:#fff;border-radius:8px;margin:8px 0'>📈 Trade — Practice trading strategies</a>"
    return page("EARN", body)

@app.route("/earn/pay", methods=["GET", "POST"])
def earn_pay():
    if auth_required(): return redirect("/login")
    if request.method == "POST":
        your_name = request.form.get("your_name", "")
        client_name = request.form.get("client_name", "")
        service = request.form.get("service", "")
        amount = request.form.get("amount", "")
        due_date = request.form.get("due_date", "")
        payment_method = request.form.get("payment_method", "")
        invoice = f"<div class='card'><h2>INVOICE</h2><p><strong>From:</strong> {your_name}</p><p><strong>To:</strong> {client_name}</p><hr style='border-color:#333'><p><strong>Service:</strong> {service}</p><p><strong>Amount Due:</strong> ${amount}</p><p><strong>Due Date:</strong> {due_date}</p><p><strong>Payment Method:</strong> {payment_method}</p><hr style='border-color:#333'><p style='color:#aaa;font-size:0.9em'>Thank you for your business.</p></div><br><button onclick='window.print()' style='background:#1a4a1a'>Print / Save as PDF</button>"
        return page("Invoice", f"<h1>Invoice Generated</h1>{invoice}", "/earn/pay")
    body = "<h1>💳 Invoice Generator</h1><form method='post'><input name='your_name' placeholder='Your name or business name'/><input name='client_name' placeholder='Client name'/><input name='service' placeholder='Service provided'/><input name='amount' placeholder='Amount (e.g. 50)'/><input name='due_date' placeholder='Due date'/><input name='payment_method' placeholder='Payment method (PayPal, Venmo, etc)'/><button type='submit'>Generate Invoice</button></form>"
    return page("Pay", body, "/earn")

@app.route("/earn/wallet", methods=["GET", "POST"])
def earn_wallet():
    if auth_required(): return redirect("/login")
    if request.method == "POST":
        coin = request.form.get("coin", "")
        address = request.form.get("address", "")
        note = request.form.get("note", "")
        body = f"<h1>👛 Wallet Entry Saved</h1><div class='card'><p><strong>Coin:</strong> {coin}</p><p><strong>Address:</strong> <code style='word-break:break-all'>{address}</code></p><p><strong>Note:</strong> {note}</p></div><br><a href='/earn/wallet'>Add Another</a>"
        return page("Wallet", body, "/earn")
    body = "<h1>👛 Wallet Tracker</h1><form method='post'><input name='coin' placeholder='Coin (e.g. Bitcoin, Ethereum, USDT)'/><input name='address' placeholder='Your wallet address'/><input name='note' placeholder='Note (e.g. main wallet, tips wallet)'/><button type='submit'>Save Address</button></form>"
    return page("Wallet", body, "/earn")

@app.route("/earn/faucet")
def earn_faucet():
    if auth_required(): return redirect("/login")
    faucets = ai("List 10 legitimate free crypto faucets that are currently active. For each: name, URL, which coin they give, how often you can claim, and estimated earnings per day. Be honest about amounts - they are small.")
    return page("FaucetHub", f"<h1>🚰 FaucetHub</h1><pre>{faucets}</pre>", "/earn")

@app.route("/earn/trade", methods=["GET", "POST"])
def earn_trade():
    if auth_required(): return redirect("/login")
    if request.method == "POST":
        strategy = request.form.get("strategy", "")
        output = ai(f"Analyze this trading strategy and give detailed feedback: {strategy}. Include: strengths, weaknesses, risk level, potential improvements, and a realistic assessment of profitability. Be honest.")
        return page("Trade", f"<h1>📈 Strategy Analysis</h1><pre>{output}</pre><a href='/earn/trade'>Analyze Another</a>", "/earn")
    body = "<h1>📈 Trade Analyzer</h1><form method='post'><textarea name='strategy' placeholder='Describe your trading strategy...' style='height:150px'></textarea><button type='submit'>Analyze Strategy</button></form>"
    return page("Trade", body, "/earn")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
