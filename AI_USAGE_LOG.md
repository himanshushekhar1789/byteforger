# AI Usage Log

This document records significant AI-assisted decisions and implementation work performed during the hackathon.

---

## Entry 1 — Project Architecture and Data Layer

### Goal

Understand the architecture of the AI Interview Agent and establish the initial data layer.

### AI Assistance

AI assistance was used to:

- Analyze the hackathon problem statement.
- Design a simple backend architecture for the interview agent.
- Determine how candidate profiles and curriculum data should be connected.
- Recommend separating data loading from API and interview logic.
- Generate the initial implementation of `data_loader.py`.

### Implementation

Created `data_loader.py` to load:

- `data/candidates.json`
- `data/curriculum.json`

The loader uses Python's JSON functionality and `pathlib` to locate the project's data directory reliably.

### Validation

Tested the loader against the provided hackathon data.

Result:

- 20 candidates loaded successfully.
- 31 curriculum days loaded successfully.

During testing, the candidate JSON structure was discovered to contain a top-level `candidates` key. The loader was adjusted to return the actual candidate list from that key.

### Human Decisions

The project uses a simple file-based data layer rather than introducing a database because the hackathon explicitly provides synthetic candidate and curriculum data and does not require persistent accounts or a production database.

The implementation was tested locally before being accepted.