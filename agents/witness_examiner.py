from core.llm import chat
from core.prompts import WITNESS_SYSTEM
from graph.state import CaseState


def run_witness_examiner(state: CaseState) -> dict:
    """
    Agent 3: Witness Examiner (CONDITIONAL)
    Reached only when the graph router determines disputed_testimony=True.
    Identifies contradictions, credibility issues, and weaknesses in testimony.
    """
    case_description = state["case_description"]
    investigation = state.get("investigation", "")

    user_prompt = f"""
    Examine the testimony and evidence in this case for contradictions,
    credibility issues, and weaknesses.

    CASE DESCRIPTION:
    {case_description}

    INVESTIGATOR FINDINGS:
    {investigation if investigation else "No investigation findings available."}

    Focus on:
    1. Contradictions between witness accounts
    2. Credibility issues with any party or witness
    3. Weaknesses in the evidence or testimony

    Follow the output format exactly as specified in the system prompt.
    """

    response = chat(WITNESS_SYSTEM, user_prompt)

    return {
        "witness_examination": response
    }