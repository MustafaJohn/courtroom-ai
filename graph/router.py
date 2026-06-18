from graph.state import CaseState


# Maps internal node names to friendly progress labels for display in
# the CLI and Streamlit UI. None = plumbing node, not shown to the user.
NODE_LABELS = {
    "investigator": "Investigator — extracting facts and evidence",
    "precedent_researcher": "Precedent Researcher — finding legal principles",
    "research_join": None,
    "witness_examiner": "Witness Examiner — disputed testimony detected, cross-examining",
    "arguments_gate": None,
    "plaintiff_counsel": "Plaintiff's Counsel — building argument",
    "defense_counsel": "Defense Counsel — building argument",
    "juror_1": "Juror 1 (Strict Constructionist) — casting independent vote",
    "juror_2": "Juror 2 (Liberal Humanist) — casting independent vote",
    "juror_3": "Juror 3 (Pragmatic Moderate) — casting independent vote",
    "jury_deliberation": "Jury — rebuttal round and majority verdict",
    "judge": "Judge — issuing final ruling",
}


def route_after_investigation(state: CaseState) -> str:
    """
    The single dynamic routing decision in this workflow.

    Called from the research_join node, which waits for BOTH Investigator
    and Precedent Researcher to finish before this routing decision fires.

    If the Investigator flagged disputed testimony, route to the Witness
    Examiner before arguments are built. Otherwise, skip straight to the
    arguments_gate join node, which fans out to both counsels.

    This is what makes the graph's path depend on intermediate findings
    rather than being a fixed, hard-coded sequence.
    """
    if state["disputed_testimony"]:
        return "witness_examiner"
    return "arguments_gate"


def research_join(state: CaseState) -> dict:
    """
    Passthrough join node. Exists only so the graph has a single, real
    fan-in point after Investigator + Precedent Researcher both complete,
    before the routing decision fires. No LLM call — pure graph plumbing.
    """
    return {}


def arguments_gate(state: CaseState) -> dict:
    """
    Passthrough join node. Single funnel point both routing branches
    (witness_examiner or skip) converge on, before fanning out to
    Plaintiff and Defense Counsel. Prevents the double-fire bug where
    both counsels would otherwise have two independent incoming edges.
    No LLM call — pure graph plumbing.
    """
    return {}