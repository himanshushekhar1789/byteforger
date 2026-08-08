# ByteForger - AI Interview Agent

ByteForger is an AI-powered technical interview agent that conducts adaptive, conversational interviews based on a candidate's role, curriculum, and learning signals.

## Features

- Candidate-specific interview planning
- Curriculum-driven technical questions
- Adaptive follow-up questions
- Maximum follow-ups per curriculum topic
- Conversation state maintained using `sessionId`
- Groq-powered LLM integration
- Structured final interview feedback
- FastAPI HTTP API

## Architecture

```text
Candidate
    |
    v
Interview Planner
    |
    v
Interview State
    |
    v
Interview Agent
    |
    +----> Groq LLM
    |
    v
FastAPI
    |
    v
POST /api/interview

byteforger/
├── data/
├── interview_agent.py
├── interview_planner.py
├── interview_state.py
├── data_loader.py
├── llm_client.py
├── main.py
├── test_interview.py
├── AI_USAGE_LOG.md
├── requirements.txt
└── .gitignore

Setup

Create a virtual environment:
python -m venv .venv
Activate the virtual environment:
.venv\Scripts\Activate.ps1
Install the project dependencies:
pip install -r requirements.txt
Create a .env file in the project root:
GROQ_API_KEY=your_groq_api_key_here
Replace your_groq_api_key_here with your own Groq API key.
Do not commit the .env file to Git.
Run the API

Start the FastAPI server:
uvicorn main:app --reload
The API will be available at:
http://127.0.0.1:8000
Interactive API documentation is available at:
http://127.0.0.1:8000/docs
API
Start an Interview
POST /api/interview



Request:
{
  "sessionId": "abc-123",
  "candidate": {
    "...": "candidate data"
  }
}
Response:
{
  "reply": "Interview question...",
  "done": false
}
Continue an Interview

Use the same sessionId and send the candidate's answer:
{
  "sessionId": "abc-123",
  "message": "Candidate's answer..."
}
Response:
{
  "reply": "Next interview question...",
  "done": false
}
Completed Interview

When the minimum interview coverage is reached:
{
  "reply": "Interview completed.",
  "done": true,
  "feedback": {
    "summary": "...",
    "strengths": [],
    "gaps": [],
    "next": []
  }
}
Testing

Run the interview logic test with:
python test_interview.py
The API can also be tested through the interactive FastAPI documentation:
http://127.0.0.1:8000/docs
AI Usage

AI-assisted development decisions, prompts, and usage during the development of ByteForger are documented in:
AI_USAGE_LOG.md
