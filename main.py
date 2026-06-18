"""
CLI entry point for the courtroom multi-agent system.

Usage:
    python main.py --case "Smith sues Jones for breach of contract..."
    python main.py --case-file cases/contract_dispute.txt
"""

import argparse
import sys
import time
from pathlib import Path

from core.config import settings
from core.report import generate_report
from graph.workflow import build_workflow
from graph.router import NODE_LABELS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a case through the courtroom multi-agent system."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--case", type=str, help="Case description as a string.")
    group.add_argument("--case-file", type=str, help="Path to a text file containing the case description.")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path for the Markdown report (default: output/report.md).",
    )
    parser.add_argument(
        "--print-report",
        action="store_true",
        help="Print the full report to stdout in addition to saving it.",
    )
    return parser.parse_args()


def load_case_description(args: argparse.Namespace) -> str:
    if args.case:
        return args.case.strip()

    case_path = Path(args.case_file)
    if not case_path.exists():
        print(f"Error: case file not found: {case_path}", file=sys.stderr)
        sys.exit(1)

    text = case_path.read_text(encoding="utf-8").strip()
    if not text:
        print(f"Error: case file is empty: {case_path}", file=sys.stderr)
        sys.exit(1)
    return text


def run_with_progress(app, initial_state: dict) -> dict:
    """
    Streams the graph execution node-by-node, printing a friendly progress
    line as each agent completes. Returns the final accumulated state.
    """
    final_state = dict(initial_state)
    start_time = time.time()

    for step in app.stream(initial_state, stream_mode="updates"):
        for node_name, node_output in step.items():
            label = NODE_LABELS.get(node_name)
            if label:
                elapsed = time.time() - start_time
                print(f"  [{elapsed:5.1f}s] ✓ {label}")
            final_state.update(node_output or {})

            if node_name == "jury_deliberation" and node_output.get("deliberation_log"):
                print("\n  ── Jury rebuttal round: before → after ──")
                for line in node_output["deliberation_log"].splitlines():
                    print(f"    {line}")
                print()

    total_time = time.time() - start_time
    print(f"\nCompleted in {total_time:.1f}s\n")
    return final_state


def main() -> None:
    args = parse_args()
    case_description = load_case_description(args)

    print("Running case through courtroom multi-agent system...\n")

    app = build_workflow()
    initial_state = {
        "case_description": case_description,
        "juror_votes": [],
    }

    try:
        final_state = run_with_progress(app, initial_state)
    except RuntimeError as e:
        print(f"\nError: workflow failed — {e}", file=sys.stderr)
        sys.exit(1)

    report = generate_report(final_state)

    output_path = Path(args.output) if args.output else Path(settings.output_dir) / "report.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    print(f"Jury majority: {final_state.get('jury_majority', 'N/A')}")
    print(f"Report saved to: {output_path}")

    if args.print_report:
        print("\n" + report)


if __name__ == "__main__":
    main()