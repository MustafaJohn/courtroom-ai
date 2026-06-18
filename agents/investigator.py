from core.llm import chat
from core.prompts import INVESTIGATOR_SYSTEM
from graph.state import CaseState


def run_investigator(state: CaseState) -> dict:
    """
    Agent 1: Legal Investigator
    Extracts facts, evidence, gaps, and determines if testimony is disputed.
    """
    case_description = state["case_description"]
    
    user_prompt = f"""
    Analyze the following legal case and extract the required information:
    
    CASE DESCRIPTION:
    {case_description}
    
    Follow the output format exactly as specified in the system prompt.
    """
    
    response = chat(INVESTIGATOR_SYSTEM, user_prompt)
    
    # Parse disputed testimony from response
    disputed = False
    if "DISPUTED TESTIMONY: YES" in response.upper():
        disputed = True
    
    return {
        "investigation": response,
        "disputed_testimony": disputed
    }