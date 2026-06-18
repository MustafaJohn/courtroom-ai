import operator
from typing import Annotated
from typing_extensions import TypedDict


class JurorVote(TypedDict):
    juror_id: str          # "juror_1", "juror_2", "juror_3"
    persona: str            # "Strict Constructionist", "Liberal Humanist", "Pragmatic Moderate"
    verdict: str             # initial verdict — "Plaintiff" | "Defense"
    confidence: int          # current confidence (overwritten after rebuttal)
    original_confidence: int  # confidence at initial vote, preserved for before/after comparison
    reasoning: str
    rebuttal: str             # filled after rebuttal round
    final_verdict: str        # verdict after rebuttal round


class CaseState(TypedDict):
    # ── Input ──────────────────────────────────────────────────────────
    case_description: str

    # ── Investigation phase (parallel) ────────────────────────────────
    investigation: str
    disputed_testimony: bool          # parsed from investigation, drives routing
    precedents: str

    # ── Conditional ────────────────────────────────────────────────────
    witness_examination: str          # empty string if not triggered

    # ── Arguments phase (parallel) ─────────────────────────────────────
    plaintiff_argument: str
    defense_argument: str

    # ── Jury phase ─────────────────────────────────────────────────────
    # Annotated with operator.add so 3 parallel juror nodes each append their
    # own vote instead of overwriting each other (last-write-wins problem).
    juror_votes: Annotated[list[JurorVote], operator.add]
    jury_majority: str                  # "Plaintiff" | "Defense"
    deliberation_log: str               # presentable before/after summary of rebuttal round

    # ── Judge phase ────────────────────────────────────────────────────
    judge_decision: str                 # raw judge output

    # ── Output ─────────────────────────────────────────────────────────
    final_report: str