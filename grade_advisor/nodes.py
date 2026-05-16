"""LLM and tool execution nodes for the Student Grade Advisor graph."""

import json
import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq

from .state import ToolUseState
from .tools import TOOL_BY_NAME, TOOLS

load_dotenv()

GROQ_MODEL = "llama-3.1-8b-instant"

_llm: ChatGroq | None = None


def get_llm() -> ChatGroq:
    """Create the Groq chat model lazily so non-LLM checks can run."""

    global _llm
    if _llm is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing. Rotate the exposed key, add the new "
                "value to .env, and restart the server."
            )
        _llm = ChatGroq(model=GROQ_MODEL, temperature=0.0, api_key=api_key)
    return _llm


ADVISOR_SYSTEM_PROMPT = """
You are an academic grade advisor for Air University students.
You must use tools for factual academic data instead of guessing.

Available data can answer:
- CGPA, credit hours, and academic standing.
- Course grades for a named semester.
- Graduation eligibility and missing requirements.

When a question asks for more than one kind of information, call all relevant
tools before giving the final answer. Keep final answers clear, supportive, and
based only on the tool results.
"""


def llm_node(state: ToolUseState) -> dict:
    """Ask the model to answer or request tools."""

    print(f"  [Advisor LLM] Turn {state['turn_count'] + 1}")
    llm_with_tools = get_llm().bind_tools(TOOLS)
    response: AIMessage = llm_with_tools.invoke(
        [SystemMessage(content=ADVISOR_SYSTEM_PROMPT), *state["messages"]]
    )

    update: dict[str, Any] = {
        "messages": [response],
        "turn_count": state["turn_count"] + 1,
    }
    if not getattr(response, "tool_calls", None):
        update["final_answer"] = response.content
    return update


def _safe_json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False)


def tool_node(state: ToolUseState) -> dict:
    """Execute every tool call requested by the last AI message."""

    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", None) or []
    print(f"  [Advisor Tools] Executing {len(tool_calls)} tool call(s)")

    tool_messages: list[ToolMessage] = []
    new_log: list[dict[str, Any]] = []

    for index, call in enumerate(tool_calls, start=1):
        name = call.get("name", "")
        args = call.get("args", {}) or {}
        tool_call_id = call.get("id") or f"manual_tool_call_{index}"
        tool_item = TOOL_BY_NAME.get(name)

        if tool_item is None:
            result: Any = {"error": f"Unknown tool requested: {name}"}
        else:
            try:
                result = tool_item.invoke(args)
            except Exception as exc:  # Keep the graph alive for bad tool args.
                result = {"error": f"{type(exc).__name__}: {exc}"}

        tool_messages.append(
            ToolMessage(
                content=_safe_json(result),
                name=name or "unknown_tool",
                tool_call_id=tool_call_id,
            )
        )
        new_log.append(
            {
                "tool": name or "unknown_tool",
                "arguments": args,
                "result": result,
            }
        )

    return {
        "messages": tool_messages,
        "tool_log": [*state.get("tool_log", []), *new_log],
    }
