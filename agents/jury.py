from core.llm import chat
from core.prompts import (
    JUROR1_SYSTEM,
    JUROR2_SYSTEM,
    JUROR3_SYSTEM,
    REBUTTAL_SYSTEM,
)
from graph.state import CaseState, JurorVote


# ─────────────────────────────────────────────────────────────────────────
# Phase 1 — independent votes (3 separate parallel graph nodes)
# ─────────────────────────────────────────────────────────────────────────

def _build_case_summary(state: CaseState) -> str:
    """Shared case context every juror sees before voting."""
    return f"""
    CASE DESCRIPTION:
    {state['case_description']}

    INVESTIGATOR FINDINGS:
    {state.get('investigation', 'No investigation findings available.')}

    WITNESS EXAMINATION:
    {state.get('witness_examination') or 'No disputed testimony — witness examination was not required.'}

    PLAINTIFF'S ARGUMENT:
    {state.get('plaintiff_argument', 'No plaintiff argument available.')}

    DEFENSE'S ARGUMENT:
    {state.get('defense_argument', 'No defense argument available.')}
    """


def _vote(juror_id: str, persona: str, system_prompt: str, state: CaseState) -> dict:
    """Shared logic for casting one juror's independent vote."""
    user_prompt = f"""
    Review the case below and deliver your independent verdict.
    {_build_case_summary(state)}

    Follow the output format exactly as specified in the system prompt.
    """

    response = chat(system_prompt, user_prompt)
    verdict, confidence, reasoning = _parse_vote(response)

    vote: JurorVote = {
        "juror_id": juror_id,
        "persona": persona,
        "verdict": verdict,
        "confidence": confidence,
        "original_confidence": confidence,
        "reasoning": reasoning,
        "rebuttal": "",
        "final_verdict": "",
    }
    return {"juror_votes": [vote]}


def run_juror_1(state: CaseState) -> dict:
    """Agent 6: Juror 1 — Strict Constructionist."""
    return _vote("juror_1", "Strict Constructionist", JUROR1_SYSTEM, state)


def run_juror_2(state: CaseState) -> dict:
    """Agent 7: Juror 2 — Liberal Humanist."""
    return _vote("juror_2", "Liberal Humanist", JUROR2_SYSTEM, state)


def run_juror_3(state: CaseState) -> dict:
    """Agent 8: Juror 3 — Pragmatic Moderate."""
    return _vote("juror_3", "Pragmatic Moderate", JUROR3_SYSTEM, state)


# ─────────────────────────────────────────────────────────────────────────
# Phase 2 — rebuttal round + majority verdict (single node, runs after all 3 votes)
# ─────────────────────────────────────────────────────────────────────────

def run_jury_deliberation(state: CaseState) -> dict:
    """
    Each juror reads the other two jurors' verdicts and reasoning, then
    issues a final verdict (may hold or flip). Majority verdict is locked
    after this round. Runs sequentially since each juror's rebuttal context
    is the full set of original votes — no parallelism needed here.
    """
    votes = state["juror_votes"]
    updated_votes: list[JurorVote] = []

    for vote in votes:
        others = [v for v in votes if v["juror_id"] != vote["juror_id"]]
        others_summary = "\n\n".join(
            f"{o['persona']} ({o['juror_id']}): VERDICT={o['verdict']}, "
            f"CONFIDENCE={o['confidence']}\nREASONING: {o['reasoning']}"
            for o in others
        )

        user_prompt = f"""
        Your original verdict: {vote['verdict']} (confidence {vote['confidence']})
        Your original reasoning: {vote['reasoning']}

        OTHER JURORS' VERDICTS:
        {others_summary}

        Follow the output format exactly as specified in the system prompt.
        """

        response = chat(REBUTTAL_SYSTEM, user_prompt)
        rebuttal_text, final_verdict, final_confidence, final_reasoning = _parse_rebuttal(
            response, fallback_verdict=vote["verdict"], fallback_confidence=vote["confidence"]
        )

        updated_votes.append({
            **vote,
            "rebuttal": rebuttal_text,
            "final_verdict": final_verdict,
            "confidence": final_confidence,
            "reasoning": final_reasoning,
        })

    majority = _calculate_majority(updated_votes)

    return {
        "juror_votes": updated_votes,
        "jury_majority": majority,
        "deliberation_log": _build_deliberation_log(updated_votes),
    }


def _build_deliberation_log(votes: list[JurorVote]) -> str:
    """
    Builds a presentable before/after summary of the rebuttal round,
    highlighting any juror who changed their verdict. Used by main.py
    for live CLI display and by report.py for the final document.
    """
    lines = []
    for v in votes:
        changed = v["verdict"] != v["final_verdict"]
        arrow = "→" if changed else "held at"
        verdict_line = (
            f"{v['persona']} ({v['juror_id']}): "
            f"{v['verdict']} {arrow} {v['final_verdict']}"
            if changed else
            f"{v['persona']} ({v['juror_id']}): held at {v['verdict']}"
        )
        confidence_line = f"confidence {v['original_confidence']} → {v['confidence']}"
        flag = "  *** VERDICT CHANGED ***" if changed else ""
        lines.append(f"{verdict_line} ({confidence_line}){flag}")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────
# Parsing helpers — convert structured LLM text into typed fields
# ─────────────────────────────────────────────────────────────────────────

def _parse_vote(response: str) -> tuple[str, int, str]:
    """Extracts VERDICT, CONFIDENCE, REASONING from a juror's initial vote."""
    verdict = "Plaintiff"
    confidence = 5
    reasoning = response

    for line in response.splitlines():
        upper = line.strip().upper()
        if upper.startswith("VERDICT:"):
            verdict = "Defense" if "DEFENSE" in upper else "Plaintiff"
        elif upper.startswith("CONFIDENCE:"):
            confidence = _extract_int(line, default=5)

    reasoning_idx = response.upper().find("REASONING:")
    if reasoning_idx != -1:
        reasoning = response[reasoning_idx + len("REASONING:"):].strip()

    return verdict, confidence, reasoning


def _parse_rebuttal(
    response: str, fallback_verdict: str, fallback_confidence: int
) -> tuple[str, str, int, str]:
    """Extracts MY REBUTTAL, ADJUSTED VERDICT, ADJUSTED CONFIDENCE, FINAL REASONING."""
    rebuttal_text = ""
    final_verdict = fallback_verdict
    final_confidence = fallback_confidence
    final_reasoning = response

    rebuttal_idx = response.upper().find("MY REBUTTAL:")
    verdict_idx = response.upper().find("ADJUSTED VERDICT:")
    if rebuttal_idx != -1:
        end = verdict_idx if verdict_idx != -1 else len(response)
        rebuttal_text = response[rebuttal_idx + len("MY REBUTTAL:"):end].strip()

    for line in response.splitlines():
        upper = line.strip().upper()
        if upper.startswith("ADJUSTED VERDICT:"):
            if "DEFENSE" in upper:
                final_verdict = "Defense"
            elif "PLAINTIFF" in upper:
                final_verdict = "Plaintiff"
            # "SAME" → keep fallback_verdict
        elif upper.startswith("ADJUSTED CONFIDENCE:"):
            final_confidence = _extract_int(line, default=fallback_confidence)

    reasoning_idx = response.upper().find("FINAL REASONING:")
    if reasoning_idx != -1:
        final_reasoning = response[reasoning_idx + len("FINAL REASONING:"):].strip()

    return rebuttal_text, final_verdict, final_confidence, final_reasoning


def _extract_int(line: str, default: int) -> int:
    digits = "".join(c for c in line if c.isdigit())
    return int(digits) if digits else default


def _calculate_majority(votes: list[JurorVote]) -> str:
    plaintiff_votes = sum(1 for v in votes if v["final_verdict"] == "Plaintiff")
    defense_votes = sum(1 for v in votes if v["final_verdict"] == "Defense")
    return "Plaintiff" if plaintiff_votes >= defense_votes else "Defense"