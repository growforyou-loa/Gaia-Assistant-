# 🌙 Gaia Assistant — AIDE Setup Guide

## 📁 Final Project Structure

```
GaiaAssistant/
└── app/
    ├── build.gradle
    ├── src/
    │   └── main/
    │       ├── AndroidManifest.xml
    │       ├── assets/
    │       │   └── index.html          ← Your UI (modified for Android)
    │       ├── java/
    │       │   └── com/gaia/assistant/
    │       │       └── MainActivity.java
    │       └── res/
    │           ├── drawable/
    │           │   └── ic_launcher.png  ← Any PNG icon you want
    │           ├── layout/
    │           │   └── activity_main.xml
    │           ├── values/
    │           │   ├── strings.xml
    │           │   └── styles.xml
    │           └── xml/
    │               ├── network_security_config.xml
    │               ├── searchable.xml
    │               └── assist_config.xml
```

---

## 🔧 Step-by-Step AIDE Setup

### STEP 1 — Create the Project in AIDE

1. Open **AIDE** on your phone
2. Tap **"New Project"**
3. Select **"Android App"**
4. Set:
   - **App Name:** `Gaia`
   - **Package Name:** `com.gaia.assistant`
   - **Min SDK:** `21`
5. Tap **Create**

---

### STEP 2 — Create the `assets` Folder

AIDE does NOT create an assets folder automatically. You must do it manually:

1. In AIDE's file explorer, navigate to: `app/src/main/`
2. Long-press on `main/`
3. Tap **"New Folder"**
4. Type: `assets`
5. Tap OK

---

### STEP 3 — Paste Each File

Open each file in AIDE and **replace the entire contents** with the code provided:

#### `app/src/main/assets/index.html`
- Navigate to `assets/`
- Tap **"New File"** → name it `index.html`
- Paste the full HTML code

#### `app/src/main/java/com/gaia/assistant/MainActivity.java`
- Navigate to the Java file (already exists)
- Open it → **Select All** → delete → paste the new Java code

#### `app/src/main/AndroidManifest.xml`
- Open → **Select All** → delete → paste the new Manifest XML

#### `app/src/main/res/values/styles.xml`
- Open → **Select All** → delete → paste the new styles XML

#### `app/src/main/res/values/strings.xml`
- Open or create → paste the strings XML

#### `app/src/main/res/layout/activity_main.xml`
- Open → **Select All** → delete → paste (just a FrameLayout placeholder)

#### XML files in `app/src/main/res/xml/`
- If the `xml/` folder doesn't exist: long-press `res/` → New Folder → `xml`
- Create these 3 files:
  - `network_security_config.xml`
  - `searchable.xml`
  - `assist_config.xml`
- Paste respective content into each

#### `app/build.gradle`
- Open → **Select All** → delete → paste

---

### STEP 4 — Add an App Icon

1. Find any PNG image (square, at least 48×48 px)
2. Rename it to `ic_launcher.png`
3. Copy it to: `app/src/main/res/drawable/`

If you don't have one, AIDE will use its default icon.

---

### STEP 5 — Build & Run

1. Make sure your phone and the Flask (Termux) server are on the **same WiFi network**
2. Start your Flask backend in Termux:
   ```bash
   python app.py
   ```
3. In AIDE, tap the **▶ Run** (play) button
4. AIDE will compile and install the APK on your device
5. Grant all permission dialogs that appear

---

### STEP 6 — Set Gaia as Default Assistant

This is what makes it launch on **long-press Home**:

1. Go to **Settings → Apps → Default Apps → Digital Assistant**
   (On Samsung: Settings → Advanced Features → Bixby → Default Assistant)
2. Select **"Gaia"** from the list
3. Done ✅

Now **long-press the Home button** to launch Gaia instantly.

---

## 🔌 How the Architecture Works

```
User speaks/types
      ↓
  index.html (UI in WebView)
      ↓
  GaiaBridge.startVoiceInput()   ← JS calls Java
      ↓
  Android SpeechRecognizer       ← Native Android STT
      ↓
  window.onVoiceResult(text)     ← Java calls back to JS
      ↓
  fetch('http://192.168.1.19:5000/chat', { text })  ← HTTP to Flask
      ↓
  Flask response: { action, response, package }
      ↓
  executeAction(data)            ← JS decides what to do
      ↓
  GaiaBridge.openApp(pkg) etc.   ← JS calls Java
      ↓
  Java executes real Android action (open app, call, alarm...)
      ↓
  GaiaBridge.speak(response)     ← Java TTS speaks response
```

---

## ⚠️ Common Issues & Fixes

| Problem | Fix |
|---|---|
| "App not found" for voice | Grant RECORD_AUDIO permission manually in Settings → Apps → Gaia → Permissions |
| Cannot reach Flask | Check both phone & PC are on same WiFi; verify Flask is running with `python app.py` |
| Alarm not setting | Grant SET_ALARM permission; Clock app must be installed |
| Calls not working | Grant CALL_PHONE permission in Settings → Apps → Gaia → Permissions |
| Fonts look different | Normal — Google Fonts may not load on first run without internet |
| "Network error" | Check `network_security_config.xml` has your IP `192.168.1.19` listed |
| AIDE build fails | Make sure package name `com.gaia.assistant` matches exactly in Manifest and Java |

---

## 📡 Flask Backend Expected Response Format

Your Flask `/chat` endpoint should return JSON like this:

```json
{
  "action": "open_app",
  "response": "Opening YouTube for you",
  "package": "com.google.android.youtube"
}
```

```json
{
  "action": "set_alarm",
  "response": "Alarm set for 7 AM",
  "time": "7:00 AM"
}
```

```json
{
  "action": "call",
  "response": "Calling Mom",
  "contact": "Mom"
}
```

```json
{
  "action": "show_text",
  "response": "The capital of France is Paris."
}
```

---

## ✅ Supported Actions (Java Bridge)

| Action value | What Java does |
|---|---|
| `open_app` | Opens app by package name or keyword |
| `call` | Makes phone call |
| `send_sms` | Opens SMS app with contact+body |
| `set_alarm` | Opens Clock with alarm preset |
| `set_timer` | Opens Clock with timer preset |
| `play_music` | Opens music app |
| `open_url` | Opens URL in browser |
| `search` | Google search |
| `navigate` | Google Maps navigation |
| `wifi_on/off` | Toggle WiFi (Android 9 opens settings panel) |
| `bluetooth_on/off` | Toggle Bluetooth |
| `flashlight_on/off` | Torch on/off |
| `volume_up/down` | Adjust media volume |
| `mute/unmute` | Mute/unmute media |
| `silent_mode` | Set phone to silent |
| `vibrate_mode` | Set phone to vibrate |
| `normal_mode` | Set phone to normal |
| `media_play/pause/next/prev` | Control media playback |
| `copy_text` | Copy to clipboard |
| `share` | Android share sheet |
| `battery_status` | Show battery % in toast |

