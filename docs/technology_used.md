# Technology Used

**Project:** Online Safety Companion

---

## IBM watsonx Orchestrate

The entire multi-agent system runs on **IBM watsonx Orchestrate** using the
native ADK (Agent Development Kit).

### Agent architecture

Three agents are deployed:

| Agent | Role | Type |
|---|---|---|
| `online_safety_companion` | Orchestrator. Manages conversation flow, gathers context, coordinates sub-agents, writes the final reply. | Supervisor / orchestrator |
| `safety_agent` | Analyzes message content for risk signals. Calls `risk_scorer` tool and cross-references the knowledge base. Returns a structured risk assessment. | Collaborator |
| `support_agent` | Translates the risk assessment into plain language. Generates 2–3 options and a draft message to a trusted adult. | Collaborator |

### Tool

`risk_scorer` is a Python function registered with the ADK `@tool` decorator.
It applies rule-based regex pattern matching to detect:
- Platform migration pressure (e.g. Discord → Telegram)
- Secrecy from parents or family
- Isolation language
- Money, gift card, and cryptocurrency requests
- Photo and video requests
- Fake urgency
- Too-good-to-be-true offers
- Love-bombing and excessive flattery
- Personal information requests
- In-person meeting requests
- Sextortion / leverage with existing content
- Inconsistent identity claims

The tool returns `risk_level` (low / medium / high), `signals` (list), and
`recommended_next_steps` (list).

### Knowledge base

Three Markdown documents are loaded into the watsonx Orchestrate knowledge store:
- `grooming_warning_signs.md` — pattern-level grooming indicators
- `scam_patterns.md` — romance scams, gift-card scams, sextortion, job scams
- `what_to_do_next.md` — evidence preservation, reporting resources, crisis lines

### LLM

All three agents use **ibm/granite-3-3-8b-instruct** via watsonx Orchestrate's
built-in model routing.

---

## IBM Bob

**IBM Bob** (IBM's AI coding assistant) was used throughout development:

| Task | How Bob was used |
|---|---|
| Agent YAML design | Bob drafted all three ADK agent YAML files, checked instruction completeness, and identified missing guardrails |
| Tool development | Bob generated `risk_scorer.py` with all 12 signal detection rule groups, type hints, docstrings, and the `@tool` decorator |
| Knowledge base | Bob authored all three knowledge Markdown files, deliberately keeping content at pattern level to avoid producing material that could be repurposed |
| Test suite | Bob wrote 8 test conversations (`test_cases.md`) and the full `test_risk_scorer.py` pytest suite including edge cases |
| Documentation | Bob drafted `README.md`, `problem_solution.md`, `demo_script.md`, and this file |
| Review | Bob reviewed the `online_safety_companion` agent for logical gaps, redundant questions, missing escalation paths, and rule consistency |

Bob was used inside VS Code via the Bob extension, with the workspace set to
this project repository.

---

## Other technologies

| Technology | Usage |
|---|---|
| Python 3.10+ | `risk_scorer.py` tool and `test_risk_scorer.py` |
| pytest | Unit testing of the risk scorer tool |
| Bash | `deploy.sh` deployment script |
| Markdown | Knowledge base documents |
| Mermaid | Architecture diagram in README |
