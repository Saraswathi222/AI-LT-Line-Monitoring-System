import math
from flask import Flask, request, jsonify, render_template, session, redirect, url_for


from flask_cors import CORS
from pymongo import MongoClient
import random
import numpy as np
import joblib
import os
import re
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
live_cache = {}
last_generated_time = None
CACHE_DURATION = 120  # 2 minutes


# ================= APP CONFIG =================
import os

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "../frontend"),
    static_folder=os.path.join(os.path.dirname(__file__), "../frontend")
)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)
app.secret_key = "123saras"
# ================= DATABASE =================
client = MongoClient("mongodb://localhost:27017/")
db = client["lt_line_monitoring"]
users_col = db["users"]
reports_col = db["reports"]   # ⭐ NEW COLLECTION

# ================= LOAD TRAINED MODEL =================
MODEL_PATH = "./ml/fault_model.pkl"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("❌ fault_model.pkl not found. Train the model first.")
model = joblib.load(MODEL_PATH)

# ================= STREETS / LINES =================
STREETS = [
    {"name": "Anna Nagar", "city": "Trichy", "lat": 10.8123, "lng": 78.7056},
    {"name": "Srirangam", "city": "Trichy", "lat": 10.8572, "lng": 78.6880},
    {"name": "Woraiyur", "city": "Trichy", "lat": 10.8250, "lng": 78.6820},
    {"name": "Thillai Nagar", "city": "Trichy", "lat": 10.8205, "lng": 78.6962},
    {"name": "Cantonment", "city": "Trichy", "lat": 10.8055, "lng": 78.6855},

    {"name": "K K Nagar", "city": "Trichy", "lat": 10.8012, "lng": 78.6911},
    {"name": "Ariyamangalam", "city": "Trichy", "lat": 10.7943, "lng": 78.7342},
    {"name": "Golden Rock", "city": "Trichy", "lat": 10.7835, "lng": 78.7210},
    {"name": "Puthur", "city": "Trichy", "lat": 10.8110, "lng": 78.6901},
    {"name": "Kajal Nagar", "city": "Trichy", "lat": 10.8282, "lng": 78.7094},

    {"name": "Bharathidasan Colony", "city": "Trichy", "lat": 10.8180, "lng": 78.7005},
    {"name": "Melapudur", "city": "Trichy", "lat": 10.8068, "lng": 78.6924},
    {"name": "Palakarai", "city": "Trichy", "lat": 10.7991, "lng": 78.6992},
    {"name": "Beema Nagar", "city": "Trichy", "lat": 10.8104, "lng": 78.7039},
    {"name": "Karumandapam", "city": "Trichy", "lat": 10.7925, "lng": 78.6893},

    {"name": "Ponmalai", "city": "Trichy", "lat": 10.7898, "lng": 78.7061},
    {"name": "Edamalaipatti Pudur", "city": "Trichy", "lat": 10.8041, "lng": 78.7423},
    {"name": "Thuvakudi", "city": "Trichy", "lat": 10.7586, "lng": 78.8192},
    {"name": "Kattur", "city": "Trichy", "lat": 10.7750, "lng": 78.7205},
    {"name": "Thiruvanaikoil", "city": "Trichy", "lat": 10.8505, "lng": 78.7054},

    {"name": "Uyyakondan Thirumalai", "city": "Trichy", "lat": 10.8234, "lng": 78.7311},
    {"name": "Senthaneerpuram", "city": "Trichy", "lat": 10.7998, "lng": 78.7135},
    {"name": "Vayalur Road", "city": "Trichy", "lat": 10.8139, "lng": 78.7532},
    {"name": "Subramaniapuram", "city": "Trichy", "lat": 10.7901, "lng": 78.7036},
    {"name": "Ramalinga Nagar", "city": "Trichy", "lat": 10.8199, "lng": 78.7048},

    {"name": "Ayyappa Nagar", "city": "Trichy", "lat": 10.7974, "lng": 78.7284},
    {"name": "Vignesh Nagar", "city": "Trichy", "lat": 10.7843, "lng": 78.7355},
    {"name": "Vasan Nagar", "city": "Trichy", "lat": 10.8218, "lng": 78.7099},
    {"name": "Raja Colony", "city": "Trichy", "lat": 10.8087, "lng": 78.6978},
    {"name": "Shanmuga Nagar", "city": "Trichy", "lat": 10.7920, "lng": 78.7233},

    {"name": "Mannarpuram", "city": "Trichy", "lat": 10.8019, "lng": 78.6724},
    {"name": "Pirattiyur", "city": "Trichy", "lat": 10.8423, "lng": 78.7445},
    {"name": "K Abisekapuram", "city": "Trichy", "lat": 10.8317, "lng": 78.7046},
    {"name": "Thiruchirapalli Fort", "city": "Trichy", "lat": 10.8258, "lng": 78.6945},
    {"name": "Rockfort", "city": "Trichy", "lat": 10.8276, "lng": 78.6931},

    {"name": "Kamaraj Nagar", "city": "Trichy", "lat": 10.7965, "lng": 78.7044},
    {"name": "Periyar Nagar", "city": "Trichy", "lat": 10.8145, "lng": 78.7110},
    {"name": "Jawahar Nagar", "city": "Trichy", "lat": 10.8007, "lng": 78.7172},
    {"name": "Ashok Nagar", "city": "Trichy", "lat": 10.8071, "lng": 78.7194},
    {"name": "LIC Colony", "city": "Trichy", "lat": 10.8126, "lng": 78.7128},

    {"name": "Airport Area", "city": "Trichy", "lat": 10.7654, "lng": 78.7082},
    {"name": "Panayapuram", "city": "Trichy", "lat": 10.8448, "lng": 78.7216},
    {"name": "Inamkulathur", "city": "Trichy", "lat": 10.8392, "lng": 78.7308},
    {"name": "Mullipadi", "city": "Trichy", "lat": 10.8213, "lng": 78.7405},
    {"name": "Kumbakudi", "city": "Trichy", "lat": 10.8351, "lng": 78.7482}
]

PHASES = ["A", "B", "C"]

# ================= FAULT REASON ENGINE =================

def fault_reason(data):
    if data["leakage_current"] > 1.0:
        return {
            "cause": "High leakage current detected",
            "solution": "Inspect insulation, tighten joints, replace damaged cable",
            "action": "Shutdown recommended"
        }
    elif data["temperature_c"] > 75:
        return {
            "cause": "Overheating of line",
            "solution": "Reduce load and improve cooling",
            "action": "Monitor continuously"
        }
    elif data["voltage"] < 200 or data["voltage"] > 250:
        return {
            "cause": "Voltage fluctuation",
            "solution": "Install voltage stabilizer",
            "action": "Maintenance required"
        }
    else:
        return {
            "cause": "Normal operating condition",
            "solution": "No action required",
            "action": "Safe"
        }


# ================= FRONTEND ROUTES (PROTECTED) =================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        return redirect(url_for("home"))
    return render_template("dashboard.html")


@app.route("/reports")
def reports():
    if "user_email" not in session:
        return redirect(url_for("home"))
    return render_template("reports.html")


@app.route("/map")
def map_page():
    if "user_email" not in session:
        return redirect(url_for("home"))
    return render_template("map.html")


@app.route("/profile-page")
def profile_page():
    if "user_email" not in session:
        return redirect(url_for("home"))
    return render_template("profile.html")


# ================= DISTANCE CALCULATION =================
def calculate_distance(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = (math.sin(dlat/2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlng/2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ================= SIGNUP =================
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    email = data.get("email", "").strip()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    lat = data.get("lat")
    lng = data.get("lng")

    # ✅ Validate location
    if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        return jsonify({"error": "Location not selected"}), 400

    # ✅ Check if user already exists
    if users_col.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    # ================= SMART CLUSTER ASSIGNMENT =================

    street_distances = []

    for s in STREETS:
        distance = calculate_distance(lat, lng, s["lat"], s["lng"])
        street_distances.append((s, distance))

    # Sort by nearest to user
    street_distances.sort(key=lambda x: x[1])

    # Get nearest street
    nearest_street = street_distances[0][0]

    # Find streets near that nearest street (within 3km radius)
    cluster = []

    for s in STREETS:
        d = calculate_distance(
            nearest_street["lat"],
            nearest_street["lng"],
            s["lat"],
            s["lng"]
        )
        if d <= 3:
            cluster.append(s["name"])

    # Shuffle cluster to create variation
    random.shuffle(cluster)

    # Assign 5–7 streets (depending on availability)
    assigned_streets = cluster[:7] if len(cluster) >= 7 else cluster

    # ================= SAVE USER =================

    users_col.insert_one({
        "email": email,
        "username": username,
        "password": generate_password_hash(password),
        "lat": lat,
        "lng": lng,
        "assigned_streets": assigned_streets,
        "created_at": datetime.now()
    })

    return jsonify({
        "message": "Signup successful",
        "assigned_streets": assigned_streets
    }), 201
# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    user = users_col.find_one({"email": data.get("email")})

    if not user or not check_password_hash(user["password"], data.get("password")):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_email"] = user["email"]

    return jsonify({
        "message": "Login successful",
        "username": user["username"],
        "assigned_streets": user["assigned_streets"]
    })


# ================= PROFILE DATA =================
@app.route("/profile")
def profile():

    if "user_email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = users_col.find_one(
        {"email": session["user_email"]},
        {"_id": 0}
    )

    # Ensure field exists
    if "assigned_streets" not in user:
        user["assigned_streets"] = []

    return jsonify(user)



@app.route("/update-profile", methods=["POST"])
def update_profile():

    if "user_email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    username = data.get("username")
    phone = data.get("phone")

    users_col.update_one(
        {"email": session["user_email"]},
        {
            "$set": {
                "username": username,
                "phone": phone
            }
        }
    )

    return jsonify({"success": True})
# ================= LIVE DATA (USER-SPECIFIC) =================
from datetime import datetime
import time

@app.route("/live-data")
def live_data():

    global live_cache, last_generated_time

    if "user_email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = users_col.find_one({"email": session["user_email"]})
    assigned_streets = user.get("assigned_streets", [])

    current_time = time.time()

    # ✅ If cache exists and within 2 minutes → return same data
    if last_generated_time and (current_time - last_generated_time < CACHE_DURATION):
        return jsonify(live_cache.get(session["user_email"], []))

    # 🔥 Otherwise generate NEW data
    response = []

    for idx, s in enumerate(STREETS, start=1):

        if s["name"] not in assigned_streets:
            continue

        voltage = round(random.uniform(190, 260), 2)
        current = round(random.uniform(6, 20), 2)
        leakage = round(random.uniform(0, 1.5), 2)
        temp = round(random.uniform(35, 90), 2)

        load_kw = round(voltage * current / 1000, 2)

        if voltage < 190 or voltage > 260 or temp > 80 or leakage > 1.0:
            fault_status = "FAULT"
        elif (190 <= voltage < 200 or
              250 < voltage <= 260 or
              75 < temp <= 80 or
              0.8 < leakage <= 1.0):
            fault_status = "WARNING"
        else:
            fault_status = "NORMAL"

        reason = fault_reason({
            "leakage_current": leakage,
            "temperature_c": temp,
            "voltage": voltage
        })

        response.append({
            "street": s["name"],
            "city": s["city"],
            "lat": s["lat"],
            "lng": s["lng"],
            "line_no": idx,
            "phase": random.choice(PHASES),
            "voltage": voltage,
            "current": current,
            "load_kw": load_kw,
            "fault_status": fault_status,
            "cause": reason["cause"],
            "solution": reason["solution"],
            "action": reason["action"],
            "confidence_percent": random.randint(85, 99)
        })

    # ✅ Save to cache
    live_cache[session["user_email"]] = response
    last_generated_time = current_time

    return jsonify(response)
# ================= RESOLVE ISSUE =================
from datetime import datetime
from flask import request, jsonify, session

@app.route("/resolve", methods=["POST"])
def resolve_issue():

    global live_cache

    if "user_email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = users_col.find_one({"email": session["user_email"]})
    data = request.get_json()

    street_name = data.get("street")
    fault_status = data.get("fault_status")

    # 1️⃣ Insert into reports
    reports_col.insert_one({
        "street": street_name,
        "incident": fault_status,
        "status": "RESOLVED",
        "officer_email": user["email"],
        "officer_name": user["username"],
        "resolved_at": datetime.now()
    })

    # 2️⃣ Update cache (VERY IMPORTANT)
    user_email = session["user_email"]

    if user_email in live_cache:
        for item in live_cache[user_email]:
            if item["street"] == street_name:
                item["fault_status"] = "NORMAL"

    return jsonify({"message": "Issue resolved successfully"})
# ================= USER REPORT DATA =================
@app.route("/report-data")
def report_data():

    if "user_email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    reports = reports_col.find({
        "officer_email": session["user_email"]
    })

    data = []

    for r in reports:
        data.append({
            "date": r.get("resolved_at").strftime("%Y-%m-%d") if r.get("resolved_at") else "-",
            "street": r.get("street", "-"),
            "incident": r.get("incident", "FAULT"),   # ✅ FIXED
            "severity": "HIGH" if r.get("incident") == "FAULT" else "LOW",
            "status": r.get("status", "-"),
            "officer": r.get("officer_name", "-"),
            "response_time": 15   # optional dummy value
        })

    return jsonify(data)


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
