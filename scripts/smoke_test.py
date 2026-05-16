"""Local smoke checks that do not require a Groq API key."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grade_advisor.tools import (
    check_graduation_eligibility,
    get_cgpa,
    get_course_grades,
)
from main import app


def main() -> None:
    client = TestClient(app)

    health = client.get("/health")
    health.raise_for_status()
    payload = health.json()
    assert payload["status"] == "ok"
    assert "generator" in payload["graph_nodes"]
    assert "critic" in payload["graph_nodes"]
    assert "llm" in payload["advisor_graph_nodes"]
    assert "tools" in payload["advisor_graph_nodes"]

    for graph_name in ("reflection", "advisor"):
        response = client.get(f"/visualise?graph={graph_name}")
        response.raise_for_status()
        assert response.json()["nodes"]

    assert get_cgpa.invoke({"student_id": "AU-2021-CS-001"})["cgpa"] == 3.42
    assert get_course_grades.invoke(
        {"student_id": "AU-2021-CS-001", "semester": "Fall 2025"}
    )["courses"]
    assert (
        check_graduation_eligibility.invoke({"student_id": "AU-2020-AI-010"})[
            "eligible"
        ]
        is True
    )

    print("Smoke checks passed.")


if __name__ == "__main__":
    main()
