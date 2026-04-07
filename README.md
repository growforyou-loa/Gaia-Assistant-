# Gaia-Assistant-
### Built by Gajanan | [growforyou.in](https://growforyou.in)

> A sleek, voice-first personal AI assistant with a holographic HUD interface.
> Powered by Groq (LLaMA 3.3 70B) · Deployed free on Render + GitHub Pages.

---

## Project Structure

```
aria-assistant/
├── app.py              ← Flask backend (Groq AI brain)
├── requirements.txt    ← Python dependencies
├── render.yaml         ← Render.com deploy config
├── .env.example        ← Environment variable template
├── .gitignore          ← Ignores .env and cache files
│
├── index.html          ← Full PWA frontend (single file)
├── manifest.json       ← PWA install manifest
├── sw.js               ← Service worker (offline support)
│
└── README.md           ← This file
```

---

## Features

- 🎤 **Voice Input** — Web Speech API (free, browser-native)
- 🔊 **Voice Output** — SpeechSynthesis (realistic, zero cost)
- 🧠 **AI Brain** — Groq LLaMA 3.3 70B (14,400 req/day free)
- ⚡ **Actions** — Open URLs, Search, Call, WhatsApp, Music, Maps, Alarms
- 🌦️ **Weather** — Live weather via OpenWeatherMap (free)
- 📱 **PWA** — Installable on Android/iOS home screen
- 🌐 **Offline Shell** — Service worker caches UI

---

## Step-by-Step Setup

### 1. Get Free API Keys

| Service | URL | Free Tier |
|---|---|---|
| **Groq** | [console.groq.com](https://console.groq.com) | 14,400 req/day |
| **OpenWeatherMap** (optional) | [openweathermap.org/api](https://openweathermap.org/api) | 1,000 calls/day |

### 2. Deploy Backend to Render

1. Push this repo to **GitHub**
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` — click **Deploy**
5. In Render dashboard → **Environment** → add:
   - `GROQ_API_KEY` = your key from console.groq.com
   - `OPENWEATHER_KEY` = your key (optional)
6. Note your Render URL: `https://aria-assistant-api.onrender.com`

### 3. Update Frontend Backend URL

In `index.html`, line ~320:
```javascript
const BACKEND = "https://aria-assistant-api.onrender.com"; // ← your Render URL
```

Also register the service worker by adding before `</body>`:
```html
<script>
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js');
  }
</script>
```

### 4. Deploy Frontend to GitHub Pages

1. In your repo → Settings → Pages
2. Source: **Deploy from branch** → `main` → `/` (root)
3. Your assistant is live at: `https://yourusername.github.io/aria-assistant/`

### 5. Install on Your Phone (Android)

1. Open your GitHub Pages URL in **Chrome**
2. Tap the 3-dot menu → **Add to Home Screen**
3. Tap Install → ARIA icon appears on your home screen ✅

### 6. Install on iPhone (iOS)

1. Open URL in **Safari**
2. Tap Share icon → **Add to Home Screen**
3. Tap Add → ARIA appears on home screen ✅

---

## Supported Voice Commands

| Say | Action |
|---|---|
| "Open YouTube" | Opens YouTube |
| "Search for AI news" | Google search |
| "Call 9876543210" | Phone call |
| "WhatsApp Riya" | Opens WhatsApp |
| "Set alarm for 7 AM" | Alarm intent |
| "Set timer for 5 minutes" | Timer |
| "Weather in Mumbai" | Live weather |
| "Play Arijit Singh" | Spotify search |
| "Navigate to Pune" | Google Maps |
| "What time is it?" | Spoken answer |
| "Tell me a joke" | General AI response |

---

## Customisation

### Rename the assistant
In `app.py`, change:
```python
ASSISTANT_NAME = "ARIA"   # Change to any name
OWNER_NAME     = "Gajanan" # Your name
```

### Add more actions
In `app.py` → `SYSTEM_PROMPT`, extend the intent list.
In `index.html` → `handleAction()`, add new `case` blocks.

### Change voice
In `index.html` → `loadVoices()`, adjust the regex pattern to match a preferred TTS voice name.

---

## Free Stack — Total Cost: ₹0

| Service | Use | Cost |
|---|---|---|
| Groq API | AI brain | Free |
| OpenWeatherMap | Weather | Free |
| Render.com | Backend hosting | Free |
| GitHub Pages | Frontend hosting | Free |
| Web Speech API | Voice in/out | Free |

---

## Credits

Built with ❤️ by **Gajanan**
Website: [growforyou.in](https://growforyou.in)
AI: Groq · LLaMA 3.3 70B by Meta
