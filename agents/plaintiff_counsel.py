from core.llm import chat
from core.prompts import PLAINTIFF_SYSTEM
from graph.state import CaseState


def run_plaintiff_counsel(state: CaseState) -> dict:
    """
    Agent 4: Plaintiff's Counsel
    Builds the strongest case for the plaintiff using the investigation,
    legal precedents, and witness examination findings (if any).
    Runs in parallel with Defense Counsel.
    """
    case_description = state["case_description"]
    investigation = state.get("investigation", "")
    precedents = state.get("precedents", "")
    witness_examination = state.get("witness_examination", "")

    user_prompt = f"""
    Build the strongest possible case for the plaintiff using the information below.

    CASE DESCRIPTION:
    {case_description}

    INVESTIGATOR FINDINGS:
    {investigation if investigation else "No investigation findings available."}

    LEGAL PRECEDENTS & PRINCIPLES:
    {precedents if precedents else "No precedents available."}

    WITNESS EXAMINATION:
    {witness_examination if witness_examination else "No disputed testimony — witness examination was not required."}

    Follow the output format exactly as specified in the system prompt.
    """

    response = chat(PLAINTIFF_SYSTEM, user_prompt)

    return {
        "plaintiff_argument": response
    }