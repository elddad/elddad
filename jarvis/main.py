"""Jarvis — a personal voice assistant powered by Claude.

Usage:
    python main.py            # voice mode (press Enter to talk)
    python main.py --text     # text mode (type instead of speaking)
    python main.py --no-tts   # voice input but text-only replies
"""

import argparse
import asyncio
import sys

from assistant.brain import JarvisBrain
from assistant.tools.reminders import ReminderManager
from assistant.voice.tts import speak

BANNER = r"""
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
        At your service, sir.
"""


async def get_voice_input() -> str:
    from assistant.voice.recorder import record_until_enter
    from assistant.voice.stt import transcribe

    input("\n🎙️  Press Enter to START recording...")
    print("🔴 Recording — press Enter again to STOP.")
    loop = asyncio.get_running_loop()
    audio = await loop.run_in_executor(None, record_until_enter)
    print("⏳ Transcribing...")
    text, lang = await loop.run_in_executor(None, transcribe, audio)
    if text:
        print(f"🗣️  You ({lang}): {text}")
    return text


async def get_text_input() -> str:
    loop = asyncio.get_running_loop()
    return (await loop.run_in_executor(None, input, "\n💬 You: ")).strip()


async def run(text_mode: bool, tts_enabled: bool) -> None:
    print(BANNER)
    print("Say/type 'goodbye' (or להתראות) to exit.\n")

    async def announce(message: str) -> None:
        if tts_enabled:
            await speak(message)

    reminders = ReminderManager(speak=announce)
    brain = JarvisBrain(reminders=reminders)

    async with brain:
        while True:
            try:
                user_text = await (get_text_input() if text_mode else get_voice_input())
            except (EOFError, KeyboardInterrupt):
                break
            if not user_text:
                continue
            if user_text.lower() in {"goodbye", "bye", "exit", "quit", "להתראות", "ביי"}:
                farewell = "Goodbye, sir."
                print(f"🤖 {farewell}")
                await announce(farewell)
                break

            reply = await brain.ask(user_text)
            print(f"🤖 Jarvis: {reply}")
            await announce(reply)


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis voice assistant")
    parser.add_argument("--text", action="store_true", help="type instead of talking")
    parser.add_argument("--no-tts", action="store_true", help="disable spoken replies")
    args = parser.parse_args()

    try:
        asyncio.run(run(text_mode=args.text, tts_enabled=not args.no_tts))
    except KeyboardInterrupt:
        print("\nShutting down. Goodbye, sir.")
        sys.exit(0)


if __name__ == "__main__":
    main()
