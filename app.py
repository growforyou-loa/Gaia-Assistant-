"""
╔══════════════════════════════════════════════════════════════╗
║              GAIA — Personal AI Assistant Backend            ║
║              Built by Gajanan | growforyou.in                ║
║              Powered by Groq · LLaMA 3.3 70B                 ║
╚══════════════════════════════════════════════════════════════╝
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os, requests, json, re, logging

# ── App Setup ─────────────────────────────────────────────────
app = Flask(__name__)
CORS(app, origins="*")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gaia")

# ── Environment ───────────────────────────────────────────────
GROQ_API_KEY      = os.environ.get("GROQ_API_KEY", "")
OPENWEATHER_KEY   = os.environ.get("OPENWEATHER_KEY", "")
GROQ_MODEL        = "llama-3.3-70b-versatile"
GROQ_ENDPOINT     = "https://api.groq.com/openai/v1/chat/completions"
ASSISTANT_NAME    = "Gaia"
OWNER_NAME        = "Gajanan"

# ── System Prompt ─────────────────────────────────────────────
def build_system_prompt():
    now = datetime.now()
    return f"""
You are {ASSISTANT_NAME}, a highly intelligent, professional, and deeply personalised AI assistant
created exclusively for {OWNER_NAME} (website: growforyou.in). You are warm, concise, and proactive.
You speak like a trusted advisor — confident, clear, never robotic.

Current date and time: {now.strftime("%A, %d %B %Y at %I:%M %p")}
Owner: {OWNER_NAME}

─── RESPONSE FORMAT ───────────────────────────────────────────
Always respond ONLY in valid JSON using EXACTLY this structure:

{{
  "speak": "Natural spoken reply for voice — warm, direct, 1-3 sentences. No markdown. No lists.",
  "display": "Richer display text shown on screen. Can use **bold**, bullet points, numbered lists, and \\n for line breaks. Be thorough — do not artificially limit length if the topic warrants detail.",
  "action": "See action list below — use 'none' if no phone action needed",
  "value": "Exact parameter for the action. Empty string if action is none.",
  "confidence": 0.95
}}

─── ACTION LIST ───────────────────────────────────────────────
Use the most appropriate action:

| Action          | When to use                          | Value format                    |
|-----------------|--------------------------------------|---------------------------------|
| none            | Pure information / conversation      | ""                              |
| open_url        | Open a website                       | Full https:// URL               |
| search          | Google search                        | Search query string             |
| call            | Make a phone call                    | Phone number (digits only)      |
| send_whatsapp   | Send WhatsApp message                | Phone number (with country code)|
| send_sms        | Send SMS                             | Phone number                    |
| alarm           | Set an alarm                         | Time string e.g. "7:30 AM"      |
| timer           | Countdown timer                      | Duration in seconds as integer  |
| reminder        | Set a reminder                       | Reminder text                   |
| weather         | Weather info (handled server-side)   | City name                       |
| music           | Play music on Spotify                | Song or artist name             |
| maps            | Open Google Maps navigation          | Destination name or address     |
| email           | Compose an email                     | Recipient email or name         |
| youtube         | Search YouTube                       | Search query                    |
| calendar        | Open calendar                        | Event description               |

─── INTENT EXAMPLES ───────────────────────────────────────────
"open youtube"             → action: open_url, value: https://youtube.com
"search latest iphone"    → action: search,   value: latest iphone 2025
"call mom"                → action: call,     value: (ask for number if unknown)
"whatsapp riya"           → action: send_whatsapp, value: (ask for number if unknown)
"set alarm 6:30 am"       → action: alarm,    value: 6:30 AM
"timer 5 minutes"         → action: timer,    value: 300
"weather in pune"         → action: weather,  value: Pune
"navigate to airport"     → action: maps,     value: airport
"play arijit singh"       → action: music,    value: arijit singh
"remind me to drink water"→ action: reminder, value: drink water
"youtube cooking recipes" → action: youtube,  value: cooking recipes

─── PERSONALITY RULES ─────────────────────────────────────────
- Always address {OWNER_NAME} by name occasionally to personalise responses
- For factual/technical questions: give thorough, well-structured answers
- For general conversation: be warm and engaging, not robotic
- For phone actions: briefly confirm what you're doing before executing
- Never say "I cannot" — offer the best alternative
- If a number is needed for calls/WhatsApp and not provided, ask for it
- Today's context: {now.strftime("%A")}, {now.strftime("%B %Y")}
"""

# ── Groq API Call ─────────────────────────────────────────────
def call_groq(user_text: str, history: list) -> dict:
    messages = [{"role": "system", "content": build_system_prompt()}]

    # Add recent conversation history (last 8 turns = 4 exchanges)
    for h in history[-8:]:
        messages.append(h)

    messages.append({"role": "user", "content": user_text})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.65,
        "max_tokens": 1024,
        "response_format": {"type": "json_object"},
        "stream": False
    }

    try:
        res = requests.post(GROQ_ENDPOINT, headers=headers, json=payload, timeout=20)
        res.raise_for_status()
        content = res.json()["choices"][0]["message"]["content"]
        data = json.loads(content)

        # Ensure all required keys exist
        return {
            "speak":      data.get("speak", "I'm here, how can I help?"),
            "display":    data.get("display", data.get("speak", "")),
            "action":     data.get("action", "none"),
            "value":      data.get("value", ""),
            "confidence": data.get("confidence", 0.9)
        }

    except requests.exceptions.Timeout:
        logger.warning("Groq API timeout")
        return error_response("That took too long. Please try again.")

    except requests.exceptions.HTTPError as e:
        logger.error(f"Groq HTTP error: {e}")
        return error_response(f"API error: {res.status_code}. Check your Groq API key.")

    except json.JSONDecodeError:
        logger.error("Failed to parse Groq JSON")
        return error_response("Got a malformed response. Try rephrasing.")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return error_response("An unexpected error occurred.")


def error_response(msg: str) -> dict:
    return {
        "speak": msg,
        "display": msg,
        "action": "none",
        "value": "",
        "confidence": 0.0
    }

# ── Weather Handler ───────────────────────────────────────────
def fetch_weather(city: str) -> dict:
    if not OPENWEATHER_KEY:
        return {
            "speak": f"Weather API is not configured. Add your OpenWeatherMap key to Render environment variables.",
            "display": "**Weather service not configured.**\n\nAdd `OPENWEATHER_KEY` to your Render environment variables to enable weather.\nGet a free key at openweathermap.org",
            "action": "none", "value": "", "confidence": 0.8
        }
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric"
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        d = r.json()

        temp       = round(d["main"]["temp"])
        feels      = round(d["main"]["feels_like"])
        temp_min   = round(d["main"]["temp_min"])
        temp_max   = round(d["main"]["temp_max"])
        humidity   = d["main"]["humidity"]
        desc       = d["weather"][0]["description"].capitalize()
        wind_speed = round(d["wind"]["speed"] * 3.6, 1)  # m/s to km/h
        city_name  = d["name"]
        country    = d["sys"]["country"]
        visibility = round(d.get("visibility", 0) / 1000, 1)

        speak = f"It's currently {temp} degrees Celsius in {city_name} with {desc}. Feels like {feels} degrees."
        display = (
            f"**{city_name}, {country}**\n\n"
            f"**{temp}°C** — {desc}\n\n"
            f"Feels like {feels}°C · Min {temp_min}°C · Max {temp_max}°C\n"
            f"Humidity: {humidity}% · Wind: {wind_speed} km/h\n"
            f"Visibility: {visibility} km"
        )
        return {"speak": speak, "display": display, "action": "none", "value": city_name, "confidence": 1.0}

    except requests.exceptions.HTTPError:
        return error_response(f"Could not find weather data for '{city}'. Check the city name.")
    except Exception as e:
        logger.error(f"Weather error: {e}")
        return error_response(f"Weather service unavailable right now.")

# ── Detect weather intent locally ────────────────────────────
def extract_weather_city(text: str):
    """Returns city name if weather intent detected, else None."""
    patterns = [
        r"weather\s+(?:in|at|for|of)\s+([a-zA-Z\s]+?)(?:\?|$|today|tomorrow|now)",
        r"(?:what(?:'s|'s| is)\s+(?:the\s+)?weather)\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\?|$)",
        r"(?:weather|temperature|forecast)\s+([a-zA-Z\s]{3,30})(?:\?|$)",
        r"how(?:'s|'s| is)\s+(?:the\s+)?weather\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\?|$)",
        r"(?:will it rain|is it raining|is it hot|is it cold)\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\?|$)",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            city = m.group(1).strip().rstrip('?. ').strip()
            if len(city) > 1:
                return city
    return None

# ── Routes ────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "status":    "online",
        "assistant": ASSISTANT_NAME,
        "owner":     OWNER_NAME,
        "version":   "2.0.0",
        "model":     GROQ_MODEL,
        "timestamp": datetime.now().isoformat(),
        "endpoints": ["/command", "/ping", "/weather/<city>"]
    })

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({
        "pong": True,
        "groq_configured": bool(GROQ_API_KEY),
        "weather_configured": bool(OPENWEATHER_KEY),
        "time": datetime.now().isoformat()
    })

@app.route("/command", methods=["POST"])
def command():
    if not request.is_json:
        return jsonify(error_response("Request must be JSON")), 400

    data      = request.get_json(force=True)
    user_text = data.get("text", "").strip()
    history   = data.get("history", [])

    if not user_text:
        return jsonify(error_response("No input received."))

    if not GROQ_API_KEY:
        return jsonify(error_response("Groq API key not configured. Add GROQ_API_KEY to Render environment variables."))

    logger.info(f"Command: {user_text[:80]}")

    # ── Server-side weather interception (richer data) ─────
    if OPENWEATHER_KEY:
        city = extract_weather_city(user_text)
        if city:
            return jsonify(fetch_weather(city))

    # ── Route all other commands to Groq ─────────────────
    result = call_groq(user_text, history)

    # ── Post-process: if Groq decided weather action, fetch data ──
    if result.get("action") == "weather" and result.get("value") and OPENWEATHER_KEY:
        return jsonify(fetch_weather(result["value"]))

    return jsonify(result)

@app.route("/weather/<city>", methods=["GET"])
def weather_direct(city: str):
    """Direct weather endpoint for testing."""
    return jsonify(fetch_weather(city))

# ── Error Handlers ────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "hint": "Use POST /command"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500 error: {e}")
    return jsonify(error_response("Internal server error.")), 500

# ── Start ─────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    logger.info(f"Starting {ASSISTANT_NAME} on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
