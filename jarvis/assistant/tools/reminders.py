"""In-session reminders and timers. Fires by speaking out loud."""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Awaitable, Callable

SpeakFn = Callable[[str], Awaitable[None]]


@dataclass
class Reminder:
    message: str
    due_at: float
    task: asyncio.Task = field(repr=False, default=None)


class ReminderManager:
    """Schedules reminders on the running event loop and announces them via TTS."""

    def __init__(self, speak: SpeakFn):
        self._speak = speak
        self._reminders: list[Reminder] = []

    def add(self, minutes: float, message: str) -> str:
        if minutes <= 0:
            return "Reminder time must be in the future."
        reminder = Reminder(message=message, due_at=time.time() + minutes * 60)
        reminder.task = asyncio.get_running_loop().create_task(self._fire(reminder, minutes * 60))
        self._reminders.append(reminder)
        return f"Reminder set for {int(minutes)} minute(s) from now: {message}"

    async def _fire(self, reminder: Reminder, delay: float) -> None:
        await asyncio.sleep(delay)
        print(f"\n⏰ REMINDER: {reminder.message}")
        await self._speak(reminder.message)
        if reminder in self._reminders:
            self._reminders.remove(reminder)

    def list_pending(self) -> str:
        pending = [r for r in self._reminders if r.due_at > time.time()]
        if not pending:
            return "No pending reminders."
        lines = []
        for r in sorted(pending, key=lambda r: r.due_at):
            mins = max(0, round((r.due_at - time.time()) / 60))
            lines.append(f"- in about {mins} minute(s): {r.message}")
        return "Pending reminders:\n" + "\n".join(lines)

    def cancel_all(self) -> str:
        count = len(self._reminders)
        for r in self._reminders:
            if r.task:
                r.task.cancel()
        self._reminders.clear()
        return f"Cancelled {count} reminder(s)."
