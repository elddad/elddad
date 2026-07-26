"""The AI brain: Claude, via the Claude Agent SDK, with Jarvis's custom tools."""

import asyncio
from datetime import datetime
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
    tool,
)

from .config import SYSTEM_PROMPT
from .tools.apps import open_app, open_url
from .tools.reminders import ReminderManager
from .tools.weather import get_weather


def _text_result(text: str, is_error: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {"content": [{"type": "text", "text": text}]}
    if is_error:
        result["is_error"] = True
    return result


async def _run_sync(fn, *args) -> str:
    """Run a blocking function (network, subprocess) off the event loop."""
    return await asyncio.get_running_loop().run_in_executor(None, fn, *args)


def _build_tools(reminders: ReminderManager):
    """Create Jarvis's custom tools, bound to this session's reminder manager."""

    @tool("get_weather", "Get the current weather and today's forecast for a city. "
          "Works with city names in any language.", {"city": str})
    async def weather_tool(args: dict[str, Any]) -> dict[str, Any]:
        try:
            return _text_result(await _run_sync(get_weather, args["city"]))
        except Exception as e:
            return _text_result(f"Weather lookup failed: {e}", is_error=True)

    @tool("get_time", "Get the current local date and time.", {})
    async def time_tool(args: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now().astimezone()
        return _text_result(now.strftime("%A, %d %B %Y, %H:%M (%Z)"))

    @tool("set_reminder", "Set a reminder or timer. It will be announced out loud when due. "
          "minutes may be fractional (0.5 = 30 seconds).",
          {"minutes": float, "message": str})
    async def set_reminder_tool(args: dict[str, Any]) -> dict[str, Any]:
        return _text_result(reminders.add(float(args["minutes"]), str(args["message"])))

    @tool("list_reminders", "List all pending reminders.", {})
    async def list_reminders_tool(args: dict[str, Any]) -> dict[str, Any]:
        return _text_result(reminders.list_pending())

    @tool("cancel_reminders", "Cancel all pending reminders.", {})
    async def cancel_reminders_tool(args: dict[str, Any]) -> dict[str, Any]:
        return _text_result(reminders.cancel_all())

    @tool("open_app", "Open an application on the user's computer, e.g. browser, chrome, "
          "calculator, files, terminal, spotify, vscode.", {"name": str})
    async def open_app_tool(args: dict[str, Any]) -> dict[str, Any]:
        return _text_result(await _run_sync(open_app, args["name"]))

    @tool("open_url", "Open a website URL in the user's default browser.", {"url": str})
    async def open_url_tool(args: dict[str, Any]) -> dict[str, Any]:
        return _text_result(await _run_sync(open_url, args["url"]))

    return [
        weather_tool, time_tool,
        set_reminder_tool, list_reminders_tool, cancel_reminders_tool,
        open_app_tool, open_url_tool,
    ]


class JarvisBrain:
    """One long-lived Claude session that remembers the whole conversation."""

    def __init__(self, reminders: ReminderManager):
        jarvis_server = create_sdk_mcp_server(
            name="jarvis",
            version="1.0.0",
            tools=_build_tools(reminders),
        )
        options = ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            mcp_servers={"jarvis": jarvis_server},
            allowed_tools=[
                # Jarvis's own tools
                "mcp__jarvis__get_weather",
                "mcp__jarvis__get_time",
                "mcp__jarvis__set_reminder",
                "mcp__jarvis__list_reminders",
                "mcp__jarvis__cancel_reminders",
                "mcp__jarvis__open_app",
                "mcp__jarvis__open_url",
                # Built-in web tools for "look this up for me"
                "WebSearch",
                "WebFetch",
            ],
            max_turns=15,
        )
        self._client = ClaudeSDKClient(options=options)

    async def __aenter__(self) -> "JarvisBrain":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self._client.__aexit__(*exc_info)

    async def ask(self, user_text: str) -> str:
        """Send one user utterance and return Claude's spoken reply."""
        await self._client.query(user_text)

        text_parts: list[str] = []
        final_result: str | None = None
        async for message in self._client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text_parts.append(block.text)
            elif isinstance(message, ResultMessage):
                if message.subtype == "success" and message.result:
                    final_result = message.result
                break  # response is complete

        if text_parts:
            return text_parts[-1].strip()
        if final_result:
            return final_result.strip()
        return "I'm sorry sir, I didn't manage to produce an answer."
