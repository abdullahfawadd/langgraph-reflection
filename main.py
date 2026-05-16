"""FastAPI entrypoint for Lab 10 LangGraph agents."""

import json
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from grade_advisor.graph import MAX_TURNS, advisor_app, initial_advisor_state, run_advisor
from grade_advisor.nodes import GROQ_MODEL as ADVISOR_MODEL
from reflection.graph import (
    MAX_ROUNDS,
    initial_reflection_state,
    reflection_app,
    run_reflection,
)
from reflection.nodes import GROQ_MODEL as REFLECTION_MODEL

load_dotenv()

app = FastAPI(
    title="LangGraph Reflection and Tool Use Lab",
    description="Lab 10 implementation with FYP Reflection and Student Grade Advisor agents.",
    version="1.0.0",
)


class ReflectionRequest(BaseModel):
    task: str = Field(
        ...,
        min_length=1,
        description="FYP title and problem statement to review.",
        examples=[
            (
                "Title: AI-Based Attendance Monitoring System\n"
                "Problem Statement: Manual attendance tracking in university "
                "classes is slow and error-prone. The project proposes a face "
                "recognition system that records attendance and generates "
                "reports for instructors."
            )
        ],
    )
    max_rounds: int = Field(
        default=MAX_ROUNDS,
        ge=1,
        le=5,
        description="Maximum Generator-Critic cycles.",
    )


class AdvisorRequest(BaseModel):
    student_id: str = Field(
        ...,
        min_length=1,
        description="Student ID, for example AU-2021-CS-001.",
        examples=["AU-2021-CS-001"],
    )
    question: str = Field(
        ...,
        min_length=1,
        description="Academic standing question.",
        examples=[
            "What is my CGPA and am I eligible to graduate?",
        ],
    )
    max_turns: int = Field(
        default=MAX_TURNS,
        ge=2,
        le=10,
        description="Safety limit for the LLM-tool dispatch loop.",
    )


def _visible_graph_nodes(compiled_graph) -> list[str]:
    nodes = compiled_graph.get_graph().nodes.keys()
    return [node for node in nodes if not node.startswith("__")]


REFLECTION_ASCII = """
        START
          |
          v
     [generator] <-----+
          |            |
          v            |
       [critic] --revise
          |
        done
          v
         END
""".strip()

ADVISOR_ASCII = """
        START
          |
          v
        [llm] <------+
          |          |
    use_tools        |
          v          |
       [tools] ------+
          |
        done
          v
         END
""".strip()


def _print_graph_ascii(compiled_graph, fallback: str) -> str:
    graph_obj = compiled_graph.get_graph()
    try:
        if hasattr(graph_obj, "draw_ascii"):
            native_ascii = graph_obj.draw_ascii()
            combined = (
                f"{native_ascii}\n\n"
                "Teaching diagram with conditional route labels:\n"
                f"{fallback}"
            )
            print(combined)
            return combined
        if hasattr(graph_obj, "print_ascii"):
            graph_obj.print_ascii()
            print("\nTeaching diagram with conditional route labels:")
            print(fallback)
            return fallback
    except Exception as exc:
        print(f"Could not render LangGraph ASCII automatically: {exc}")

    print(fallback)
    return fallback


@app.get("/health")
def health() -> dict:
    """Return project and graph health metadata."""

    reflection_nodes = _visible_graph_nodes(reflection_app)
    advisor_nodes = _visible_graph_nodes(advisor_app)
    return {
        "status": "ok",
        "framework": "LangGraph",
        "patterns": ["Reflection", "Tool Use"],
        "model": REFLECTION_MODEL,
        "reflection_model": REFLECTION_MODEL,
        "advisor_model": ADVISOR_MODEL,
        "graph_nodes": reflection_nodes,
        "advisor_graph_nodes": advisor_nodes,
        "max_rounds": MAX_ROUNDS,
        "max_turns": MAX_TURNS,
        "graphs": {
            "reflection": {
                "pattern": "Reflection",
                "nodes": reflection_nodes,
            },
            "advisor": {
                "pattern": "Tool Use",
                "nodes": advisor_nodes,
            },
        },
    }


@app.get("/visualise")
def visualise(
    graph: Literal["reflection", "advisor"] = Query(
        default="reflection",
        description="Which graph to print.",
    )
) -> dict:
    """Print and return a graph ASCII diagram."""

    if graph == "reflection":
        ascii_graph = _print_graph_ascii(reflection_app, REFLECTION_ASCII)
        return {
            "graph": "reflection",
            "message": "Reflection graph printed to the server terminal.",
            "nodes": _visible_graph_nodes(reflection_app),
            "ascii": ascii_graph,
        }

    ascii_graph = _print_graph_ascii(advisor_app, ADVISOR_ASCII)
    return {
        "graph": "advisor",
        "message": "Advisor graph printed to the server terminal.",
        "nodes": _visible_graph_nodes(advisor_app),
        "ascii": ascii_graph,
    }


@app.post("/reflect")
def reflect(req: ReflectionRequest) -> dict:
    """Run the FYP Reflection graph and return the final report."""

    if not req.task.strip():
        raise HTTPException(status_code=400, detail="task cannot be empty")
    try:
        return run_reflection(req.task, req.max_rounds)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/stream")
def stream_reflect(req: ReflectionRequest) -> StreamingResponse:
    """Stream intermediate Reflection node results as server-sent events."""

    if not req.task.strip():
        raise HTTPException(status_code=400, detail="task cannot be empty")

    def event_generator():
        try:
            for step in reflection_app.stream(
                initial_reflection_state(req.task, req.max_rounds)
            ):
                node_name = next(iter(step))
                state_update = step[node_name]
                event = {
                    "node": node_name,
                    "round": state_update.get("reflection_rounds", "?"),
                    "approved": state_update.get("approved"),
                }
                if node_name == "generator" and "current_draft" in state_update:
                    draft = state_update["current_draft"]
                    event["draft_preview"] = (
                        draft[:300] + "..." if len(draft) > 300 else draft
                    )
                if node_name == "critic" and "critique" in state_update:
                    critique = state_update["critique"]
                    event["critique_preview"] = (
                        critique[:300] + "..." if len(critique) > 300 else critique
                    )
                yield f"data: {json.dumps(event)}\n\n"
        except RuntimeError as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/advise")
def advise(req: AdvisorRequest) -> dict:
    """Run the Student Grade Advisor Tool Use graph."""

    if not req.student_id.strip():
        raise HTTPException(status_code=400, detail="student_id cannot be empty")
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty")
    try:
        return run_advisor(req.student_id, req.question, req.max_turns)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
