# Lab 10 Report, Postman Testing, and Screenshot Guide

## Project Information

Project title: LangGraph Reflection Pattern and Tool Use Pattern Implementation

Course: SE483 - Generative AI for Software Engineering

Repository: `https://github.com/abdullahfawadd/langgraph-reflection`

Local project path: `d:\langgraph-reflection`

Running server URL on this machine:

```text
http://127.0.0.1:8010
```

Swagger UI:

```text
http://127.0.0.1:8010/docs
```

Note: Port `8000` was already occupied on this machine, so this project is running on port `8010`.

## Objective

This lab implements agentic patterns using LangGraph:

1. Reflection Pattern: a Generator-Critic-Revise loop using LangGraph `StateGraph`.
2. Tool Use Pattern: a Student Grade Advisor that calls Python tools instead of guessing academic data.

The app uses FastAPI, LangGraph, LangChain, `langchain-groq`, and Groq `llama-3.1-8b-instant`.

## API Key Status

The Groq key is added locally in `.env` so the app can run.

Important:

- `.env` is ignored by git.
- The key is not committed or pushed to GitHub.
- Because the key was shared in chat, it should still be rotated after testing.

The committed safe example file is:

```text
.env.example
```

## Project Structure

```text
langgraph-reflection/
|-- reflection/
|   |-- state.py        # ReflectionState with add_messages reducer
|   |-- nodes.py        # FYP feedback generator and critic nodes
|   `-- graph.py        # Reflection graph and routing function
|-- grade_advisor/
|   |-- state.py        # ToolUseState with add_messages reducer
|   |-- tools.py        # Simulated student academic data tools
|   |-- nodes.py        # llm_node and tool_node
|   `-- graph.py        # Tool Use graph and routing function
|-- docs/
|   `-- lab10_answers.md
|-- main.py             # FastAPI app
|-- postman_collection.json
|-- requirements.txt
|-- README.md
|-- LAB_REPORT.md
`-- .env.example
```

## How to Run

From PowerShell:

```powershell
cd d:\langgraph-reflection
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8010
```

Open Swagger:

```text
http://127.0.0.1:8010/docs
```

## Quick Verification Commands

These checks confirm the project imports and the non-LLM endpoints work:

```powershell
python -m compileall main.py reflection grade_advisor scripts
python scripts\smoke_test.py
```

Expected output:

```text
Smoke checks passed.
```

## Postman Setup Process

1. Open Postman.
2. Click `Import`.
3. Import `postman_collection.json`.
4. Open the imported collection.
5. Set collection variable:

```text
baseUrl = http://127.0.0.1:8010
```

6. Set request timeout:

```text
Settings -> General -> Request timeout in ms -> 120000
```

7. Run the requests in this order:

```text
1. Health
2. Visualise Reflection
3. Visualise Advisor
4. Reflect FYP Feedback
5. Stream Reflection
6. Advise Single Tool
7. Advise Multi Tool
```

## General Screenshot Rules

For every screenshot, include:

- The full Postman request URL.
- The HTTP method.
- The JSON body if it is a POST request.
- The response body.
- For graph screenshots, include the terminal where Uvicorn is running.

Use these placeholders in your final Word/PDF submission:

```text
[Attach Screenshot Here: Screenshot 1 - Health Check]
[Attach Screenshot Here: Screenshot 2 - Reflection Graph]
[Attach Screenshot Here: Screenshot 3 - Advisor Graph]
[Attach Screenshot Here: Screenshot 4 - FYP Reflection Response]
[Attach Screenshot Here: Screenshot 5 - Stream Response]
[Attach Screenshot Here: Screenshot 6 - Single Tool Advisor Response]
[Attach Screenshot Here: Screenshot 7 - Multi Tool Advisor Response]
```

## Endpoint Test 1 - Health Check

Purpose: prove the API is running and both graphs are loaded.

Postman request:

```http
GET {{baseUrl}}/health
```

Direct URL:

```text
http://127.0.0.1:8010/health
```

Expected response includes:

```json
{
  "status": "ok",
  "framework": "LangGraph",
  "patterns": ["Reflection", "Tool Use"],
  "graph_nodes": ["generator", "critic"],
  "advisor_graph_nodes": ["llm", "tools"]
}
```

Screenshot placeholder:

```text
[Attach Screenshot Here: Screenshot 1 - GET /health response showing generator, critic, llm, and tools]
```

## Endpoint Test 2 - Visualise Reflection Graph

Purpose: prove the Reflection graph still has the generator and critic loop.

Postman request:

```http
GET {{baseUrl}}/visualise?graph=reflection
```

Direct URL:

```text
http://127.0.0.1:8010/visualise?graph=reflection
```

Expected graph:

```text
START -> generator -> critic
critic --revise--> generator
critic --done--> END
```

Screenshot placeholder:

```text
[Attach Screenshot Here: Screenshot 2 - Uvicorn terminal showing Reflection graph with generator and critic loop]
```

## Endpoint Test 3 - Visualise Tool Use Graph

Purpose: prove the Tool Use graph has the LLM-tool dispatch loop.

Postman request:

```http
GET {{baseUrl}}/visualise?graph=advisor
```

Direct URL:

```text
http://127.0.0.1:8010/visualise?graph=advisor
```

Expected graph:

```text
START -> llm
llm --use_tools--> tools
tools -> llm
llm --done--> END
```

Screenshot placeholder:

```text
[Attach Screenshot Here: Screenshot 3 - Uvicorn terminal showing Tool Use graph with llm and tools loop]
```

## Graded Lab Task 1 - FYP Feedback Reflection Agent

Task requirement:

- Change the domain to an FYP Feedback Agent.
- The generator writes structured FYP feedback reports.
- The critic checks specificity, actionability, completeness, and professional tone.
- `state.py` and `graph.py` remain the same graph structure.

Implemented files:

```text
reflection/state.py
reflection/nodes.py
reflection/graph.py
main.py
```

Postman request:

```http
POST {{baseUrl}}/reflect
Content-Type: application/json
```

Body:

```json
{
  "task": "Title: AI-Based Attendance Monitoring System\nProblem Statement: Manual attendance tracking in university classes is slow and error-prone. The project proposes a face recognition system that records attendance and generates reports for instructors.",
  "max_rounds": 3
}
```

Expected response fields:

```json
{
  "task": "...",
  "final_draft": "...",
  "critique": "...",
  "reflection_rounds": 2,
  "approved": true,
  "message_count": 4
}
```

What to check:

- `final_draft` is not empty.
- `final_draft` includes Technical Feasibility.
- `final_draft` includes Novelty.
- `final_draft` includes Scope.
- `final_draft` includes Recommendations.
- `reflection_rounds` is at least `2`.
- `approved` field exists.
- The feedback is specific and actionable.

Screenshot placeholders:

```text
[Attach Screenshot Here: Screenshot 4A - POST /reflect request body in Postman]
[Attach Screenshot Here: Screenshot 4B - POST /reflect response showing final_draft]
[Attach Screenshot Here: Screenshot 4C - POST /reflect response showing reflection_rounds >= 2 and approved field]
```

Written reflection answer:

Use the answer already written in:

```text
docs/lab10_answers.md
```

Placeholder for final submission:

```text
[Paste Graded Task 1 Reflection Question Answer Here]
```

## Graded Lab Task 1 - Stream Demonstration

Purpose: prove `.stream()` shows intermediate Reflection steps.

Postman request:

```http
POST {{baseUrl}}/stream
Content-Type: application/json
```

Body:

```json
{
  "task": "Title: Smart Complaint Routing for University Helpdesks\nProblem Statement: Students submit complaints through multiple channels. The system should classify complaints and route them to the correct department.",
  "max_rounds": 3
}
```

Expected stream sequence:

```text
generator event
critic event
generator event
critic event
```

Screenshot placeholder:

```text
[Attach Screenshot Here: Screenshot 5 - POST /stream showing generator and critic events]
```

## Graded Lab Task 2 - Tool Use Student Grade Advisor

Task requirement:

- Implement Tool Use Pattern in LangGraph.
- Build a Student Grade Advisor for Air University students.
- Use Python tools for academic data.
- LLM must call tools through `bind_tools()`.
- Tool node executes tool calls and returns tool messages.
- Routing function checks whether the last message contains tool calls.

Implemented files:

```text
grade_advisor/state.py
grade_advisor/tools.py
grade_advisor/nodes.py
grade_advisor/graph.py
main.py
```

Implemented tools:

```text
get_cgpa(student_id)
get_course_grades(student_id, semester)
check_graduation_eligibility(student_id)
```

Available sample student IDs:

```text
AU-2021-CS-001
AU-2022-SE-017
AU-2020-AI-010
```

### Task 2 Test A - Single Tool Query

Purpose: prove the LLM can call one tool.

Postman request:

```http
POST {{baseUrl}}/advise
Content-Type: application/json
```

Body:

```json
{
  "student_id": "AU-2021-CS-001",
  "question": "What is my current CGPA and academic standing?"
}
```

Expected response includes:

```json
{
  "answer": "...",
  "tools_called": ["get_cgpa"],
  "tool_log": [...]
}
```

Screenshot placeholders:

```text
[Attach Screenshot Here: Screenshot 6A - POST /advise single-tool request body]
[Attach Screenshot Here: Screenshot 6B - POST /advise response showing get_cgpa in tools_called]
```

### Task 2 Test B - Multi Tool Query

Purpose: prove the LLM can call multiple tools in the same graph run.

Postman request:

```http
POST {{baseUrl}}/advise
Content-Type: application/json
```

Body:

```json
{
  "student_id": "AU-2021-CS-001",
  "question": "Show my Fall 2025 grades, CGPA, and graduation eligibility."
}
```

Expected response includes several tools:

```json
{
  "answer": "...",
  "tools_called": [
    "get_course_grades",
    "get_cgpa",
    "check_graduation_eligibility"
  ],
  "tool_log": [...]
}
```

The order of `tools_called` can vary depending on the model.

Screenshot placeholders:

```text
[Attach Screenshot Here: Screenshot 7A - POST /advise multi-tool request body]
[Attach Screenshot Here: Screenshot 7B - POST /advise response showing multiple tools_called]
[Attach Screenshot Here: Screenshot 7C - POST /advise response showing tool_log details]
```

### Task 2 Alignment Table

Use the completed table from:

```text
docs/lab10_answers.md
```

Placeholder for final submission:

```text
[Paste Tool Use Alignment Table Here]
```

### Task 2 Written Explanation

Use the completed explanation from:

```text
docs/lab10_answers.md
```

Placeholder for final submission:

```text
[Paste 8-10 Line Tool Use Explanation Here]
```

## Final Screenshot Checklist

Attach these screenshots in order:

1. Health check response: `GET /health`.
2. Reflection graph terminal output: `GET /visualise?graph=reflection`.
3. Tool Use graph terminal output: `GET /visualise?graph=advisor`.
4. Graded Task 1 request body: `POST /reflect`.
5. Graded Task 1 response showing `final_draft`.
6. Graded Task 1 response showing `reflection_rounds >= 2`.
7. Stream response showing generator and critic events: `POST /stream`.
8. Graded Task 2 single-tool request body: `POST /advise`.
9. Graded Task 2 single-tool response showing `get_cgpa`.
10. Graded Task 2 multi-tool request body: `POST /advise`.
11. Graded Task 2 multi-tool response showing multiple tools.
12. Graded Task 2 multi-tool response showing `tool_log`.
13. Optional: Swagger UI showing all endpoints.
14. Optional: GitHub repository page showing pushed code.

## Final Files to Submit

Submit these files or repository link:

```text
reflection/state.py
reflection/nodes.py
reflection/graph.py
grade_advisor/state.py
grade_advisor/tools.py
grade_advisor/nodes.py
grade_advisor/graph.py
main.py
docs/lab10_answers.md
README.md
LAB_REPORT.md
postman_collection.json
```

## How to Stop the Server

If running in a terminal, press:

```text
Ctrl + C
```

If running in the background:

```powershell
Stop-Process -Id (Get-Content .\uvicorn-8010.pid) -Force
```

## How to Restart the Server

```powershell
cd d:\langgraph-reflection
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8010
```
