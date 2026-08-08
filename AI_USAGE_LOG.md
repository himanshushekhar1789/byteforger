# AI Usage Log

This document records significant AI-assisted decisions and implementation
work performed during the ByteForger hackathon.

AI was used as a development assistant for architecture discussions,
implementation guidance, debugging, interview logic, API design,
optimization, documentation, testing, and final project validation.

The final implementation decisions were reviewed, modified, tested, and
accepted by the developer.

---

## Entry 1 - Project Architecture and Data Layer

### Goal

Understand the architecture of the AI Interview Agent and establish the
initial data layer.

### AI Prompt

> Help me understand the architecture of the AI Interview Agent. I need to
> connect candidate profiles with curriculum data and build a simple backend
> that can load the provided hackathon data.

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

The loader uses Python's JSON functionality and `pathlib` to locate the
project data directory reliably.

### Validation

Tested the loader against the provided hackathon data.

Result:

- 20 candidates loaded successfully.
- 31 curriculum days loaded successfully.

During testing, the candidate JSON structure was discovered to contain a
top-level `candidates` key. The loader was adjusted to return the actual
candidate list from that key.

### Human Decisions

The project uses a simple file-based data layer rather than introducing a
database because the hackathon provides synthetic candidate and curriculum
data and does not require persistent accounts or a production database.

---

## Entry 2 - Interview State and Session Management

### Goal

Create a state object that can maintain an interview session across multiple
questions and candidate answers.

### AI Prompt

> I need an InterviewState class for my technical interview agent. It should
> track the session, candidate, interview plan, questions asked, curriculum
> days covered, answers, conversation history, and the current topic. It
> should also determine when the interview has reached minimum coverage.

### AI Assistance

AI assistance was used to design the interview state model and identify the
information that needs to persist throughout an interview.

### Implementation

Implemented `InterviewState` in `interview_state.py`.

The state tracks:

- `session_id`
- Candidate information
- Interview plan
- `questions_asked`
- `days_covered`
- `conversation_history`
- Current curriculum topic
- Follow-ups per curriculum day

### Validation

Tested sessions by adding questions and answers and checking:

- Question count
- Covered curriculum days
- Conversation history
- Current topic
- Minimum coverage

### Human Decisions

In-memory session storage was selected because persistent database storage
was not required for the hackathon.

---

## Entry 3 - Interview Planning

### Goal

Generate an interview plan based on candidate information, completed
missions, role relevance, curriculum priority, and learning signals.

### AI Prompt

> I need an interview planner that takes a candidate profile and curriculum
> information and produces a prioritized interview plan. How should I rank
> curriculum topics using role relevance, priority, and whether the candidate
> has already completed the topic?

### AI Assistance

AI assistance was used to reason about:

- Candidate-specific topic selection
- Priority ordering
- Role relevance
- Completed versus skipped missions
- Avoiding irrelevant curriculum topics
- Producing a manageable interview plan

### Implementation

Implemented `interview_planner.py`.

The planner generated a candidate-specific prioritized curriculum plan.

### Validation

The planner was executed against the provided candidate data and produced
a prioritized list of curriculum days.

### Human Decisions

The planner prioritizes technically relevant topics while still allowing
broader curriculum coverage.

---

## Entry 4 - Adaptive Follow-Up Questions

### Goal

Make the interview conversational instead of asking only a fixed sequence of
questions.

The interviewer should decide whether a candidate's answer deserves a
follow-up question or whether it should move to another curriculum topic.

### AI Prompt

> I want my technical interview agent to decide whether the candidate's
> latest answer deserves a follow-up on the same curriculum topic. What
> criteria should I use to decide between FOLLOW_UP and MOVE_ON?

### AI Assistance

AI assistance was used to design follow-up decision criteria.

A follow-up can be useful when:

- The candidate makes an interesting technical claim.
- The answer contains a weakness or missing detail.
- The candidate mentions a trade-off worth exploring.
- Clarification would provide additional evidence of understanding.

The interviewer should move on when:

- The answer is sufficiently complete.
- There is little useful information to probe.
- Another curriculum topic should be assessed.

### Implementation

Implemented adaptive follow-up behavior in `interview_agent.py`.

The system evaluates the candidate's answer and determines whether to:

```text
FOLLOW_UP
Entry 5 - Follow-Up Limits and Minimum Coverage
Goal

Prevent the interviewer from spending too much time on one topic while
ensuring that enough curriculum topics are covered.

AI Prompt

I want to prevent my adaptive interviewer from asking unlimited follow-up
questions on the same topic. How can I track follow-ups per curriculum day
and move to the next topic after a reasonable limit?

AI Assistance

AI assistance suggested maintaining a follow-up counter for each curriculum
day and using the counter when deciding whether another follow-up is allowed.

Implementation

The interview state was extended to track follow-ups per curriculum day.

The interview allows a maximum of two follow-ups for a curriculum day.

Minimum interview coverage was defined as:

8 questions
AND
4 curriculum days
Validation

A complete interview test produced:

Questions asked: 10
Curriculum days covered: 4
Days: [7, 8, 10, 12]
Follow-ups per day: {10: 2, 12: 2, 7: 2}
Minimum requirements: PASSED
Human Decisions

The limits were chosen to balance:

Exploring interesting candidate answers.
Preventing the interview from getting stuck on one topic.
Ensuring multiple curriculum areas are assessed.
Entry 6 - Reducing LLM API Calls
Goal

Reduce the number of LLM requests made during an interview.

AI Prompt

I have a technical interview agent where one LLM call decides whether to
ask a follow-up and another LLM call generates the question. This is causing
too many API requests. How can I combine these into one LLM call?

AI Assistance

AI assistance suggested combining the decision and question generation into
one structured LLM response.

The model could return information equivalent to:

{
  "decision": "FOLLOW_UP",
  "question": "..."
}

or:

{
  "decision": "MOVE_ON",
  "question": "..."
}
Implementation

The interview logic was adjusted so one model request could analyze the
candidate answer, decide whether a follow-up was appropriate, and generate
the next question.

Validation

The interview continued to produce relevant follow-up questions while
reducing unnecessary model calls.

Human Decisions

This optimization became important because the available LLM quota was
limited.

Entry 7 - Gemini to Groq Migration
Goal

Replace the original Gemini integration after the available Gemini quota
became a practical limitation during development and testing.

AI Prompt

The Gemini API is returning a 429 quota error and the free quota is too
limited for repeated interview testing. What alternatives can I use, and
how can I migrate the LLM client without changing the rest of my interview
agent?

AI Assistance

AI assistance helped evaluate alternative LLM providers and suggested
migrating the model client to Groq.

Implementation

The project was migrated to the Groq Python client.

The rest of the application continues to use:

generate_response(prompt)

This keeps provider-specific implementation isolated inside llm_client.py.

Validation

The Groq client was tested successfully.

The interview was then tested with:

Initial questions
Follow-up questions
Curriculum transitions
Final feedback
Human Decisions

Groq was selected to make repeated development testing practical within the
available token limits.

The API key is stored in .env and excluded from Git using .gitignore.

Entry 8 - Structured Final Interview Feedback
Goal

Make final interview feedback machine-readable so that it can be returned
cleanly through the API.

AI Prompt

My final interview feedback currently returns plain text with sections for
summary, strengths, gaps, and next steps. Change the output so the LLM
returns valid JSON that my FastAPI backend can parse.

AI Assistance

AI assistance recommended asking the LLM to return only valid JSON using a
fixed schema:

{
  "summary": "...",
  "strengths": [],
  "gaps": [],
  "next": []
}

The model was instructed not to return Markdown or additional explanation
outside the JSON.

Implementation

generate_final_feedback() was changed to:

Generate structured feedback.
Receive the model response.
Parse the response using json.loads().
Return the resulting Python dictionary.
Validation

The feedback function was tested with a simulated interview conversation.

The returned value was confirmed to be a Python dictionary containing:

summary
strengths
gaps
next

The API was also tested and successfully returned structured feedback with
done: true.

Human Decisions

Structured JSON was selected because it is easier for an API client or
frontend to consume than unstructured text.

Entry 9 - FastAPI Interview API
Goal

Expose the interview agent through an HTTP API.

AI Prompt

I have a working Python interview agent. I need to expose it through
FastAPI using POST /api/interview. The first request should start an
interview using a sessionId and candidate, and subsequent requests should
use the same sessionId with the candidate's message.

AI Assistance

AI assistance was used to design:

The Pydantic request model
Session-based request handling
Start-interview behavior
Continue-interview behavior
Completion responses
Error handling
Implementation

Added:

POST /api/interview

with:

class InterviewRequest(BaseModel):
    sessionId: str
    candidate: dict | None = None
    message: str | None = None

The API flow is:

First request
    |
    v
sessionId + candidate
    |
    v
Start interview
    |
    v
Return question

Subsequent request
    |
    v
sessionId + message
    |
    v
Process answer
    |
    v
Return next question

When minimum coverage is reached:

Interview completed
    |
    v
Structured feedback
Validation

The endpoint was tested using FastAPI's TestClient.

The following behavior was confirmed:

First request
    -> HTTP 200
    -> Interview question
    -> done: false

Second request
    -> HTTP 200
    -> Follow-up question
    -> done: false

Completed interview
    -> HTTP 200
    -> Structured feedback
    -> done: true
Human Decisions

The API layer was kept thin and delegates interview behavior to the existing
interview engine.

Entry 10 - API Session Validation
Goal

Verify that the API correctly distinguishes between a new interview session
and an existing interview session.

AI Prompt

I tested my POST /api/interview endpoint. The first request works, but when
I send the candidate's answer I get "candidate is required when starting an
interview." Help me reason about whether the session state is being reused
correctly.

AI Assistance

AI assistance helped identify that the same sessionId must be reused across
requests and that the first request must create the interview state.

Implementation

The API was tested using two sequential requests with the same session ID:

Request 1:
sessionId + candidate

Request 2:
sessionId + message
Validation

The test successfully produced:

FIRST STATUS: 200
FIRST RESPONSE: interview question

SECOND STATUS: 200
SECOND RESPONSE: follow-up question

This confirmed that session state was being reused correctly.

Human Decisions

The candidate is required only when starting a new session. Existing
sessions require the sessionId and candidate message.

Entry 11 - README and Dependency Documentation
Goal

Make the project understandable and runnable by another developer.

AI Prompt

Create a concise README for ByteForger explaining what the project does,
its features, architecture, project structure, setup instructions,
environment variables, API usage, testing, and AI usage documentation.

AI Assistance

AI assistance was used to organize the documentation into:

Project overview
Features
Architecture
Project structure
Setup
Environment variables
API usage
Testing
AI usage documentation
Implementation

Added:

README.md
requirements.txt

The README explains how to:

Create a virtual environment.
Activate the environment.
Install dependencies.
Configure the Groq API key.
Start the FastAPI server.
Access /docs.
Use /api/interview.
Run the interview test.
Validation

The dependencies were tested using:

pip install -r requirements.txt

All required packages were available in the development environment.

Human Decisions

The documentation was kept focused on the actual hackathon implementation.

Entry 12 - Secret Protection
Goal

Ensure the Groq API key is not committed to the Git repository.

AI Prompt

I accidentally placed an API key in a README while preparing the project.
What should I do before pushing the repository to GitHub?

AI Assistance

AI assistance recommended treating the exposed key as compromised, removing
it from the README, revoking the exposed key, and keeping the replacement key
only in .env.

Implementation

The exposed key was removed and the old key was revoked.

The README now contains only:

GROQ_API_KEY=your_groq_api_key_here

The real API key is stored locally in .env.

.env is listed in .gitignore.

Validation

Git was checked using:

git check-ignore -v .env

The result confirmed that .env is ignored.

Human Decisions

API credentials are intentionally kept outside the repository and are never
included in source code, README documentation, or committed files.

Entry 13 - Final Repository Validation
Goal

Verify that the project is stable and ready for final hackathon submission.

AI Prompt

Help me perform a final audit of my ByteForger project. I want to verify
that the API works, the final feedback is structured correctly, the
repository is clean, secrets are not committed, and the required
documentation is present.

AI Assistance

AI assistance was used to create a final verification checklist covering:

FastAPI application loading
/api/interview route availability
Interview state behavior
Minimum coverage
Structured feedback
.env protection
Git status
README
requirements.txt
AI usage documentation
Validation

The following were successfully verified:

FastAPI application loads successfully.
POST /api/interview exists.
Multi-turn interview sessions work.
Adaptive follow-up questions work.
Minimum coverage is reached correctly.
Structured final feedback is returned.
.env is ignored by Git.
Working tree is clean after commits.
README and requirements are present.
Changes were pushed successfully to GitHub.
Human Decisions

The project was intentionally kept focused on the required backend/API
functionality.

A frontend may be added later if sufficient time remains, primarily to improve
the demonstration experience.

Entry 14 - Optional Frontend Planning
Goal

Consider whether a frontend should be added to improve the final hackathon
demonstration.

AI Prompt

The backend interview API is working. Would a simple frontend improve the
hackathon demo, and approximately how much time would it take to build one
without changing the backend?

AI Assistance

AI assistance suggested that a lightweight frontend could improve the visual
quality of the demonstration while keeping the existing API unchanged.

A possible interface would contain:

Candidate information
Interviewer question
Candidate answer input
Submit button
Interview progress
Final feedback
Implementation Status

The frontend is an optional enhancement rather than a core requirement.

The backend API remains the primary implementation.

Human Decisions

The decision was made to complete all mandatory requirements first.

If sufficient time remains before submission, a lightweight HTML/CSS/JavaScript
frontend may be added to improve the demo video.

No frontend work should compromise the stability of the completed backend.

Final Summary

AI assistance was used throughout ByteForger as a development assistant for:

Architecture exploration
Data loading
Interview planning
State management
Adaptive follow-up logic
Curriculum coverage
API-call optimization
LLM provider migration
Structured feedback
FastAPI integration
Debugging
Testing
Documentation
Security checks
Final repository validation

The developer reviewed, modified, executed, tested, and validated the
implementation before committing changes to GitHub.

AI assistance was used to accelerate development and reasoning, while the
final implementation and engineering decisions were made and verified by the
developer.
