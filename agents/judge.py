from core.llm import chat
from core.prompts import JUDGE_SYSTEM
from graph.state import CaseState


def run_judge(state: CaseState) -> dict:
    """
    Agent 9: Judge
    Reviews all three jurors' final verdicts and the locked majority.
    Issues a binding ruling: AGREE with majority, DISSENT with opinion,
    or OVERRIDE with legal justification.
    """
    juror_votes = state["juror_votes"]
    jury_majority = state["jury_majority"]

    votes_summary = "\n\n".join(
        f"{v['persona']} ({v['juror_id']}): FINAL VERDICT={v['final_verdict']}, "
        f"CONFIDENCE={v['confidence']}\nREASONING: {v['reasoning']}\nREBUTTAL: {v['rebuttal']}"
        for v in juror_votes
    )

    user_prompt = f"""
    CASE DESCRIPTION:
    {state['case_description']}

    PLAINTIFF'S ARGUMENT:
    {state.get('plaintiff_argument', 'No plaintiff argument available.')}

    DEFENSE'S ARGUMENT:
    {state.get('defense_argument', 'No defense argument available.')}

    JURY VERDICTS (after deliberation and rebuttal):
    {votes_summary}

    JURY MAJORITY VERDICT: {jury_majority}

    Review the jury's reasoning and issue your final binding ruling.
    Follow the output format exactly as specified in the system prompt.
    """

    response = chat(JUDGE_SYSTEM, user_prompt)

    return {
        "judge_decision": response
    }