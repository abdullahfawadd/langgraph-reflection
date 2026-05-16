"""Shared state for the LangGraph Tool Use grade advisor."""

from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages


class ToolUseState(TypedDict):
    """All memory needed for the tool dispatch loop."""

    messages: Annotated[list[Any], add_messages]
    student_id: str
    question: str
    tool_log: list[dict[str, Any]]
    turn_count: int
    final_answer: str
    max_turns: int
