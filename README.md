# courtroom-ai

A multi-agent AI system that simulates a law firm case review workflow. Given a case description, 9 specialized agents collaborate to investigate facts, research legal precedents, argue both sides, deliberate as a jury, and issue a final judge's ruling — all documented in an explainable Markdown report.

<img width="1440" height="1240" alt="image" src="https://github.com/user-attachments/assets/dcea1545-038f-4869-9997-3d5e77bf093b" />

### Agents
 
| # | Agent | Role |
|---|---|---|
| 1 | **Investigator** | Extracts facts, evidence, and gaps. Flags disputed testimony to trigger dynamic routing. |
| 2 | **Precedent Researcher** | Finds relevant legal principles and 4 illustrative precedents (plaintiff and defense-favoring). |
| 3 | **Witness Examiner** | *Conditional* — only runs when disputed testimony is flagged. Cross-examines contradictions and credibility issues. |
| 4 | **Plaintiff's Counsel** | Builds the strongest case for the plaintiff using all upstream findings. |
| 5 | **Defense Counsel** | Builds the strongest case for the defendant using all upstream findings. |
| 6–8 | **Jurors 1–3** | Three distinct personas (Strict Constructionist, Liberal Humanist, Pragmatic Moderate) cast independent parallel verdicts, then read each other's reasoning and issue a final verdict after one rebuttal round. |
| 9 | **Judge** | Reviews the jury's deliberation. May AGREE with the majority, DISSENT (disagreeing with reasoning while upholding the verdict), or OVERRIDE (changing the outcome with legal justification). |
 
### Key Design Decisions
 
**Dynamic routing** — whether the Witness Examiner runs is determined at runtime by the Investigator's output, not hardcoded. This is the core non-linear routing requirement.
 
**Join nodes** — `research_join` and `arguments_gate` are passthrough nodes that ensure parallel branches converge cleanly before downstream agents fire. Without them, agents with two incoming edges fire once per edge (double-fire bug — discovered and fixed during smoke testing).
 
**Parallel execution** — Investigator + Precedent Researcher run in parallel (Phase 1). Plaintiff + Defense Counsel run in parallel (Phase 3). All 3 Jurors run in parallel (Phase 4).
 
**Inter-agent collaboration** — the jury rebuttal round is the clearest example: each juror reads the other two jurors' actual reasoning and may change their verdict based on it. State changes are tracked before/after and shown in both the CLI and report.

**Framework choice:** LangGraph
- Stateful, typed state management (`CaseState`)
- Native support for conditional edges (dynamic routing)
- Parallel execution without additional orchestration
- Passthrough join nodes for fan-in convergence
- Better suited for this workflow than CrewAI (fine-grained control over state and routing)

**Hallucination mitigation** — the Precedent Researcher prompt explicitly instructs the model not to present cases as definitively verified. The generated report includes a disclaimer. In a production system, this agent would be replaced with a CourtListener or Westlaw API integration.
 
**Model** — `gpt-4o-mini` by default. Configurable via `MODEL` in `.env`.
 
---
 
## Setup
 
### Prerequisites
- Docker + Docker Compose, OR Python 3.11+
- OpenAI API key
### 1. Clone and configure
 
```bash
git clone <repo-url>
cd courtroom-ai
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```
 
### 2. Run with Docker (recommended)
 
```bash
# CLI — run the sample case
docker compose run courtroom-ai --case-file cases/contract_dispute.txt
 
# CLI — pass a case directly
docker compose run courtroom-ai --case "Smith v. Jones: plaintiff claims..."
 
# Streamlit UI
docker compose --profile ui up courtroom-ui
# Then open http://localhost:8501
```
 
### 3. Run locally (without Docker)
 
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
 
# CLI
python main.py --case-file cases/contract_dispute.txt
 
# Streamlit UI
streamlit run streamlit_app.py
```
 
---
 
## Usage
 
### CLI
 
```bash
python main.py --case-file cases/contract_dispute.txt
python main.py --case "Whitman Holdings sues Carrow Construction..."
python main.py --case-file cases/contract_dispute.txt --output output/my_report.md
```
 
### Streamlit UI
 
Open `http://localhost:8501`, paste or upload a case description, and click **Run Case**. Progress updates stream live as each agent completes. The full report renders inline with a download button.
 
### Adding a new case
 
Create a `.txt` file in `cases/` with a plain English description of the case — who the parties are, what happened, what's disputed, and what's being claimed. No special format required.
 
---
 
## Project Structure
 
```
courtroom-ai/
├── agents/
│   ├── investigator.py          # Agent 1
│   ├── precedent_researcher.py  # Agent 2
│   ├── witness_examiner.py      # Agent 3 (conditional)
│   ├── plaintiff_counsel.py     # Agent 4
│   ├── defense_counsel.py       # Agent 5
│   ├── jury.py                  # Agents 6–8 + deliberation
│   └── judge.py                 # Agent 9
├── graph/
│   ├── state.py                 # CaseState TypedDict — shared memory
│   ├── workflow.py              # StateGraph builder
│   └── router.py                # Conditional edge logic + NODE_LABELS
├── core/
│   ├── config.py                # Pydantic settings (reads .env)
│   ├── llm.py                   # OpenAI client with retry + timeout
│   ├── prompts.py               # All system prompts in one place
│   └── report.py                # Markdown report renderer
├── cases/
│   └── contract_dispute.txt     # Sample case
├── output/                      # Generated reports (gitignored)
├── main.py                      # CLI entry point
├── streamlit_app.py             # Streamlit UI
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
 
---
 
## Output
 
The system generates a structured Markdown report saved to `output/report.md` containing:
 
- Case description
- Investigation findings (facts, evidence, gaps)
- Legal precedent research (4 precedents with relevance scores, burden of proof)
- Witness examination (if triggered)
- Both counsels' full arguments
- Jury deliberation — before/after table showing verdict and confidence changes per juror
- Judge's final ruling with legal reasoning
> **Note:** Legal precedents are illustrative of legal principles and have not been independently verified against case law databases. This system is for demonstration purposes and does not constitute legal advice.
 
---
 
## Technical Notes
 
Error handling — `core/llm.py` retries API calls up to 3 times with exponential backoff (2s → 4s → 8s) on transient failures (timeout, rate limit, API error). The top-level CLI catches unrecoverable failures and exits with a clear message.
