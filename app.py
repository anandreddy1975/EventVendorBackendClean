from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
from flask_cors import CORS
CORS(app)

# Google Sheet setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open(os.getenv("SHEET_NAME")).sheet1

# Gemini setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route("/")
def home():
    return jsonify({"message": "Event Vendor Backend Running ✅"})

@app.route("/vendors", methods=["GET"])
def get_vendors():
    vendors = [
        {
            "VendorName": "Lakshmi Caterers",
            "Category": "Catering",
            "Area": "Mogiligidda",
            "Phone": "9876543210",
            "AvailableDates": "Nov 10–15",
            "PriceRange": "₹15,000–₹50,000"
        },
        {
            "VendorName": "Sri Venkateswara Decorations",
            "Category": "Decorations",
            "Area": "Hyderabad",
            "Phone": "9988776655",
            "AvailableDates": "Nov 5–20",
            "PriceRange": "₹5,000–₹25,000"
        }
    ]
    return jsonify(vendors)


@app.route("/vendors/filter", methods=["POST"])
def filter_vendors():
    filters = request.json
    category = filters.get("category", "").lower()
    area = filters.get("area", "").lower()
    all_data = sheet.get_all_records()
    result = [v for v in all_data if category in v["Category"].lower() and area in v["Area"].lower()]
    return jsonify(result)

@app.route("/query", methods=["POST"])
def ai_query():
    user_query = request.json.get("query", "")
    prompt = f"User asked: {user_query}. Identify category, area, and date to filter vendor list."
    response = model.generate_content(prompt)
    return jsonify({"suggestion": response.text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
