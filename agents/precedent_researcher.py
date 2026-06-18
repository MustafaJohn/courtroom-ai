from core.llm import chat
from core.prompts import PRECEDENT_SYSTEM
from graph.state import CaseState


def run_precedent_researcher(state: CaseState) -> dict:
    """
    Agent 2: Precedent Researcher
    Identifies relevant legal principles and illustrative case precedents.
    Runs in parallel with the Investigator — has no dependency on its output.
    """
    case_description = state["case_description"]

    user_prompt = f"""
    Analyze the following legal case and identify relevant precedents and legal principles:

    CASE DESCRIPTION:
    {case_description}

    Follow the output format exactly as specified in the system prompt.
    """

    response = chat(PRECEDENT_SYSTEM, user_prompt)

    return {
        "precedents": response
    }