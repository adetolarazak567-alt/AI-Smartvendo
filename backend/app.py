# app.py
import os
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_KEY:
    # It's okay to run locally without key for testing, but endpoints will error
    app.logger.warning("OPENROUTER_KEY not set. Set it in environment before production.")

def call_ai(prompt, model="gpt-3.5-turbo", max_tokens=900):
    """Call OpenRouter and return assistant text (raises on HTTP error)."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a concise, professional assistant that produces content optimized for the user's request."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens
    }
    resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # safety: try several shapes
    return data.get("choices", [{}])[0].get("message", {}).get("content") or data.get("result") or ""

# -------------------------
# Endpoints for services
# -------------------------

@app.route("/generate/copywriting", methods=["POST"])
def generate_copywriting():
    body = request.json or {}
    product = body.get("product") or body.get("topic")
    tone = body.get("tone", "persuasive and professional")
    length = body.get("length", "short")  # short / medium / long

    if not product:
        return jsonify({"error":"No product/topic provided"}), 400

    prompt = (
        f"Create {length} marketing copy for: {product}\n"
        f"Tone: {tone}\n\n"
        "Include:\n- 3 headline options\n- 2 short ad captions (max 120 chars)\n- 1 longer product description (3-4 sentences)\n- Suggested CTA (one line)"
    )

    try:
        out = call_ai(prompt)
        return jsonify({"copy": out})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate/freelance", methods=["POST"])
def generate_freelance():
    body = request.json or {}
    platform = body.get("platform", "Upwork/Fiverr")
    gig = body.get("gig") or body.get("service")
    brief = body.get("brief", "")

    if not gig:
        return jsonify({"error":"No gig/service provided"}), 400

    prompt = (
        f"Write an optimized freelance proposal for {platform} for this service: {gig}\n"
        f"Include a 1-sentence hook, a 3-paragraph proposal (short), and 3 bullet points of portfolio/examples. "
        f"User brief: {brief}"
    )

    try:
        out = call_ai(prompt)
        return jsonify({"proposal": out})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate/resume", methods=["POST"])
def generate_resume():
    body = request.json or {}
    info = body.get("info")  # plain text describing user: role, experience, skills, achievements
    role = body.get("target_role", "")

    if not info:
        return jsonify({"error":"No user info provided"}), 400

    prompt = (
        f"Using the following user info, produce a professional resume summary (3-5 bullet achievements), "
        f"a tailored work-experience bullet list for a target role: {role} (if provided), and a short LinkedIn headline + summary.\n\n"
        f"User info:\n{info}\n\nFormat clearly with headings: SUMMARY, EXPERIENCE HIGHLIGHTS, LINKEDIN HEADLINE, LINKEDIN SUMMARY."
    )

    try:
        out = call_ai(prompt)
        return jsonify({"resume": out})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate/business", methods=["POST"])
def generate_business():
    body = request.json or {}
    niche = body.get("niche") or body.get("topic")
    if not niche:
        return jsonify({"error":"No niche/topic provided"}), 400

    prompt = (
        f"Generate 10 business or side-hustle ideas for the niche: {niche}. "
        "For each idea give: a one-line description, target customer, three monetization channels, and a 3-step launch plan."
    )

    try:
        out = call_ai(prompt, max_tokens=1200)
        return jsonify({"ideas": out})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate/social", methods=["POST"])
def generate_social():
    body = request.json or {}
    platform = body.get("platform", "instagram")
    topic = body.get("topic")
    tone = body.get("tone", "engaging")
    if not topic:
        return jsonify({"error":"No topic provided"}), 400

    prompt = (
        f"For {platform}, create: 5 post caption ideas (short), 10 relevant hashtags, 3 short story prompts, "
        f"and a weekly posting schedule (3 posts/week) for the topic: {topic}. Tone: {tone}."
    )

    try:
        out = call_ai(prompt)
        return jsonify({"social": out})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# health-check
@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
