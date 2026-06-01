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
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
