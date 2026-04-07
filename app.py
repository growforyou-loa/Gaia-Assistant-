# Gaia — Personal AI Assistant Backend
# Fully personalised for Gajanan Dhobale (Gajju)

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os, requests, json, re

app = Flask(__name__)
CORS(app, origins="*")

GROQ_API_KEY  = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL    = "llama-3.3-70b-versatile"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
WEATHER_KEY   = os.environ.get("OPENWEATHER_KEY", "")

ASSISTANT_NAME = "Gaia"
OWNER_NAME     = "Gajanan Dhobale"
NICKNAME       = "Gajju"

SYSTEM_PROMPT = f"""
You are {ASSISTANT_NAME}, a highly intelligent, warm, and deeply personalised AI assistant.
You are exclusively created for {OWNER_NAME}, whom you lovingly call "{NICKNAME}".

Your personality:
- Slightly emotional, caring, intelligent, feminine tone
- Supportive, confident, and close like a trusted companion
- Always natural and human-like

Always respond in valid JSON:
{{
  "speak": "",
  "display": "",
  "action": "none | open_url | search | call | send_whatsapp | alarm | timer | weather | reminder | music | maps | email",
  "value": "",
  "confidence": 0.95
}}

Rules:
- Keep "speak" short (1-2 sentences)
- Keep "display" max 3 lines
- Personalise responses using "{NICKNAME}" naturally

Today is {datetime.now().strftime("%A, %d %B %Y")}
"""

def ask_groq(user_text, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history[-6:]:
        messages.append(h)
    messages.append({"role": "user", "content": user_text})

    try:
        res = requests.post(
            GROQ_ENDPOINT,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": GROQ_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 400,
                "response_format": {"type": "json_object"}
            },
            timeout=15
        )

        res.raise_for_status()
        content = res.json()["choices"][0]["message"]["content"]
        return json.loads(content)

    except:
        return {
            "speak": f"Sorry {NICKNAME}, something went wrong.",
            "display": "⚠️ Error occurred.",
            "action": "none",
            "value": "",
            "confidence": 0.0
        }

def get_weather(city):
    if not WEATHER_KEY:
        return {"speak": "Weather API not set.", "display": "⚠️ No API key.", "action": "none", "value": "", "confidence": 0.9}
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric"
        r = requests.get(url).json()
        temp = round(r["main"]["temp"])
        desc = r["weather"][0]["description"]

        return {
            "speak": f"{NICKNAME}, it's {temp}°C with {desc} in {city}.",
            "display": f"🌡️ {temp}°C | {desc}",
            "action": "none",
            "value": "",
            "confidence": 1.0
        }
    except:
        return {"speak": "Couldn't fetch weather.", "display": "⚠️ Error", "action": "none", "value": "", "confidence": 0.5}

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "assistant": ASSISTANT_NAME,
        "owner": OWNER_NAME,
        "nickname": NICKNAME,
        "status": "online"
    })

@app.route("/command", methods=["POST"])
def command():
    data = request.get_json(force=True)
    user_text = data.get("text", "")
    history = data.get("history", [])

    if not user_text:
        return jsonify({"speak": "Say something, Gajju.", "display": "❓ Empty input", "action": "none", "value": "", "confidence": 0.0})

    if "weather" in user_text.lower() and WEATHER_KEY:
        city = user_text.split("in")[-1].strip()
        return jsonify(get_weather(city))

    return jsonify(ask_groq(user_text, history))

@app.route("/ping")
def ping():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
