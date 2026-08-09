

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from data_loader import load_candidates
from interview_agent import start_interview, process_answer
from interview_state import get_session


app = FastAPI(title="ByteForger Interview Agent")
app.mount("/frontend", StaticFiles(directory="frontend"), 
name="frontend")
app.mount("/data", StaticFiles(directory="data"), name="data")

@app.get("/app")
def frontend():
    return FileResponse("frontend/index.html")


class InterviewRequest(BaseModel):
    sessionId: str
    candidate: dict | None = None
    message: str | None = None


@app.get("/")
def root():
    return {
        "message": "ByteForger Interview Agent is running"
    }


@app.post("/api/interview")
def interview(request: InterviewRequest):

    state = get_session(request.sessionId)

    # First request: start a new interview
    if state is None:

        if request.candidate is None:
            return {
                "error": "candidate is required when starting an interview"
            }

        question = start_interview(
            request.sessionId,
            request.candidate
        )

        return {
            "reply": question,
            "done": False
        }

    # Subsequent request: process candidate answer
    if request.message is None:
        return {
            "error": "message is required for an existing interview session"
        }

    result = process_answer(
        request.sessionId,
        request.message
    )

    # process_answer() returns a feedback dictionary when the interview is complete
    if state.has_minimum_coverage() and isinstance(result, dict):
        return {
            "reply": "Interview completed.",
            "done": True,
            "feedback": result
        }

    return {
        "reply": result,
        "done": False
    }