from flask import Flask, jsonify
from threading import Thread
import time

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>🤖 JOTINHA ADM — Status</h1>
    <p><strong>Status:</strong> ✅ Online</p>
    <ul>
        <li><a href="/status">/status</a> — Status detalhado</li>
        <li><a href="/health">/health</a> — Health check</li>
    </ul>
    """

@app.route('/status')
def status():
    return jsonify({
        "status": "online",
        "bot": "JOTINHA ADM",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

def run():
    app.run(host='0.0.0.0', port=8080, use_reloader=False)

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()
