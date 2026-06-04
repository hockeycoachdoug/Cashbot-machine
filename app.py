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
    body += "<a href='/fbmarket' class='btn' style='background:#1877f2'>FB Marketplace</a>"
    body += "<a href='/sell' class='btn' style='background:#e44d26'>Selling Tools</a>"
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
        output = ai(f"You are an expert eBay seller. Create a complete eBay listing for: Item: {item}, Condition: {condition}, Details: {details}. Provide: 1. TITLE (80 chars max, keyword-rich) 2. DESCRIPTION (compelling, bullet points) 3. SUGGESTED PRICE (typical sold prices, recommended listing price) 4. CATEGORY (eBay category path) 5. SHIPPING (recommended method and cost) 6. PRO TIPS (2-3 tips to sell faster). Be specific and realistic.")
        return page("eBay Listing", f"<h1>eBay Listing Ready</h1><pre>{output}</pre><a href='/ebay'>List Another Item</a>", "/ebay")
    body = "<h1>eBay Listing Generator</h1><form method='post'><input name='item' placeholder='Item name'/><select name='condition'><option>Like New</option><option>Very Good</option><option>Good</option><option>Acceptable</option><option>For Parts</option></select><textarea name='details' placeholder='Extra details: what is included, any defects, accessories...' style='height:120px'></textarea><button type='submit'>Generate eBay Listing</button></form>"
    return page("eBay Lister", body, "/")

@app.route("/fbmarket", methods=["GET", "POST"])
def fbmarket():
    if auth_required(): return redirect("/login")
    if request.method == "POST":
        item = request.form.get("item", "")
        condition = request.form.get("condition", "")
        details = request.form.get("details", "")
        price = request.form.get("price", "")
        output = ai(f"Create a Facebook Marketplace listing for: Item: {item}, Condition: {condition}, Price: ${price}, Details: {details}. Include: 1. TITLE 2. DESCRIPTION (casual friendly tone) 3. CATEGORY 4. PRICE TIPS 5. THREE TIPS to sell faster locally 6. MEETUP SAFETY TIPS.")
        return page("FB Marketplace", f"<h1>Facebook Marketplace Listing</h1><pre>{output}</pre><a href='/fbmarket'>List Another</a>", "/fbmarket")
    body = "<h1>Facebook Marketplace Generator</h1><form method='post'><input name='item' placeholder='Item name'/><select name='condition'><option>New</option><option>Like New</option><option>Good</option><option>Fair</option><option>Poor</option></select><input name='price' placeholder='Your asking price (e.g. 75)'/><textarea name='details' placeholder='Extra details...' style='height:100px'></textarea><button type='submit'>Generate Listing</button></form>"
    return page("FB Marketplace", body, "/")

@app.route("/sell")
def sell():
    if auth_required(): return redirect("/login")
    body = "<h1>🛒 Selling Tools</h1>"
    body += "<a href='/sell/craigslist' style='display:block;padding:14px;background:#1a1a1a;color:#fff;border-radius:8px;margin:8px 0'>📋 Craigslist Generator</a>"
    body += "<a href='/sell/pricecheck' style='display:block;padding:14px;background:#1a1a1a;color:#fff;border-radius:8px;margin:8px 0'>💲 Price Research — What does it actually sell for?</a>"
    body += "<a href='/sell/bulklister' style='display:block;padding:14px;background:#1a1a1a;color:#fff;border-radius:8px;margin:8px 0'>📦 Bulk Lister — List 10 items at once</a>"
    body += "<a href='/sell/negotiator' style='display:block;padding:14px;background:#1a1a1a;color:#fff;border-radius:8px;margin:8px 0'>🤝 Offer Negotiator — Counter lowball offers</a>"
    return page("Selling Tools", body)

@app.route("/sell/craigslist", methods=["GET", "POST"])
def craigslist():
    if auth_required(): return redirect("/login")
    if request.method == "POST":
        item = request.form.get("item", "")
        price = request.form.get("price", "")
        location = request.form.get("location", "")
        details = request.form.get("details", "")
        output = ai(f"Create a Craigslist listing for: Item: {item}, Price: ${price}, Location: {location}, Details: {details}. Include: 1. TITLE (short, clear, no caps abuse) 2. DESCRIPTION (honest, straightforward, Craigslist style — no fluff) 3. BEST CATEGORY to post in 4. PRICE TIP (is this priced right for Craigslist?) 5. TWO SAFETY TIPS for Craigslist transactions. Keep it simple and direct.")
        return page("Craigslist", f"<h1>Craigslist Listing Ready</h1><pre>{output}</pre><a href='/sell/craigslist'>List Another</a>", "/sell")
    body = "<h1>📋 Craigslist Generator</h1><form method='post'><input name='item' placeholder='Item name'/><input name='price' placeholder='Asking price (e.g. 75)'/><input name='location' placeholder='Your city or area'/><textarea name='details' placeholder='Condition, what is included, any defects...' style='height:100px'></textarea><button type='submit'>Generate Listing</button></form>"
    return page("Craigslist", body, "/sell")

@app.route("/sell/pricecheck", methods=["GET", "POST"])
def pricecheck():
    if auth_required(): return redirect("/login")
    if request.method == "POST":
        item = request.form.get("item", "")
        condition = request.form.get("condition", "")
        output = ai(f"You are an expert reseller. Research realistic sold prices for: {item} in {condition} condition. Provide: 1. EBAY SOLD PRICE RANGE (low to high, typical) 2. FACEBOOK MARKETPLACE RANGE 3. CRAIGSLIST RANGE 4. BEST PLATFORM to sell this item and why 5. RECOMMENDED LISTING PRICE to sell within 7 days 6. ANY TIPS specific to selling this item. Be honest and specific based on real market knowledge.")
        return page("Price Research", f"<h1>💲 Price Research Results</h1><pre>{output}</pre><a href='/sell/pricecheck'>Check Another Item</a>", "/sell")
    body = "<h1>💲 Price Research</h1><p>Find out what your item actually sells for before listing it.</p><form method='post'><input name='item' placeholder='Item name (e.g. iPhone 13, Air Jordan 11, Vitamix blender)'/><select name='condition'><option>Like New</option><option>Very Good</option><option>Good</option><option>Fair</option><option>For Parts</option></select><button type='submit'>Research Price</button></form>"
    return page("Price Research", body, "/sell")

@app.route("/sell/bulklister", methods=["GET", "POST"])
def bulklister():
    if auth_required(): return redirect("/login")
    if request.method == "POST":
        items = request.form.get("items", "")
        platform = request.form.get("platform", "")
        output = ai(f"You are an expert reseller. Create ready-to-post {platform} listings for each of these items: {items}. For each item provide: TITLE, one-paragraph DESCRIPTION, and SUGGESTED PRICE. Separate each listing clearly with the item name as a header. Be specific and realistic with prices.")
        return page("Bulk Lister", f"<h1>📦 Bulk Listings Ready</h1><pre>{output}</pre><a href='/sell/bulklister'>List More Items</a>", "/sell")
    body = "<h1>📦 Bulk Lister</h1><p>Describe up to 10 items — get all listings generated at once.</p><form method='post'><textarea name='items' placeholder='List your items, one per line. Include condition. Example:\nNike Air Max size 10, good condition\niPad mini 3rd gen, cracked screen\nKitchenAid mixer, like new with attachments' style='height:200px'></textarea><select name='platform'><option>eBay</option><option>Facebook Marketplace</option><option>Craigslist</option></select><button type='submit'>Generate All Listings</button></form>"
    return page("Bulk Lister", body, "/sell")

@app.route("/sell/negotiator", methods=["GET", "POST"])
def negotiator():
    if auth_required(): return redirect("/login")
    if request.method == "POST":
        item = request.form.get("item", "")
        asking = request.form.get("asking", "")
        offer = request.form.get("offer", "")
        platform = request.form.get("platform", "")
        output = ai(f"I am selling a {item} for ${asking} on {platform}. A buyer offered ${offer}. Write 3 counter-offer responses: 1. FIRM response (politely hold price) 2. FLEXIBLE response (meet in the middle) 3. FINAL OFFER response (lowest you should go with reasoning). Each response should be short, friendly, and ready to send. Also tell me: is their offer reasonable or a lowball? What is a fair final price?")
        return page("Negotiator", f"<h1>🤝 Counter-Offer Responses</h1><pre>{output}</pre><a href='/sell/negotiator'>New Negotiation</a>", "/sell")
    body = "<h1>🤝 Offer Negotiator</h1><p>Got a lowball offer? Get 3 ready-to-send counter responses.</p><form method='post'><input name='item' placeholder='What are you selling?'/><input name='asking' placeholder='Your asking price (e.g. 100)'/><input name='offer' placeholder='Their offer (e.g. 60)'/><select name='platform'><option>eBay</option><option>Facebook Marketplace</option><option>Craigslist</option><option>Other</option></select><button type='submit'>Generate Counter Offers</button></form>"
    return page("Negotiator", body, "/sell")

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
