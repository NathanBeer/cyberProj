"""
Flask web application for the cyber attack detection agent.
"""
import json
from flask import Flask, render_template, request, jsonify
from .agent import analyze

app = Flask(__name__, template_folder="../templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_request():
    data = request.get_json()
    if not data or "request" not in data:
        return jsonify({"error": "Missing 'request' field in JSON body"}), 400

    raw_request = data["request"].strip()
    if not raw_request:
        return jsonify({"error": "Empty request"}), 400

    try:
        result = analyze(raw_request)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


def run():
    app.run(debug=True, host="0.0.0.0", port=5000)
