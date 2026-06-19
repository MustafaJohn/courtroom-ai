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

## Sample Run
CLI Run: 
<img width="1833" height="630" alt="image" src="https://github.com/user-attachments/assets/d8a770c2-815d-4458-afb1-e548cf0f3389" />

Streamlit UI:
<img width="1842" height="808" alt="image" src="https://github.com/user-attachments/assets/bcad7166-bd5f-4b43-ae2a-ef0c96ed2f5c" />

There is a sample output attached in the `sample_output` directory showing the output.

```
<details>
<summary>Sample Report Excerpt</summary>

# Courtroom AI — Case Report

*Generated: 2026-06-19 20:19*

## Case Description

Case: Whitman Holdings LLC v. Carrow Construction Inc.

Whitman Holdings LLC ("Plaintiff") hired Carrow Construction Inc. ("Defendant")
to renovate a commercial office building under a signed contract dated March 3,
2024. The contract specified completion within 90 days and required the use of
fire-rated drywall throughout, per local commercial building code.

The renovation was completed 140 days after the start date. During a routine
fire inspection three months after completion, the inspector found that
standard (non-fire-rated) drywall had been installed in two stairwells,
in violation of the building code referenced in the contract. Whitman Holdings
was ordered by the city to remedy the violation at its own expense, costing
approximately $85,000 in remediation and lost rental income during the
remediation period.

Whitman Holdings is suing Carrow Construction for breach of contract, seeking
$85,000 in damages plus the contractual penalty of $500/day for the 50-day
delay beyond the 90-day deadline (totaling $25,000), for a combined claim of
$110,000.

Carrow Construction disputes liability for the drywall issue. They claim
their site foreman, Daniel Reyes, verified that fire-rated drywall was
installed in all required areas before the project was signed off. However,
Whitman's facilities manager, Priya Anand, states that during a walkthrough
before final payment, she personally observed standard drywall being
installed in the stairwells and raised a verbal concern to Reyes at the time,
which Reyes denies ever occurred. Reyes maintains no such conversation took
place and that Anand did not raise any concerns prior to signing the
completion certificate.

Carrow Construction further argues the 50-day delay was caused by a permit
processing delay at the city planning office, which they claim is an excusable
delay under the contract's force majeure clause, not a breach attributable to
Carrow.

## Investigation Findings

FACTS:
- Whitman Holdings LLC hired Carrow Construction Inc. to renovate a commercial office building under a contract dated March 3, 2024.
- The renovation was completed 140 days after the start date, and fire-rated drywall was required by the contract and local building code.

EVIDENCE:
- A fire inspection three months after completion revealed that standard drywall was installed in two stairwells, violating the building code.
- Whitman Holdings incurred $85,000 in remediation costs and lost rental income due to the violation.

GAPS:
- There is no documented evidence of the alleged conversation between Priya Anand and Daniel Reyes regarding the drywall concerns.
- The specific details of the permit processing delay and its impact on the project timeline are not provided.

DISPUTED TESTIMONY: YES

## Legal Precedent Research

> **Note:** Legal precedents cited in this report are illustrative of legal principles and have not been independently verified against case law databases.

PRECEDENT 1:
- Case name: Hurst v. Cummings Construction Co.
- Year: 2018
- Key principle: A contractor is liable for breach of contract when they fail to meet the specifications outlined in the contract, regardless of any internal verification processes.
- Outcome: The court ruled in favor of the plaintiff, holding the contractor responsible for using non-compliant materials despite claims of internal checks.
- Relevance to this case (1-10): 9 - This case directly addresses the contractor's liability for failing to use fire-rated drywall as specified in the contract.

PRECEDENT 2:
- Case name: Smith v. Greenfield Builders
- Year: 2020
- Key principle: Delays caused by external factors, such as permit processing, may be considered excusable delays under force majeure clauses, provided they are adequately documented and communicated.
- Outcome: The court found in favor of the defendant, ruling that the delay was excusable due to the unforeseen permit processing delays.
- Relevance to this case (1-10): 8 - This precedent supports Carrow Construction's defense regarding the delay, emphasizing the need for proper documentation and communication of such delays.

PRECEDENT 3:
- Case name: Johnson v. Metro Contractors
- Year: 2019
- Key principle: A party claiming damages must prove that the damages were directly caused by the breach and must provide evidence of the costs incurred.
- Outcome: The court ruled that the plaintiff failed to sufficiently demonstrate that the damages claimed were a direct result of the breach, leading to a dismissal of the claim.
- Relevance to this case (1-10): 7 - This case highlights the burden on Whitman Holdings to prove that the damages from the drywall issue and the delay were directly attributable to Carrow Construction's actions.

LEGAL PRINCIPLES:
- A contractor is liable for breach of contract when they fail to meet the specifications outlined in the contract.
- Delays caused by external factors may be considered excusable under force majeure clauses if documented and communicated properly.
- A party claiming damages must prove that the damages were directly caused by the breach and provide evidence of the costs incurred.
- Verbal communications regarding concerns about contract performance must be documented to be considered valid in disputes over contract compliance.

BURDEN OF PROOF:
- Whitman Holdings LLC must prove that Carrow Construction Inc. breached the contract by failing to use fire-rated drywall and that the damages claimed were a direct result of this breach.
- Carrow Construction Inc. must prove that the delay was caused by an excusable force majeure event and not due to their own negligence.

## Witness Examination

CONTRADICTIONS:
- Priya Anand claims she observed standard drywall being installed and raised concerns to Daniel Reyes, while Reyes denies any such conversation took place and asserts that no concerns were raised prior to signing the completion certificate.
- Carrow Construction attributes the 50-day delay to a permit processing delay, but there is no evidence provided to support this claim, creating a contradiction regarding the cause of the delay.

CREDIBILITY ISSUES:
- Daniel Reyes's credibility may be questioned due to the lack of documentation supporting his claim that fire-rated drywall was installed, as well as the absence of any witnesses to corroborate his account of the completion process.
- Priya Anand's credibility could be challenged because there is no documented evidence of her reported concerns about the drywall, which may lead to doubts about her reliability as a witness.

WEAKNESSES:
- The absence of documented evidence regarding the conversation between Anand and Reyes weakens the case for Whitman Holdings, as it relies heavily on verbal claims without corroboration.
- The lack of specific details regarding the permit processing delay and its impact on the project timeline weakens Carrow Construction's defense, as it fails to substantiate their claim of an excusable delay under the contract's force majeure clause.

## Arguments

### Plaintiff's Counsel

CLAIMS:
- Breach of contract due to the installation of non-compliant (standard) drywall instead of fire-rated drywall as specified in the contract and local building code.
- Breach of contract due to the 50-day delay in project completion beyond the agreed 90-day timeline.

DAMAGES SOUGHT: $110,000

PRECEDENTS CITED:
- Hurst v. Cummings Construction Co. (2018) — This case establishes that a contractor is liable for breach of contract when they fail to meet the specifications outlined in the contract, regardless of any internal verification processes. In this case, Carrow Construction installed non-compliant drywall, directly violating the contract's terms.
- Johnson v. Metro Contractors (2019) — This case emphasizes that a party claiming damages must prove that the damages were directly caused by the breach. Whitman Holdings must demonstrate that the remediation costs and lost rental income were a direct result of Carrow's breach regarding the drywall installation.

REASONING:
In Hurst v. Cummings Construction Co., the court ruled that the contractor was liable for using non-compliant materials, which is directly applicable to this case. Carrow Construction's installation of standard drywall instead of the required fire-rated drywall constitutes a clear breach of the contract and local building code. The inspector's findings corroborate Whitman Holdings' claim that the work was not performed according to the agreed specifications, thus establishing liability on the part of Carrow Construction.

In Johnson v. Metro Contractors, the court highlighted the necessity for the plaintiff to prove that the damages claimed were directly attributable to the breach. Whitman Holdings has incurred $85,000 in remediation costs and lost rental income due to the violation of the building code, which they must demonstrate is a direct result of Carrow's failure to comply with the contract specifications regarding drywall installation. The connection between the breach and the incurred damages is evident, as the city mandated remediation due to the violation, leading to financial losses for Whitman Holdings.

While Carrow Construction may argue that the 50-day delay was due to an excusable force majeure event, the lack of documentation regarding the permit processing delay weakens their defense. The burden is on Carrow to provide evidence supporting their claim of an excusable delay, which they have failed to do. Therefore, Whitman Holdings is justified in seeking damages for both the remediation costs and the contractual penalties associated with the delay. 

In conclusion, Whitman Holdings has a strong case for breach of contract based on the installation of non-compliant materials and the subsequent financial damages incurred, as supported by relevant legal precedents.

### Defense Counsel

REBUTTALS:
- The absence of documented evidence regarding the alleged conversation between Priya Anand and Daniel Reyes undermines Whitman Holdings' claims, as verbal assertions without corroboration do not meet the burden of proof required to establish a breach of contract.
- The claim for damages related to the drywall issue is weakened by the lack of direct evidence linking Carrow Construction's actions to the alleged violations, as established in Johnson v. Metro Contractors, where the burden was on the plaintiff to demonstrate direct causation of damages.

AFFIRMATIVE DEFENSES:
- Carrow Construction asserts that the delay in project completion was caused by an excusable force majeure event, specifically a permit processing delay at the city planning office, which is supported by the precedent set in Smith v. Greenfield Builders.
- Carrow Construction argues that they fulfilled their contractual obligations by verifying compliance with the specifications prior to project sign-off, thereby mitigating liability for the alleged drywall issue.

PRECEDENTS CITED:
- Hurst v. Cummings Construction Co. (2018)
- Smith v. Greenfield Builders (2020)
- Johnson v. Metro Contractors (2019)

REASONING:
In defending Carrow Construction Inc. against the claims of Whitman Holdings LLC, it is crucial to emphasize the lack of documented evidence supporting the plaintiff's assertions. The absence of any written record of the alleged conversation between Priya Anand and Daniel Reyes regarding the drywall concerns significantly undermines Whitman's case. As established in Johnson v. Metro Contractors, the burden of proof lies with the plaintiff to demonstrate that the damages claimed were directly attributable to the defendant's breach. Without concrete evidence, Whitman's claims remain speculative.

Furthermore, Carrow Construction's defense hinges on the argument that the 50-day delay in project completion was due to an excusable force majeure event, specifically a permit processing delay. This is consistent with the precedent set in Smith v. Greenfield Builders, where the court recognized that external factors could justify delays if properly documented. The lack of specific details regarding the permit processing delay, however, does create a challenge for Carrow, but it does not negate the potential for an excusable delay under the contract.

Lastly, while Hurst v. Cummings Construction Co. establishes that contractors are liable for failing to meet contract specifications, Carrow Construction's internal verification process and the absence of documented complaints from Whitman Holdings suggest that they acted in good faith and complied with the contract to the best of their ability. This context should be considered when evaluating the overall liability in this case.

## Jury Deliberation

**Majority verdict:** Plaintiff

| Juror | Initial Verdict | Final Verdict | Confidence (before → after) | Changed? |
|---|---|---|---|---|
| Strict Constructionist | Plaintiff | Plaintiff | 8 → 9 | — No |
| Liberal Humanist | Plaintiff | Plaintiff | 8 → 8 | — No |
| Pragmatic Moderate | Plaintiff | Plaintiff | 7 → 8 | — No |

#### Strict Constructionist (juror_1)

- **Initial verdict:** Plaintiff (confidence 8/10)
- **Final verdict:** Plaintiff (confidence 9/10)

**Initial reasoning:** In conclusion, the evidence clearly demonstrates that Carrow Construction breached the contract by using standard drywall instead of the required fire-rated drywall, leading to significant financial damages for Whitman Holdings LLC. The lack of sufficient documentation to support Carrow's defense further strengthens the Plaintiff's case. Therefore, I maintain my verdict in favor of the Plaintiff, with increased confidence in the merits of their claims.

**Rebuttal after hearing peers:** I appreciate both jurors' agreement on the breach of contract by Carrow Construction due to the use of non-compliant drywall. Juror_2's point about the lack of documentation supporting Carrow's claims regarding the permit processing issue reinforces my stance. I also agree with Juror_3 that while the absence of evidence concerning the conversation between Priya Anand and Daniel Reyes introduces some uncertainty, it does not overshadow the clear violation of contract terms regarding drywall installation. 

However, I would like to address Juror_3's confidence level of 7, which suggests a slight hesitance. I believe that the strong evidence of the fire inspector's findings and the direct link between Carrow's actions and the damages incurred should bolster confidence in the Plaintiff's case. The precedents cited, particularly Hurst v. Cummings Construction Co., further support the notion that contractors are held liable for failing to meet explicit contract specifications.

#### Liberal Humanist (juror_2)

- **Initial verdict:** Plaintiff (confidence 8/10)
- **Final verdict:** Plaintiff (confidence 8/10)

**Initial reasoning:** In conclusion, the evidence clearly demonstrates that Carrow Construction Inc. breached the contract by installing non-compliant drywall, which led to significant financial damages for Whitman Holdings LLC. The lack of sufficient documentation from Carrow regarding their defense further supports the Plaintiff's claims. Therefore, I maintain my verdict in favor of the Plaintiff, as the breach and the resulting damages are well substantiated by the evidence presented.

**Rebuttal after hearing peers:** I appreciate the thoroughness of both jurors' arguments, particularly the emphasis on the explicit requirement for fire-rated drywall in the contract. Juror_1 states, "the contract between Whitman Holdings LLC and Carrow Construction Inc. explicitly required the use of fire-rated drywall," which aligns with my original reasoning. I agree with this point as it underscores the clear breach of contract by Carrow Construction. Juror_3 also highlights the connection between the breach and the damages, noting that "the fire inspector's findings corroborate Whitman Holdings LLC's claims," which reinforces my view that the evidence strongly supports the Plaintiff's position.

However, I find Juror_3's mention of uncertainty regarding the conversation between Priya Anand and Daniel Reyes to be somewhat overstated. While the lack of documentation is indeed a concern, it does not significantly impact the clear breach of contract regarding the drywall installation. Both jurors effectively argue that Carrow's failure to provide documentation for their permit delay claim weakens their defense, which I fully support.

#### Pragmatic Moderate (juror_3)

- **Initial verdict:** Plaintiff (confidence 7/10)
- **Final verdict:** Plaintiff (confidence 8/10)

**Initial reasoning:** In conclusion, the evidence presented confirms that Carrow Construction Inc. breached the contract by using non-compliant drywall, which directly resulted in significant financial damages for Whitman Holdings LLC. The failure to provide adequate documentation regarding the alleged permit issues further solidifies the case against Carrow. Therefore, I find in favor of the Plaintiff, Whitman Holdings LLC, and support their claim for damages related to the breach of contract.

**Rebuttal after hearing peers:** I appreciate the thoroughness of both jurors' arguments, particularly the emphasis on the clear breach of contract due to the installation of non-compliant drywall. I agree with both Strict Constructionist and Liberal Humanist that the evidence strongly supports the claim that Carrow Construction Inc. violated the contract terms, as highlighted by the fire inspector's findings. The point made by both jurors regarding the burden of proof lying with Carrow Construction to justify the delay is particularly compelling. I also concur that the lack of documentation regarding the alleged permit delay significantly weakens Carrow's defense.

However, I would like to emphasize that while the absence of evidence regarding the conversation between Priya Anand and Daniel Reyes creates some uncertainty, it does not detract from the overwhelming evidence of the breach itself. My original confidence level was a 7, and after considering the strong alignment of reasoning among my fellow jurors, I feel more assured in my position.

## Judge's Ruling

DECISION: Agree  
FINAL VERDICT: Plaintiff  
DAMAGES: $110,000  
REASONING: The jury's majority verdict aligns with the evidence presented in the case. Carrow Construction's failure to install fire-rated drywall, as specified in the contract and required by local building codes, constitutes a clear breach of contract. The fire inspector's findings corroborate Whitman Holdings' claims, establishing a direct link between Carrow's actions and the damages incurred, which include $85,000 in remediation costs and lost rental income. 

The jury correctly noted that Carrow Construction did not provide sufficient documentation to support their claim of an excusable delay due to permit processing issues, which further solidifies the case against them. The precedents cited, particularly Hurst v. Cummings Construction Co., support the conclusion that contractors are liable for failing to meet explicit contract specifications. Therefore, I find the jury's reasoning sound and agree with their verdict in favor of the Plaintiff, Whitman Holdings LLC.

---

*This report was generated by a multi-agent AI system for demonstration purposes and does not constitute legal advice.*
</details>
```
---
 
## Technical Notes
 
Error handling — `core/llm.py` retries API calls up to 3 times with exponential backoff (2s → 4s → 8s) on transient failures (timeout, rate limit, API error). The top-level CLI catches unrecoverable failures and exits with a clear message.
