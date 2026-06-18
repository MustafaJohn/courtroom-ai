"""
Streamlit UI for the courtroom multi-agent system.
Thin presentation layer only — reuses build_workflow() and generate_report()
directly from the CLI codebase. No duplicated agent or graph logic.

Run locally:
    streamlit run streamlit_app.py

Run via Docker Compose:
    docker compose --profile ui up
"""

import streamlit as st

from core.report import generate_report
from graph.workflow import build_workflow
from graph.router import NODE_LABELS

st.set_page_config(page_title="Courtroom AI", page_icon="⚖️", layout="centered")

st.title("⚖️ Courtroom AI")
st.caption(
    "A multi-agent system simulating a law firm case review — "
    "Investigator, Precedent Researcher, Witness Examiner, both Counsels, "
    "a 3-juror panel, and a Judge."
)

# ── Input ────────────────────────────────────────────────────────────────
case_description = st.text_area(
    "Case description",
    height=220,
    placeholder=(
        "Describe the case: who the parties are, what happened, "
        "what's disputed, and what's being claimed..."
    ),
)

uploaded_file = st.file_uploader("...or upload a case file (.txt)", type=["txt"])
if uploaded_file is not None:
    case_description = uploaded_file.read().decode("utf-8")
    st.text_area("Loaded case description", value=case_description, height=220, disabled=True)

run_clicked = st.button("Run Case", type="primary", disabled=not case_description.strip())

# ── Execution ────────────────────────────────────────────────────────────
if run_clicked:
    app = build_workflow()
    initial_state = {
        "case_description": case_description.strip(),
        "juror_votes": [],
    }

    progress_container = st.container(border=True)
    progress_container.markdown("**Workflow progress**")
    progress_log = progress_container.empty()
    deliberation_box = st.empty()

    final_state = dict(initial_state)
    log_lines = []

    try:
        with st.spinner("Running case through the courtroom..."):
            for step in app.stream(initial_state, stream_mode="updates"):
                for node_name, node_output in step.items():
                    label = NODE_LABELS.get(node_name)
                    if label:
                        log_lines.append(f"✓ {label}")
                        progress_log.markdown("\n\n".join(log_lines))
                    final_state.update(node_output or {})

                    if node_name == "jury_deliberation" and node_output.get("deliberation_log"):
                        deliberation_box.markdown(
                            "**Jury rebuttal round — before → after**\n\n```\n"
                            + node_output["deliberation_log"]
                            + "\n```"
                        )
    except RuntimeError as e:
        st.error(f"Workflow failed: {e}")
        st.stop()

    st.success(f"Done. Jury majority: **{final_state.get('jury_majority', 'N/A')}**")

    report = generate_report(final_state)

    st.divider()
    st.markdown(report)

    st.download_button(
        label="Download report as Markdown",
        data=report,
        file_name="report.md",
        mime="text/markdown",
    )