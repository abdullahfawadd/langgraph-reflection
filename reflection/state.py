"""Shared state for the LangGraph Reflection agent."""

from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages


class ReflectionState(TypedDict):
    """All shared memory for the FYP feedback reflection graph."""

    messages: Annotated[list[Any], add_messages]
    task: str
    current_draft: str
    critique: str
    reflection_rounds: int
    approved: bool
    max_rounds: int
