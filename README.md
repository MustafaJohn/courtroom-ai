# courtroom-ai
This is a project which uses AI agents to simulate a courtroom environment

File Structure
courtroom-ai/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── main.py
├── agents/
│   ├── __init__.py
│   ├── investigator.py
│   ├── precedent_researcher.py
│   ├── witness_examiner.py
│   ├── plaintiff_counsel.py
│   ├── defense_counsel.py
│   ├── jury.py
│   └── judge.py
├── graph/
│   ├── __init__.py
│   ├── state.py
│   ├── workflow.py
│   └── router.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── llm.py
│   ├── prompts.py
│   └── report.py
├── cases/
│   └── contract_dispute.txt
├── output/
│   └── .gitkeep
└── tests/
    ├── __init__.py
    └── test_agents.py

<img width="1440" height="1240" alt="image" src="https://github.com/user-attachments/assets/dcea1545-038f-4869-9997-3d5e77bf093b" />

