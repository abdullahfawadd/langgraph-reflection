"""Graph assembly and runner for the FYP Reflection agent."""

from langgraph.graph import END, StateGraph

from .nodes import critic_node, generator_node
from .state import ReflectionState

MAX_ROUNDS = 3


def should_continue(state: ReflectionState) -> str:
    """Route to another revision or end the graph."""

    max_rounds = state.get("max_rounds", MAX_ROUNDS)
    if state["approved"]:
        print(
            f"  [Reflection Router] Approved after "
            f"{state['reflection_rounds']} round(s)"
        )
        return "done"
    if state["reflection_rounds"] >= max_rounds:
        print(f"  [Reflection Router] Max rounds ({max_rounds}) reached")
        return "done"
    print(f"  [Reflection Router] Routing round {state['reflection_rounds']} to revise")
    return "revise"


def build_reflection_graph():
    """Build START -> generator -> critic -> revise/done."""

    graph = StateGraph(ReflectionState)
    graph.add_node("generator", generator_node)
    graph.add_node("critic", critic_node)
    graph.set_entry_point("generator")
    graph.add_edge("generator", "critic")
    graph.add_conditional_edges(
        "critic",
        should_continue,
        {
            "revise": "generator",
            "done": END,
        },
    )
    return graph.compile()


reflection_app = build_reflection_graph()


def initial_reflection_state(task: str, max_rounds: int = MAX_ROUNDS) -> ReflectionState:
    """Create the initial graph state."""

    return {
        "messages": [],
        "task": task,
        "current_draft": "",
        "critique": "",
        "reflection_rounds": 0,
        "approved": False,
        "max_rounds": max_rounds,
    }


def run_reflection(task: str, max_rounds: int = MAX_ROUNDS) -> dict:
    """Run the full Reflection graph and return API-safe output."""

    final_state = reflection_app.invoke(initial_reflection_state(task, max_rounds))
    return {
        "task": final_state["task"],
        "final_draft": final_state["current_draft"],
        "critique": final_state["critique"],
        "reflection_rounds": final_state["reflection_rounds"],
        "approved": final_state["approved"],
        "message_count": len(final_state["messages"]),
    }
