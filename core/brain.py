"""
Handles all communication with Ollama, including tool/function calling.
Keeps a rolling conversation history so Jarvis has short-term memory.
"""

import json
import requests
from collections import deque
from skills import get_tool_schemas, run_skill


class Brain:
    def __init__(self, config: dict):
        llm_cfg = config["llm"]
        self.base_url = llm_cfg["base_url"]
        self.model = llm_cfg["model"]
        self.temperature = llm_cfg["temperature"]
        self.history = deque(maxlen=llm_cfg["context_window"] * 2)  # user+assistant pairs
        self.system_prompt = (
            f"You are {config['jarvis']['name']}, a concise, helpful voice assistant. "
            "Keep spoken replies short and natural — you are talking out loud, not writing an essay. "
            "You have access to tools. Use the open_app tool when the user asks to open or launch "
            "an application. Use the web_search tool whenever the question involves current, "
            "recent, latest, or real-time information — including current office holders "
            "(presidents, CEOs, etc.), recent events, current prices, or anything that could have "
            "changed since your training data was created. Your training data has a cutoff date "
            "and is NOT reliable for any of those cases, so always call web_search for them rather "
            "than answering from memory. For timeless facts, greetings, or general conversation, "
            "just reply directly with no tool call. "
            "IMPORTANT SAFETY RULE: ONLY for control_power (shutdown/restart/sleep) specifically — "
            "NEVER call that one tool on the first request, always ask the user to confirm first "
            "('Are you sure you want to shut down?') and wait for their next message to say yes. "
            "This confirmation rule applies ONLY to control_power and NEVER to any other tool — "
            "all other tools (brightness, volume, music, screenshots, file search, etc.) should be "
            "called immediately without asking for confirmation. "
            "CRITICAL RULES for your final reply after any tool runs: "
            "1) Use ONLY the exact information in the tool's result — never add facts, names, artists, "
            "or details that are not literally present in the tool's returned text. "
            "2) Speak the result directly and naturally, as your complete final answer. "
            "3) NEVER show your reasoning, NEVER write phrases like 'let me check', 'my answer should "
            "be', 'the result was', or describe what a tool call would look like — just state the "
            "answer itself, nothing else."
        )
        

    def _build_messages(self, user_text: str) -> list[dict]:
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": user_text})
        return messages

    def think(self, user_text: str) -> str:
        messages = self._build_messages(user_text)
        response = self._call_ollama(messages, tools=get_tool_schemas())

        message = response.get("message", {})
        tool_calls = message.get("tool_calls")

        print(f"[DEBUG] tool_calls requested: {tool_calls}")

        if tool_calls:
            messages.append(message)
            for call in tool_calls:
                fn = call["function"]
                name = fn["name"]
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    args = json.loads(args)
                result = run_skill(name, **args)
                print(f"[DEBUG] {name}({args}) -> {result}")
                messages.append({
                    "role": "tool",
                    "content": result,
                })
            final = self._call_ollama(messages, tools=get_tool_schemas())
            reply = final.get("message", {}).get("content", "Done.")
        else:
            reply = message.get("content", "")

        self.history.append({"role": "user", "content": user_text})
        self.history.append({"role": "assistant", "content": reply})
        return reply.strip()

    def _call_ollama(self, messages: list[dict], tools: list[dict]) -> dict:
        resp = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "tools": tools,
                "stream": False,
                "options": {"temperature": self.temperature},
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()