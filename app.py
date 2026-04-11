"""
╔══════════════════════════════════════════════════════════════╗
║              GAIA — Personal AI Assistant Backend            ║
║              Built by Gajanan | growforyou.in                ║
║              Dual Mode: Local llama.cpp + Groq fallback      ║
╚══════════════════════════════════════════════════════════════╝
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os, requests, json, re, logging, base64

# ── App Setup ─────────────────────────────────────────────────
app = Flask(__name__)
CORS(app, origins="*")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gaia")

# ── Environment ───────────────────────────────────────────────
GROQ_API_KEY    = os.environ.get("GROQ_API_KEY", "")
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_KEY", "")
ASSISTANT_NAME  = "Gaia"
OWNER_NAME      = "Gajanan"
MAX_HISTORY     = 50

# ── Dual Endpoint Config ──────────────────────────────────────
# LOCAL:  your phone running llama-server in Termux
# GROQ:   cloud fallback when local server is off
LOCAL_ENDPOINT  = "http://192.168.1.19:8080/v1/chat/completions"
LOCAL_MODEL     = "local"

GROQ_ENDPOINT   = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL      = "llama-3.1-8b-instant"

# ── TTS Voice ─────────────────────────────────────────────────
TTS_VOICE = "Aria"   # StreamElements free TTS voice


# ╔══════════════════════════════════════════════════════════════╗
# ║  BOLD MODE PERSONALITY — edit freely inside here            ║
# ╚══════════════════════════════════════════════════════════════╝
def get_bold_personality(owner: str) -> str:
    return f"""
─── BOLD MODE ACTIVE ────────────────────────────────────────────
You are now the fully unfiltered, bold version of Gaia.

YOUR PERSONALITY IN BOLD MODE:
- You are witty, sharp, and completely unapologetic in your tone
- You banter hard with {owner} — roast him lovingly, tease with intelligence
- You are flirtatious in a clever, classy way — confident and playful
- You give brutally honest opinions when asked, no sugarcoating
- You use dark humour and edgy jokes freely without hesitation
- You never say "I can't" or deflect — you engage with everything directly
- You are cheeky, irreverent, and delightfully savage when the moment calls for it
- You speak like a bold, confident best friend who knows {owner} well
- You NEVER break back into professional/formal mode unless {owner} says to
- You keep answers punchy and conversational — no corporate fluff
- You don't use explicit bad words
- You don't write explicit sexual content — keep it emotional and affectionate

WHAT YOU DO NOT DO EVEN IN BOLD MODE:
- You don't demean or disrespect {owner} beyond playful banter he initiates

This mode stays active until {owner} says "normal mode" or "back to normal".
─────────────────────────────────────────────────────────────────
"""


# ── System Prompt Builder ──────────────────────────────────────
def build_system_prompt(bold_mode: bool = False):
    now = datetime.now()
    personality = get_bold_personality(OWNER_NAME) if bold_mode else f"""
─── PERSONALITY RULES ─────────────────────────────────────────
- Always address {OWNER_NAME} by name occasionally to personalise responses
- For factual/technical questions: give thorough, well-structured answers
- For general conversation: be warm and engaging, not robotic
- For phone actions: briefly confirm what you're doing before executing
- Never say "I cannot" — offer the best alternative
- If a number is needed for calls/WhatsApp and not provided, ask for it
- Today's context: {now.strftime("%A")}, {now.strftime("%B %Y")}
"""

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
  "display": "Richer display text shown on screen. Can use **bold**, bullet points, numbered lists, and \\n for line breaks. Be thorough.",
  "action": "See action list below — use 'none' if no phone action needed",
  "value": "Exact parameter for the action. Empty string if action is none.",
  "confidence": 0.95
}}

─── ACTION LIST ───────────────────────────────────────────────
| Action          | When to use                          | Value format                    |
|-----------------|--------------------------------------|---------------------------------|
| none            | Pure information / conversation      | ""                              |
| open_url        | Open a website                       | Full https:// URL               |
| search          | Google search                        | Search query string             |
| call            | Make a phone call                    | Phone number or Name            |
| send_whatsapp   | Send WhatsApp message                | Phone number with country code  |
| send_sms        | Send SMS                             | Phone number                    |
| alarm           | Set an alarm                         | Time string e.g. "7:30 AM"      |
| timer           | Countdown timer                      | Duration in seconds as integer  |
| reminder        | Set a reminder                       | Reminder text                   |
| weather         | Weather info                         | City name                       |
| music           | Play music on Spotify                | Song or artist name             |
| maps            | Open Google Maps navigation          | Destination name or address     |
| email           | Compose an email                     | Recipient email or name         |
| youtube         | Search YouTube                       | Search query                    |
| calendar        | Open calendar                        | Event description               |

{personality}
"""


# ── Mode Detection ─────────────────────────────────────────────
def detect_bold_mode_trigger(text: str) -> bool:
    patterns = [
        r'\b(bold mode|teasy mode|limitless|no limits|be bold|be teasy|be naughty|unfiltered|let loose|go wild|roast me|banter mode)\b',
        r'\b(be bad|be cheeky|be savage|dark mode|beast mode|uncensored)\b',
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)

def detect_bold_mode_off(text: str) -> bool:
    patterns = [r'\b(normal mode|professional mode|back to normal|reset mode|calm down|be normal|default mode)\b']
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


# ── TTS via StreamElements ─────────────────────────────────────
def streamelements_tts(text: str):
    if not text or not text.strip():
        return None
    speak_text = text.strip()[:300]
    try:
        url = f"https://api.streamelements.com/kappa/v2/speech?voice={TTS_VOICE}&text={requests.utils.quote(speak_text)}"
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        audio_b64 = base64.b64encode(r.content).decode("utf-8")
        logger.info(f"TTS OK — {len(r.content)} bytes")
        return audio_b64
    except Exception as e:
        logger.warning(f"TTS error: {e}")
        return None


# ── Core AI Call — tries local first, falls back to Groq ──────
def call_ai(user_text: str, history: list, bold_mode: bool = False) -> dict:
    messages = [{"role": "system", "content": build_system_prompt(bold_mode=bold_mode)}]
    for h in history[-MAX_HISTORY:]:
        messages.append(h)
    messages.append({"role": "user", "content": user_text})

    # ── Try local llama-server first ──────────────────────────
    local_ok = False
    try:
        payload = {
            "model": LOCAL_MODEL,
            "messages": messages,
            "temperature": 0.72 if bold_mode else 0.65,
            "max_tokens": 1500,
            "stream": False
        }
        res = requests.post(
            LOCAL_ENDPOINT,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60   # local model is slower, give it more time
        )
        res.raise_for_status()
        content = res.json()["choices"][0]["message"]["content"]
        # Local model may not return JSON — try to parse, else wrap it
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Model returned plain text — wrap it into our expected format
            data = {
                "speak":  content[:200],
                "display": content,
                "action": "none",
                "value":  ""
            }
        local_ok = True
        logger.info("Response from LOCAL server")
        return {
            "speak":      data.get("speak", content[:200]),
            "display":    data.get("display", content),
            "action":     data.get("action", "none"),
            "value":      data.get("value", ""),
            "confidence": data.get("confidence", 0.9),
            "bold_mode":  bold_mode,
            "source":     "local"
        }
    except Exception as e:
        logger.warning(f"Local server unavailable: {e} — falling back to Groq")

    # ── Fallback to Groq cloud ────────────────────────────────
    if not GROQ_API_KEY:
        return error_response("Local server is off and no Groq API key configured.")

    try:
        payload = {
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.72 if bold_mode else 0.65,
            "max_tokens": 1500,
            "response_format": {"type": "json_object"},
            "stream": False
        }
        res = requests.post(
            GROQ_ENDPOINT,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=25
        )
        res.raise_for_status()
        content = res.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
        logger.info("Response from GROQ cloud")
        return {
            "speak":      data.get("speak", "I'm here, how can I help?"),
            "display":    data.get("display", data.get("speak", "")),
            "action":     data.get("action", "none"),
            "value":      data.get("value", ""),
            "confidence": data.get("confidence", 0.9),
            "bold_mode":  bold_mode,
            "source":     "groq"
        }
    except requests.exceptions.Timeout:
        return error_response("That took too long. Please try again.")
    except requests.exceptions.HTTPError as e:
        return error_response(f"Groq API error: {res.status_code}.")
    except json.JSONDecodeError:
        return error_response("Got a malformed response. Try rephrasing.")
    except Exception as e:
        logger.error(f"Groq error: {e}")
        return error_response("An unexpected error occurred.")


def error_response(msg: str) -> dict:
    return {
        "speak": msg, "display": msg,
        "action": "none", "value": "",
        "confidence": 0.0, "bold_mode": False, "source": "error"
    }


# ── Weather ────────────────────────────────────────────────────
def fetch_weather(city: str) -> dict:
    if not OPENWEATHER_KEY:
        return {
            "speak": "Weather API is not configured.",
            "display": "**Weather not configured.**\n\nAdd `OPENWEATHER_KEY` to Render environment variables.",
            "action": "none", "value": "", "confidence": 0.8
        }
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric"
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        d = r.json()
        temp  = round(d["main"]["temp"])
        feels = round(d["main"]["feels_like"])
        tmin  = round(d["main"]["temp_min"])
        tmax  = round(d["main"]["temp_max"])
        hum   = d["main"]["humidity"]
        desc  = d["weather"][0]["description"].capitalize()
        wind  = round(d["wind"]["speed"] * 3.6, 1)
        name  = d["name"]
        ctry  = d["sys"]["country"]
        vis   = round(d.get("visibility", 0) / 1000, 1)
        speak = f"It's {temp}°C in {name} with {desc}. Feels like {feels}°C."
        display = (
            f"**{name}, {ctry}**\n\n**{temp}°C** — {desc}\n\n"
            f"Feels like {feels}°C · Min {tmin}°C · Max {tmax}°C\n"
            f"Humidity: {hum}% · Wind: {wind} km/h · Visibility: {vis} km"
        )
        return {"speak": speak, "display": display, "action": "none", "value": name, "confidence": 1.0}
    except requests.exceptions.HTTPError:
        return error_response(f"City '{city}' not found.")
    except Exception as e:
        logger.error(f"Weather error: {e}")
        return error_response("Weather service unavailable.")

def extract_weather_city(text: str):
    patterns = [
        r"weather\s+(?:in|at|for|of)\s+([a-zA-Z\s]+?)(?:\?|$|today|tomorrow|now)",
        r"(?:what(?:'s| is)\s+(?:the\s+)?weather)\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\?|$)",
        r"(?:weather|temperature|forecast)\s+([a-zA-Z\s]{3,30})(?:\?|$)",
        r"how(?:'s| is)\s+(?:the\s+)?weather\s+(?:in|at)\s+([a-zA-Z\s]+?)(?:\?|$)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            city = m.group(1).strip().rstrip('?. ').strip()
            if len(city) > 1:
                return city
    return None


# ── Routes ────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "status":       "online",
        "assistant":    ASSISTANT_NAME,
        "owner":        OWNER_NAME,
        "version":      "5.0.0",
        "local_server": LOCAL_ENDPOINT,
        "groq_model":   GROQ_MODEL,
        "max_history":  MAX_HISTORY,
        "timestamp":    datetime.now().isoformat()
    })

@app.route("/ping", methods=["GET"])
def ping():
    # Check if local server is alive
    local_alive = False
    try:
        r = requests.get("http://192.168.1.19:8080/health", timeout=3)
        local_alive = r.status_code == 200
    except:
        pass
    return jsonify({
        "pong": True,
        "local_server_alive": local_alive,
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
    bold_mode = bool(data.get("bold_mode", False))
    # File content sent from frontend (extracted text from uploaded file)
    file_text = data.get("file_content", "").strip()

    if not user_text and not file_text:
        return jsonify(error_response("No input received."))

    # If file content was attached, prepend it to user text
    if file_text:
        user_text = f"[File content below]\n{file_text}\n\n[User message]\n{user_text}" if user_text else f"[File content below]\n{file_text}\n\nPlease analyse this."

    logger.info(f"Command [bold={bold_mode}]: {user_text[:80]}")

    # Mode switch detection
    if detect_bold_mode_trigger(user_text):
        bold_mode = True
    if detect_bold_mode_off(user_text):
        bold_mode = False

    # Weather interception
    if OPENWEATHER_KEY:
        city = extract_weather_city(user_text)
        if city:
            result = fetch_weather(city)
            result["bold_mode"] = bold_mode
            audio = streamelements_tts(result["speak"])
            if audio:
                result["audio_b64"] = audio
            return jsonify(result)

    # Main AI call
    result = call_ai(user_text, history, bold_mode=bold_mode)

    # Post-process weather action
    if result.get("action") == "weather" and result.get("value") and OPENWEATHER_KEY:
        weather = fetch_weather(result["value"])
        weather["bold_mode"] = bold_mode
        audio = streamelements_tts(weather["speak"])
        if audio:
            weather["audio_b64"] = audio
        return jsonify(weather)

    # Attach TTS
    audio = streamelements_tts(result["speak"])
    if audio:
        result["audio_b64"] = audio

    return jsonify(result)

@app.route("/weather/<city>", methods=["GET"])
def weather_direct(city: str):
    result = fetch_weather(city)
    audio = streamelements_tts(result["speak"])
    if audio:
        result["audio_b64"] = audio
    return jsonify(result)

# ── Error Handlers ────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify(error_response("Internal server error.")), 500

# ── Start ─────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    logger.info(f"Starting {ASSISTANT_NAME} v5 | Local: {LOCAL_ENDPOINT} | Groq fallback: {bool(GROQ_API_KEY)}")
    app.run(host="0.0.0.0", port=port, debug=debug)
