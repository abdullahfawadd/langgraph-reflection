"""Graph assembly and runner for the Student Grade Advisor."""

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from .nodes import llm_node, tool_node
from .state import ToolUseState

MAX_TURNS = 6


def should_use_tools(state: ToolUseState) -> str:
    """Route to tools when the latest AI message requested tool calls."""

    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", None) or []

    if tool_calls and state["turn_count"] < state.get("max_turns", MAX_TURNS):
        print(f"  [Advisor Router] Routing to tools ({len(tool_calls)} call(s))")
        return "use_tools"

    if tool_calls:
        print("  [Advisor Router] Max turns reached; ending dispatch loop")
    else:
        print("  [Advisor Router] No tool calls; ending")
    return "done"


def build_advisor_graph():
    """Build START -> llm -> tools -> llm until no tool calls remain."""

    graph = StateGraph(ToolUseState)
    graph.add_node("llm", llm_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("llm")
    graph.add_conditional_edges(
        "llm",
        should_use_tools,
        {
            "use_tools": "tools",
            "done": END,
        },
    )
    graph.add_edge("tools", "llm")
    return graph.compile()


advisor_app = build_advisor_graph()


def initial_advisor_state(
    student_id: str, question: str, max_turns: int = MAX_TURNS
) -> ToolUseState:
    """Create the initial tool-use graph state."""

    return {
        "messages": [
            HumanMessage(
                content=(
                    f"Student ID: {student_id}\n"
                    f"Student question: {question}"
                )
            )
        ],
        "student_id": student_id,
        "question": question,
        "tool_log": [],
        "turn_count": 0,
        "final_answer": "",
        "max_turns": max_turns,
    }


def run_advisor(student_id: str, question: str, max_turns: int = MAX_TURNS) -> dict:
    """Run the Tool Use graph and return API-safe output."""

    final_state = advisor_app.invoke(initial_advisor_state(student_id, question, max_turns))
    answer = final_state["final_answer"]
    if not answer:
        answer = (
            "The advisor stopped before producing a final response. "
            "Review tool_log for the available academic data."
        )

    return {
        "student_id": final_state["student_id"],
        "question": final_state["question"],
        "answer": answer,
        "tools_called": [entry["tool"] for entry in final_state["tool_log"]],
        "tool_log": final_state["tool_log"],
        "turn_count": final_state["turn_count"],
        "message_count": len(final_state["messages"]),
    }
