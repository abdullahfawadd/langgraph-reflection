# LangGraph Reflection + Tool Use Lab 10

This project implements the full SE483 Lab 10 assignment:

- Solved Reflection Pattern app using LangGraph.
- Graded Task 1 domain change into an FYP Feedback Agent.
- Take-home Tool Use Pattern app as a Student Grade Advisor.

The exposed Groq key from chat is not stored here. Rotate it in the Groq console,
then put the new key in a local `.env` file.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env`:

```text
GROQ_API_KEY=your_rotated_groq_api_key_here
```

Run the API:

```powershell
uvicorn main:app --reload --port 8000
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

### Health

```http
GET http://127.0.0.1:8000/health
```

Returns both graph node lists. The Reflection node list includes `generator`
and `critic`; the advisor node list includes `llm` and `tools`.

### Visualise Reflection Graph

```http
GET http://127.0.0.1:8000/visualise?graph=reflection
```

This prints the generator/critic loop to the terminal.

### Visualise Tool Use Graph

```http
GET http://127.0.0.1:8000/visualise?graph=advisor
```

This prints the LLM/tool dispatch loop to the terminal.

### FYP Reflection Agent

```http
POST http://127.0.0.1:8000/reflect
Content-Type: application/json

{
  "task": "Title: AI-Based Attendance Monitoring System\nProblem Statement: Manual attendance tracking in university classes is slow and error-prone. The project proposes a face recognition system that records attendance and generates reports for instructors.",
  "max_rounds": 3
}
```

Expected response fields:

- `final_draft`
- `critique`
- `reflection_rounds`
- `approved`
- `message_count`

### Stream Reflection Steps

```http
POST http://127.0.0.1:8000/stream
Content-Type: application/json

{
  "task": "Title: Smart Complaint Routing for University Helpdesks\nProblem Statement: Students submit complaints through multiple channels. The system should classify complaints and route them to the correct department.",
  "max_rounds": 3
}
```

This returns server-sent events after each graph node finishes.

### Student Grade Advisor

Single-tool query:

```http
POST http://127.0.0.1:8000/advise
Content-Type: application/json

{
  "student_id": "AU-2021-CS-001",
  "question": "What is my current CGPA and academic standing?"
}
```

Multi-tool query:

```http
POST http://127.0.0.1:8000/advise
Content-Type: application/json

{
  "student_id": "AU-2021-CS-001",
  "question": "Show my Fall 2025 grades, CGPA, and graduation eligibility."
}
```

## Simulated Student IDs

- `AU-2021-CS-001`
- `AU-2022-SE-017`
- `AU-2020-AI-010`

Short aliases also work: `001`, `017`, and `010`.

## Screenshot Checklist

Capture these for submission:

- `GET /health` showing both graph node lists.
- `GET /visualise?graph=reflection` terminal output.
- `GET /visualise?graph=advisor` terminal output.
- `POST /reflect` response with `reflection_rounds >= 2`.
- `POST /stream` showing generator and critic events.
- `POST /advise` single-tool query.
- `POST /advise` multi-tool query.

## Local Checks

These checks do not require a Groq key:

```powershell
python -m compileall .
python scripts\smoke_test.py
```

Live `/reflect`, `/stream`, and `/advise` calls require a rotated Groq key in
`.env`.
