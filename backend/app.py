from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
import openai

# ----------------------
# Load Environment
# ----------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

openai.api_key = OPENAI_API_KEY

# ----------------------
# App Setup
# ----------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "SUPER_SECRET_KEY")
CORS(app)

# ----------------------
# Dummy Admin Credentials
# ----------------------
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "youremail@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "YourSecurePassword123")

# ----------------------
# Free Trial Tracking (in-memory)
# ----------------------
trials = {
    "copywriting": 3,
    "freelance": 3,
    "resume": 3,
    "business": 3
}

# ----------------------
# Helper: OpenAI request
# ----------------------
def generate_ai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# ----------------------
# ADMIN LOGIN
# ----------------------
@app.route("/admin-login", methods=["POST"])
def admin_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        session["admin_logged_in"] = True
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "error": "Invalid email or password"}), 401

@app.route("/admin-dashboard", methods=["GET"])
def admin_dashboard():
    if session.get("admin_logged_in"):
        return "<h1>Welcome Admin!</h1><p>Here is your admin panel.</p>"
    return "Unauthorized", 401

# ----------------------
# USER TRIALS
# ----------------------
@app.route("/user-trials", methods=["GET"])
def user_trials():
    paid = session.get("paid", False)
    return jsonify({"trials": trials, "paid": paid})

# ----------------------
# PAYMENTS (dummy for now)
# ----------------------
@app.route("/paypal-init", methods=["POST"])
def paypal_init():
    data = request.get_json()
    amount = data.get("amount")
    # Here you would integrate actual PayPal SDK/API
    session["paid"] = True
    return jsonify({"status": "success", "redirect_url": "https://www.paypal.com/checkout"})

@app.route("/crypto-init", methods=["POST"])
def crypto_init():
    # Placeholder for crypto payments
    session["paid"] = True
    return jsonify({"status": "success", "redirect_url": "https://nowpayments.io/checkout"})

# ----------------------
# VENDING MACHINE ENDPOINTS
# ----------------------
@app.route("/copywriting", methods=["POST"])
def copywriting():
    if trials["copywriting"] <= 0 and not session.get("paid"):
        return jsonify({"error": "Free trials finished! Subscribe to continue."}), 403
    data = request.get_json()
    prompt = f"Generate a {data.get('copy_type')} for '{data.get('name')}' in a {data.get('tone')} tone."
    result_text = generate_ai(prompt)
    if not session.get("paid"):
        trials["copywriting"] -= 1
    return jsonify({"result": result_text})

@app.route("/freelance", methods=["POST"])
def freelance():
    if trials["freelance"] <= 0 and not session.get("paid"):
        return jsonify({"error": "Free trials finished! Subscribe to continue."}), 403
    data = request.get_json()
    prompt = (
        f"Write a {data.get('level')} freelance proposal for {data.get('job_type')} "
        f"on {data.get('platform')}."
    )
    result_text = generate_ai(prompt)
    if not session.get("paid"):
        trials["freelance"] -= 1
    return jsonify({"result": result_text})

@app.route("/resume", methods=["POST"])
def resume():
    if trials["resume"] <= 0 and not session.get("paid"):
        return jsonify({"error": "Free trials finished! Subscribe to continue."}), 403
    data = request.get_json()
    prompt = (
        f"Optimize a {data.get('purpose')} with experience: {data.get('experience')}, "
        f"skills: {data.get('skills')}, job title: {data.get('job_title')}."
    )
    result_text = generate_ai(prompt)
    if not session.get("paid"):
        trials["resume"] -= 1
    return jsonify({"result": result_text})

@app.route("/business", methods=["POST"])
def business():
    if trials["business"] <= 0 and not session.get("paid"):
        return jsonify({"error": "Free trials finished! Subscribe to continue."}), 403
    data = request.get_json()
    prompt = f"Generate a {data.get('output')} for the niche '{data.get('niche')}'."
    result_text = generate_ai(prompt)
    if not session.get("paid"):
        trials["business"] -= 1
    return jsonify({"result": result_text})

# ----------------------
# RUN APP
# ----------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
