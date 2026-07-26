# 🤖 Jarvis — Personal Voice Assistant

A Jarvis-style voice assistant (inspired by Iron Man) powered by **Claude** via the
[Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk). Speak to it in
**English or Hebrew** — it detects the language automatically and answers back
out loud in the same language.

## What it can do

- 🗣️ **Voice conversation** — push-to-talk mic input (Whisper, runs locally and free),
  spoken replies (free Microsoft Edge neural voices, excellent Hebrew support)
- 🧠 **Real conversation memory** — one long-lived Claude session per run
- 🌦️ **Weather** — current conditions + today's forecast for any city (free Open-Meteo API)
- ⏰ **Reminders & timers** — "remind me in 20 minutes to take the pizza out" → it speaks up when due
- 🔎 **Web search** — Claude's built-in WebSearch/WebFetch tools
- 💻 **Computer control** — open apps (browser, Spotify, calculator, VS Code, ...) and websites
- 🇮🇱 **Hebrew** — full support in speech recognition, replies, and text-to-speech

## Requirements

- Python **3.10+**
- A microphone and speakers
- A way to authenticate with Claude (see below)

## Setup

```bash
cd jarvis
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Authentication

The assistant's brain is the Claude Agent SDK, which runs on the same engine as
Claude Code. Two ways to authenticate:

1. **Claude Pro/Max subscription (no API key)** — if you have
   [Claude Code](https://claude.com/claude-code) installed and you've logged in with
   your claude.ai account (`claude` → `/login`), the SDK will typically pick up that
   login automatically on your machine for personal use. Just run Jarvis with no
   `ANTHROPIC_API_KEY` set.
   > Note: the *officially supported* auth for the Agent SDK is an API key —
   > subscription login is intended for Claude Code itself, so this path is
   > "works for personal use" rather than guaranteed.
2. **API key (officially supported)** — create a key at
   [console.anthropic.com](https://console.anthropic.com) and:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."   # Windows: set ANTHROPIC_API_KEY=sk-ant-...
   ```

## Run it

```bash
python main.py            # full voice mode: press Enter to talk, Enter again to stop
python main.py --text     # type instead of speaking (replies still spoken)
python main.py --text --no-tts   # pure text chat, no audio at all
```

Say **"goodbye"** / **"להתראות"** to exit.

### Example things to say

| English | עברית |
|---|---|
| "What's the weather in Tel Aviv?" | "מה מזג האוויר בתל אביב?" |
| "Remind me in 10 minutes to call mom" | "תזכיר לי בעוד 10 דקות להתקשר לאמא" |
| "Open Spotify" | "תפתח ספוטיפיי" |
| "Search the web for tonight's Maccabi game" | "חפש באינטרנט מתי המשחק של מכבי" |
| "What time is it?" | "מה השעה?" |

## Project structure

```
jarvis/
├── main.py                  # entry point + conversation loop
├── requirements.txt
└── assistant/
    ├── config.py            # voices, Whisper model, Jarvis personality prompt
    ├── brain.py             # Claude Agent SDK client + custom tool definitions
    ├── voice/
    │   ├── recorder.py      # push-to-talk microphone recording
    │   ├── stt.py           # speech-to-text (faster-whisper, auto language detect)
    │   └── tts.py           # text-to-speech (edge-tts, Hebrew/English voice picking)
    └── tools/
        ├── weather.py       # Open-Meteo weather (no API key)
        ├── reminders.py     # async reminder scheduler, announces out loud
        └── apps.py          # open apps/URLs on your computer
```

## Customizing

- **Personality** — edit `SYSTEM_PROMPT` in `assistant/config.py`
- **Voices** — change `VOICE_ENGLISH` / `VOICE_HEBREW` in `assistant/config.py`
  (list all available voices with `edge-tts --list-voices`)
- **More apps** — add entries to `_APP_COMMANDS` / `_ALIASES` in `assistant/tools/apps.py`
- **Faster/better speech recognition** — change `WHISPER_MODEL` in `assistant/config.py`
  (`tiny` = fastest, `large-v3` = most accurate; first run downloads the model)

## Troubleshooting

- **No microphone found** — `sounddevice` needs a working input device; check your OS sound settings.
  On Linux you may need `sudo apt install libportaudio2`.
- **Whisper is slow** — switch `WHISPER_MODEL` to `"base"` or `"tiny"`, or install
  CUDA-enabled `ctranslate2` if you have an NVIDIA GPU.
- **Auth errors** — make sure you're either logged into Claude Code on this machine
  or have `ANTHROPIC_API_KEY` exported.
