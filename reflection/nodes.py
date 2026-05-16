"""Generator and critic nodes for the FYP Reflection agent."""

import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from .state import ReflectionState

load_dotenv()

GROQ_MODEL = "llama-3.1-8b-instant"
MIN_APPROVAL_ROUND = 2

_llm: ChatGroq | None = None


def get_llm() -> ChatGroq:
    """Create the Groq chat model lazily so imports work without a key."""

    global _llm
    if _llm is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing. Rotate the exposed key, add the new "
                "value to .env, and restart the server."
            )
        _llm = ChatGroq(model=GROQ_MODEL, temperature=0.2, api_key=api_key)
    return _llm


GENERATOR_SYSTEM_PROMPT = """
You are an experienced FYP supervisor at Air University.
Your job is to write structured, professional feedback reports for Final Year
Project proposals.

The student will provide an FYP title and problem statement. Produce a feedback
report with exactly these sections:
1. Technical Feasibility
2. Novelty
3. Scope
4. Recommendations

When writing the first draft:
- Be specific to the supplied title and problem statement.
- Mention concrete risks, dependencies, datasets, tools, or validation methods.
- Avoid vague comments such as "needs more work" without explaining what to do.

When revising:
- Address every point raised by the critic.
- Keep the same four sections.
- Make each concern actionable by pairing it with a recommendation.
- Use a professional, supervisor-style tone.
"""

CRITIC_SYSTEM_PROMPT = """
You are a strict academic reviewer for FYP feedback reports.
Review the report against these criteria:
- Specificity: comments must be tied to the actual project idea.
- Actionability: every concern must include a practical recommendation.
- Completeness: all four sections must be present.
- Professional tone: feedback should be respectful and supervisor-like.

Decision rule:
- If every criterion is met, write APPROVED on the first line, then briefly
  explain why the report is acceptable.
- If any criterion fails, do not write APPROVED anywhere. List each issue with
  clear revision guidance.
- For review round 1, require at least one improvement and do not approve yet.
"""


def generator_node(state: ReflectionState) -> dict:
    """Produce the first FYP feedback draft or revise it from critique."""

    next_round = state["reflection_rounds"] + 1
    print(
        f"  [Reflection Generator] Round {next_round}: "
        f"{'first draft' if state['reflection_rounds'] == 0 else 'revision'}"
    )

    if state["reflection_rounds"] == 0:
        user_content = (
            "Write a structured FYP feedback report for this proposal.\n\n"
            f"{state['task']}"
        )
    else:
        user_content = (
            f"Original FYP proposal:\n{state['task']}\n\n"
            f"Previous feedback report:\n{state['current_draft']}\n\n"
            f"Critique to address:\n{state['critique']}\n\n"
            "Revise the report so it satisfies the critic."
        )

    response = get_llm().invoke(
        [
            SystemMessage(content=GENERATOR_SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]
    )
    draft = response.content
    print(f"  [Reflection Generator] Draft length: {len(draft)} characters")

    return {
        "current_draft": draft,
        "reflection_rounds": next_round,
        "messages": [AIMessage(content=draft, name="generator")],
    }


def critic_node(state: ReflectionState) -> dict:
    """Review the current FYP feedback report and set the approval flag."""

    print(f"  [Reflection Critic] Reviewing round {state['reflection_rounds']}")
    response = get_llm().invoke(
        [
            SystemMessage(content=CRITIC_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Review round: {state['reflection_rounds']}\n\n"
                    f"Original FYP proposal:\n{state['task']}\n\n"
                    f"Feedback report to review:\n{state['current_draft']}"
                )
            ),
        ]
    )
    critique = response.content.strip()

    if (
        state["reflection_rounds"] < MIN_APPROVAL_ROUND
        and critique.upper().startswith("APPROVED")
    ):
        critique = (
            "Needs revision before approval:\n"
            "- Add project-specific technical risks and required resources.\n"
            "- Make the novelty assessment more explicit against existing "
            "solutions.\n"
            "- Ensure every concern includes a concrete next action."
        )

    approved = (
        state["reflection_rounds"] >= MIN_APPROVAL_ROUND
        and critique.upper().startswith("APPROVED")
    )
    print(
        "  [Reflection Critic] Decision: "
        f"{'APPROVED' if approved else 'NEEDS REVISION'}"
    )

    return {
        "critique": critique,
        "approved": approved,
        "messages": [AIMessage(content=critique, name="critic")],
    }
