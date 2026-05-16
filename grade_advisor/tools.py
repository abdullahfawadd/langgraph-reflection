"""Simulated academic data tools for the Student Grade Advisor."""

from typing import Any

from langchain_core.tools import tool


STUDENT_DATABASE: dict[str, dict[str, Any]] = {
    "AU-2021-CS-001": {
        "name": "Hassan Ali",
        "program": "BS Computer Science",
        "cgpa": 3.42,
        "total_credit_hours": 118,
        "academic_standing": "Good Standing",
        "semesters": {
            "Fall 2025": [
                {"course": "Software Project Management", "grade": "A-", "credit_hours": 3},
                {"course": "Generative AI for Software Engineering", "grade": "A", "credit_hours": 3},
                {"course": "Final Year Project I", "grade": "B+", "credit_hours": 3},
            ],
            "Spring 2026": [
                {"course": "Final Year Project II", "grade": "In Progress", "credit_hours": 3},
                {"course": "Information Security", "grade": "B+", "credit_hours": 3},
            ],
        },
        "graduation": {
            "eligible": False,
            "missing_requirements": [
                "Complete Final Year Project II",
                "Complete 12 remaining credit hours",
                "Submit internship completion evidence",
            ],
            "expected_graduation_semester": "Fall 2026",
        },
    },
    "AU-2022-SE-017": {
        "name": "Ayesha Khan",
        "program": "BS Software Engineering",
        "cgpa": 2.68,
        "total_credit_hours": 92,
        "academic_standing": "Warning: CGPA below 2.70 scholarship threshold",
        "semesters": {
            "Fall 2025": [
                {"course": "Software Architecture", "grade": "B-", "credit_hours": 3},
                {"course": "Web Engineering", "grade": "C+", "credit_hours": 3},
                {"course": "Human Computer Interaction", "grade": "B", "credit_hours": 3},
            ],
            "Spring 2026": [
                {"course": "Software Quality Assurance", "grade": "In Progress", "credit_hours": 3},
                {"course": "Cloud Computing", "grade": "In Progress", "credit_hours": 3},
            ],
        },
        "graduation": {
            "eligible": False,
            "missing_requirements": [
                "Complete 38 remaining credit hours",
                "Register Final Year Project I",
                "Raise CGPA above 2.00 minimum graduation requirement",
            ],
            "expected_graduation_semester": "Spring 2027",
        },
    },
    "AU-2020-AI-010": {
        "name": "Sara Ahmed",
        "program": "BS Artificial Intelligence",
        "cgpa": 3.81,
        "total_credit_hours": 130,
        "academic_standing": "Dean's List",
        "semesters": {
            "Fall 2025": [
                {"course": "Deep Learning", "grade": "A", "credit_hours": 3},
                {"course": "Natural Language Processing", "grade": "A-", "credit_hours": 3},
                {"course": "Final Year Project II", "grade": "A", "credit_hours": 3},
            ],
            "Spring 2026": [
                {"course": "Professional Practices", "grade": "A-", "credit_hours": 2},
            ],
        },
        "graduation": {
            "eligible": True,
            "missing_requirements": [],
            "expected_graduation_semester": "Spring 2026",
        },
    },
}


STUDENT_ALIASES = {
    "001": "AU-2021-CS-001",
    "CS001": "AU-2021-CS-001",
    "017": "AU-2022-SE-017",
    "SE017": "AU-2022-SE-017",
    "010": "AU-2020-AI-010",
    "AI010": "AU-2020-AI-010",
}


def normalize_student_id(student_id: str) -> str:
    """Accept exact student IDs and short classroom-style aliases."""

    cleaned = student_id.strip().upper()
    return STUDENT_ALIASES.get(cleaned, cleaned)


def _student_or_error(student_id: str) -> tuple[str, dict[str, Any] | None]:
    normalized = normalize_student_id(student_id)
    return normalized, STUDENT_DATABASE.get(normalized)


@tool
def get_cgpa(student_id: str) -> dict[str, Any]:
    """Return CGPA, total credit hours, and academic standing for a student."""

    normalized, student = _student_or_error(student_id)
    if not student:
        return {
            "student_id": normalized,
            "error": "Student not found in simulated academic records.",
        }
    return {
        "student_id": normalized,
        "name": student["name"],
        "program": student["program"],
        "cgpa": student["cgpa"],
        "total_credit_hours": student["total_credit_hours"],
        "academic_standing": student["academic_standing"],
    }


@tool
def get_course_grades(student_id: str, semester: str) -> dict[str, Any]:
    """Return courses, grades, and credit hours for a student in one semester."""

    normalized, student = _student_or_error(student_id)
    if not student:
        return {
            "student_id": normalized,
            "semester": semester,
            "error": "Student not found in simulated academic records.",
        }

    requested = semester.strip().lower()
    for stored_semester, courses in student["semesters"].items():
        if stored_semester.lower() == requested:
            return {
                "student_id": normalized,
                "name": student["name"],
                "semester": stored_semester,
                "courses": courses,
            }

    return {
        "student_id": normalized,
        "name": student["name"],
        "semester": semester,
        "available_semesters": list(student["semesters"].keys()),
        "error": "Semester not found for this student.",
    }


@tool
def check_graduation_eligibility(student_id: str) -> dict[str, Any]:
    """Return graduation eligibility and missing graduation requirements."""

    normalized, student = _student_or_error(student_id)
    if not student:
        return {
            "student_id": normalized,
            "error": "Student not found in simulated academic records.",
        }
    graduation = student["graduation"]
    return {
        "student_id": normalized,
        "name": student["name"],
        "eligible": graduation["eligible"],
        "missing_requirements": graduation["missing_requirements"],
        "expected_graduation_semester": graduation["expected_graduation_semester"],
    }


TOOLS = [get_cgpa, get_course_grades, check_graduation_eligibility]
TOOL_BY_NAME = {tool_item.name: tool_item for tool_item in TOOLS}
