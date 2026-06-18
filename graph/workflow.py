from langgraph.graph import StateGraph, START, END

from graph.state import CaseState
from graph.router import route_after_investigation, research_join, arguments_gate
from agents import (
    run_investigator,
    run_precedent_researcher,
    run_witness_examiner,
    run_plaintiff_counsel,
    run_defense_counsel,
    run_juror_1,
    run_juror_2,
    run_juror_3,
    run_jury_deliberation,
    run_judge,
)


def build_workflow():
    """
    Builds the full courtroom multi-agent graph.

    Topology note: research_join and arguments_gate are passthrough nodes
    (no LLM call) that exist purely to give the graph a single, real fan-in
    point at each convergence. Without them, nodes with two independent
    incoming edges fire once per edge instead of once total — confirmed via
    smoke testing before this was finalized. See router.py for details.

    Flow:
      START ─┬─▶ investigator ──────┐
             └─▶ precedent_researcher┴─▶ research_join ─▶ [conditional]
                                                              │
                                          witness_examiner ◀──┤
                                                  │            │
                                                  └────────────┴─▶ arguments_gate
                                                                        │
                                                        ┌───────────────┴───────────────┐
                                                        ▼                                ▼
                                                plaintiff_counsel                defense_counsel
                                                        │                                │
                                                        └────────────┬───────────────────┘
                                                                      ▼
                                                      juror_1 / juror_2 / juror_3 (parallel)
                                                                      │
                                                              jury_deliberation
                                                                      │
                                                                    judge ─▶ END
    """
    graph = StateGraph(CaseState)

    # ── Register nodes ───────────────────────────────────────────────
    graph.add_node("investigator", run_investigator)
    graph.add_node("precedent_researcher", run_precedent_researcher)
    graph.add_node("research_join", research_join)
    graph.add_node("witness_examiner", run_witness_examiner)
    graph.add_node("arguments_gate", arguments_gate)
    graph.add_node("plaintiff_counsel", run_plaintiff_counsel)
    graph.add_node("defense_counsel", run_defense_counsel)
    graph.add_node("juror_1", run_juror_1)
    graph.add_node("juror_2", run_juror_2)
    graph.add_node("juror_3", run_juror_3)
    graph.add_node("jury_deliberation", run_jury_deliberation)
    graph.add_node("judge", run_judge)

    # ── Phase 1: parallel entry — Investigator + Precedent Researcher ──
    graph.add_edge(START, "investigator")
    graph.add_edge(START, "precedent_researcher")

    # ── Join: research_join waits for BOTH parallel nodes above ────────
    graph.add_edge("investigator", "research_join")
    graph.add_edge("precedent_researcher", "research_join")

    # ── Phase 2: the one dynamic routing decision in this workflow ─────
    graph.add_conditional_edges(
        "research_join",
        route_after_investigation,
        {
            "witness_examiner": "witness_examiner",
            "arguments_gate": "arguments_gate",
        },
    )

    # witness_examiner converges back to the single arguments_gate funnel.
    graph.add_edge("witness_examiner", "arguments_gate")

    # ── Phase 3: parallel counsel — fans out from the single gate ──────
    graph.add_edge("arguments_gate", "plaintiff_counsel")
    graph.add_edge("arguments_gate", "defense_counsel")

    # ── Phase 4: parallel jury — 3 independent jurors ──────────────────
    graph.add_edge("plaintiff_counsel", "juror_1")
    graph.add_edge("plaintiff_counsel", "juror_2")
    graph.add_edge("plaintiff_counsel", "juror_3")
    graph.add_edge("defense_counsel", "juror_1")
    graph.add_edge("defense_counsel", "juror_2")
    graph.add_edge("defense_counsel", "juror_3")

    # ── Phase 5: deliberation + majority ───────────────────────────────
    graph.add_edge("juror_1", "jury_deliberation")
    graph.add_edge("juror_2", "jury_deliberation")
    graph.add_edge("juror_3", "jury_deliberation")

    # ── Phase 6: judge ──────────────────────────────────────────────────
    graph.add_edge("jury_deliberation", "judge")
    graph.add_edge("judge", END)

    return graph.compile()