# Lab 10 Report and Testing Guide

## Project Title

LangGraph Reflection Pattern and Tool Use Pattern Implementation

Course: SE483 - Generative AI for Software Engineering

Repository: `https://github.com/abdullahfawadd/langgraph-reflection`

## Objective

This lab implements two agentic patterns using LangGraph:

1. Reflection Pattern: a Generator-Critic-Revise loop converted into a LangGraph `StateGraph`.
2. Tool Use Pattern: a Student Grade Advisor that lets the LLM call Python tools for academic data.

The project uses FastAPI for API endpoints and Groq `llama-3.1-8b-instant` through `langchain-groq`.

## Current Running Server

On this machine, port `8000` was already occupied by another Python process, so the lab server is running on:

```text
http://127.0.0.1:8010
```

Swagger UI:

```text
http://127.0.0.1:8010/docs
```

If you stop the server and port `8000` is free later, you can also run it on `8000`.

## Project Structure

```text
langgraph-reflection/
├── reflection/
│   ├── state.py       # ReflectionState with add_messages
│   ├── nodes.py       # FYP feedback generator and critic nodes
│   └── graph.py       # Reflection graph and routing function
├── grade_advisor/
│   ├── state.py       # ToolUseState with add_messages
│   ├── tools.py       # Simulated student data tools
│   ├── nodes.py       # llm_node and tool_node
│   └── graph.py       # Tool Use graph and routing function
├── main.py            # FastAPI app and endpoints
├── docs/
│   └── lab10_answers.md
├── postman_collection.json
├── requirements.txt
├── README.md
└── .env.example
```

## Important Security Step

The Groq API key that was pasted in chat must be considered exposed. Rotate it in the Groq console before live testing.

Do not commit `.env`.

Create `.env` locally:

```powershell
Copy-Item .env.example .env
```

Then edit `.env`:

```text
GROQ_API_KEY=your_rotated_groq_api_key_here
```

Restart the server after changing `.env`.

## Setup Steps

Run these commands from the project root:

```powershell
cd d:\langgraph-reflection
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the Server

Use port `8010` on this machine:

```powershell
cd d:\langgraph-reflection
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8010
```

Open:

```text
http://127.0.0.1:8010/docs
```

## Basic Validation Without Groq Key

These checks do not require the Groq API key:

```powershell
python -m compileall main.py reflection grade_advisor scripts
python scripts\smoke_test.py
```

Expected result:

```text
Smoke checks passed.
```

## Endpoint Testing Guide

### 1. Health Check

Method:

```http
GET http://127.0.0.1:8010/health
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

Screenshot to attach:

`Screenshot 1 - GET /health response showing generator, critic, llm, and tools nodes`

### 2. Visualise Reflection Graph

Method:

```http
GET http://127.0.0.1:8010/visualise?graph=reflection
```

Expected response includes nodes:

```json
["generator", "critic"]
```

Also check the terminal running Uvicorn. It prints the graph and the teaching diagram:

```text
START -> generator -> critic
critic --revise--> generator
critic --done--> END
```

Screenshot to attach:

`Screenshot 2 - terminal showing Reflection graph with generator and critic loop`

### 3. Visualise Tool Use Graph

Method:

```http
GET http://127.0.0.1:8010/visualise?graph=advisor
```

Expected response includes nodes:

```json
["llm", "tools"]
```

Also check the terminal running Uvicorn. It prints the graph and the teaching diagram:

```text
START -> llm
llm --use_tools--> tools
tools -> llm
llm --done--> END
```

Screenshot to attach:

`Screenshot 3 - terminal showing Tool Use graph with llm and tools loop`

### 4. FYP Reflection Agent

Method:

```http
POST http://127.0.0.1:8010/reflect
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

The exact text will vary because the LLM generates it live. For grading, make sure:

- `final_draft` is not empty.
- It contains four sections: Technical Feasibility, Novelty, Scope, Recommendations.
- `reflection_rounds` is at least `2`.
- `approved` field is present.
- Feedback is specific and actionable.

Screenshot to attach:

`Screenshot 4 - POST /reflect response showing final_draft, critique, reflection_rounds >= 2, and approved`

### 5. Stream Reflection Steps

Method:

```http
POST http://127.0.0.1:8010/stream
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

The exact number of events depends on when the critic approves or when `max_rounds` is reached.

Screenshot to attach:

`Screenshot 5 - POST /stream showing generator and critic events arriving progressively`

### 6. Student Grade Advisor - Single Tool Query

Method:

```http
POST http://127.0.0.1:8010/advise
Content-Type: application/json
```

Body:

```json
{
  "student_id": "AU-2021-CS-001",
  "question": "What is my current CGPA and academic standing?"
}
```

Expected response fields:

```json
{
  "answer": "...",
  "tools_called": ["get_cgpa"],
  "tool_log": [...]
}
```

Screenshot to attach:

`Screenshot 6 - POST /advise single-tool response showing get_cgpa in tools_called`

### 7. Student Grade Advisor - Multi Tool Query

Method:

```http
POST http://127.0.0.1:8010/advise
Content-Type: application/json
```

Body:

```json
{
  "student_id": "AU-2021-CS-001",
  "question": "Show my Fall 2025 grades, CGPA, and graduation eligibility."
}
```

Expected response fields:

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

The order may vary depending on the LLM, but the response should use multiple tools.

Screenshot to attach:

`Screenshot 7 - POST /advise multi-tool response showing course grades, CGPA, graduation eligibility, and tool_log`

## Postman Collection

Import this file into Postman:

```text
postman_collection.json
```

Set the collection variable:

```text
baseUrl = http://127.0.0.1:8010
```

Set Postman timeout to 120 seconds:

```text
Settings -> General -> Request timeout in ms -> 120000
```

## Written Work to Submit

The written answers are already completed in:

```text
docs/lab10_answers.md
```

Attach or paste these sections:

1. Graded Task 1 Reflection Question
2. Tool Use Alignment Table
3. Take-Home Explanation

## Final Submission Checklist

Submit these files:

- `reflection/state.py`
- `reflection/nodes.py`
- `reflection/graph.py`
- `grade_advisor/state.py`
- `grade_advisor/tools.py`
- `grade_advisor/nodes.py`
- `grade_advisor/graph.py`
- `main.py`
- `docs/lab10_answers.md`
- `README.md`
- `postman_collection.json`

Attach these screenshots:

1. `GET /health` response.
2. Reflection graph terminal screenshot from `/visualise?graph=reflection`.
3. Tool Use graph terminal screenshot from `/visualise?graph=advisor`.
4. `POST /reflect` response with `reflection_rounds >= 2`.
5. `POST /stream` showing generator and critic events.
6. `POST /advise` single-tool query showing `get_cgpa`.
7. `POST /advise` multi-tool query showing multiple tools and `tool_log`.
8. Optional: Swagger UI at `http://127.0.0.1:8010/docs` showing all endpoints.

## How to Stop the Server

If the server was started manually in a terminal, press:

```text
Ctrl + C
```

If it was started in the background on this machine, run:

```powershell
Stop-Process -Id (Get-Content .\uvicorn-8010.pid) -Force
```

