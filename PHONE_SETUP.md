# GAIA — Full Phone Setup Guide After Render Deploy
### Built by Gajanan | growforyou.in

---

## Step 1 — After Render Deploy: Update Your Backend URL

After Render gives you a URL like `https://gaia-assistant-api.onrender.com`,
open `index.html` and find this line near the top of the `<script>` section:

```javascript
const CFG = {
  backend: 'https://your-gaia-api.onrender.com', // ← Replace this
  ...
};
```

Replace it with your actual Render URL. Then commit and push to GitHub —
GitHub Pages will auto-redeploy.

---

## Step 2 — Install Gaia as a Phone App (PWA)

### Android (Chrome) — Recommended
1. Open your GitHub Pages URL in **Chrome**
2. Wait for the page to fully load
3. Tap the **3-dot menu (⋮)** in the top right
4. Tap **"Add to Home screen"**
5. Tap **"Add"** on the confirmation dialog
6. Gaia icon now appears on your home screen like a native app

### iPhone / iPad (Safari)
1. Open your GitHub Pages URL in **Safari** (must be Safari, not Chrome)
2. Tap the **Share button** (box with arrow pointing up)
3. Scroll down and tap **"Add to Home Screen"**
4. Tap **"Add"** in the top right
5. Gaia appears on your home screen

---

## Step 3 — Grant Microphone Permission

When you first tap the mic button inside Gaia:
- **Android**: Chrome will ask "Allow Gaia to use your microphone?" → Tap **Allow**
- **iPhone**: Safari will ask for mic access → Tap **Allow**

If you accidentally denied it:
- **Android**: Chrome Settings → Site settings → Microphone → Find your site → Allow
- **iPhone**: Settings app → Safari → Microphone → Allow

---

## Step 4 — Phone Action Deep Links (How They Work)

Gaia uses native URI schemes and Android Intents to trigger phone apps directly.

| What You Say | What Triggers |
|---|---|
| "Call 9876543210" | Opens native phone dialer with number pre-filled |
| "WhatsApp Riya" / "WhatsApp 91XXXXXXXXXX" | Opens WhatsApp chat |
| "SMS 9876543210" | Opens native SMS app with number |
| "Navigate to Mumbai" | Opens Google Maps with destination |
| "Play Arijit Singh" | Opens Spotify search |
| "Open YouTube" | Opens YouTube |
| "Set alarm 7 AM" | Sends Android clock intent (Android only) |
| "Email someone@gmail.com" | Opens your default email app |

### Important: Actions That Work on Android vs iOS

| Action | Android | iPhone |
|---|---|---|
| Phone call | Native dialer opens | Native dialer opens |
| WhatsApp | Opens app directly | Opens app directly |
| SMS | Native SMS opens | Native SMS opens |
| Google Maps | Maps app opens | Maps app opens |
| Set alarm (intent) | Clock app opens automatically | Shows toast only — iOS doesn't allow alarm intents |
| Email | Default email app opens | Mail app opens |
| Spotify | Spotify app opens if installed | Spotify app opens if installed |

### iOS Alarm Limitation
iOS does not allow web apps to set alarms programmatically. When you say "Set alarm",
Gaia will tell you the time verbally and show a toast notification.
To work around this, you can use Siri Shortcuts or manually set it in the Clock app.

---

## Step 5 — Enable Notifications (Optional)

To allow Gaia to send reminder notifications:

1. After opening Gaia in Chrome on Android, you may see "Enable notifications" prompt
2. Tap **Allow**
3. Notifications work for reminders and timers when the app is in background

---

## Step 6 — Keep the Backend Alive (Render Free Tier)

Render's free tier spins down after 15 minutes of inactivity, causing a ~30 second
delay on the first request after idle. To avoid this:

**Option A — UptimeRobot (Free)**
1. Go to uptimerobot.com → Create free account
2. Add new monitor: HTTP monitor
3. URL: `https://your-gaia-api.onrender.com/ping`
4. Interval: Every 5 minutes
5. This keeps Render awake 24/7

**Option B — Upgrade Render**
Render's $7/month plan keeps the service always-on with no cold starts.

---

## Step 7 — Weather Setup (Optional but Recommended)

1. Go to openweathermap.org → Sign up free
2. Go to API Keys section → Copy your key
3. In Render dashboard → Your service → Environment
4. Add variable: `OPENWEATHER_KEY` = your key
5. Trigger a redeploy (Render dashboard → Manual Deploy)
6. Now say "Weather in Mumbai" and Gaia returns live data

---

## Troubleshooting

**Gaia doesn't respond:**
- Check Render dashboard — is the service running?
- Open `https://your-render-url.onrender.com/ping` in browser — should return JSON
- Check that `CFG.backend` in index.html matches your Render URL exactly
- Wait 30 seconds if Render is cold-starting

**Voice input doesn't work:**
- Must use HTTPS (GitHub Pages uses HTTPS by default — you're fine)
- Must be Chrome on Android or Safari on iPhone
- Check microphone permission is granted

**Calls/WhatsApp don't open:**
- Make sure you're using Gaia from the installed PWA (home screen icon)
- Make sure WhatsApp/Phone is installed on your device
- For calls: include the full number like "call 9199XXXXXXXX"
- For WhatsApp: include country code "whatsapp 919199XXXXXXXX"

**Alarm intent not working on Android:**
- Make sure Google Clock is your default clock app
- The intent targets `com.google.android.deskclock`
- If you use a different clock app, the intent may not fire
- Alternative: Say "set alarm" and manually confirm in your clock app

---

## File Structure

```
gaia-assistant/
├── app.py              ← Flask backend (Groq AI, weather, intent routing)
├── requirements.txt    ← Python dependencies
├── render.yaml         ← Render deploy config
├── .env.example        ← Environment variables template
├── .gitignore          ← Prevents .env commit
│
├── index.html          ← Full PWA frontend (single file, production-grade)
├── manifest.json       ← PWA install manifest
├── sw.js               ← Service worker (offline shell)
│
└── PHONE_SETUP.md      ← This file
```

---

## Free Infrastructure Stack

| Service | Purpose | Cost |
|---|---|---|
| Groq API | LLaMA 3.3 70B AI brain | Free (14,400 req/day) |
| OpenWeatherMap | Live weather data | Free (1,000 calls/day) |
| Render.com | Backend hosting | Free tier |
| GitHub Pages | Frontend hosting | Free |
| Web Speech API | Voice input (STT) | Free (browser built-in) |
| SpeechSynthesis API | Voice output (TTS) | Free (browser built-in) |
| UptimeRobot | Keep Render awake | Free |

**Total monthly cost: ₹0**
