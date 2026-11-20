"""FastAPI entry point. Run: uvicorn app.main:app --reload."""

from app.config import get_settings
from app.services.llm_service import ChatServiceError, answer_question
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="University FAQ Chatbot", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class Question(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    question: str = Field(min_length=1, max_length=2000)


class Source(BaseModel):
    reference: int
    source: str
    page: int | None = None


class Answer(BaseModel):
    response: str
    sources: list[Source]


@app.get("/")
def home():
    return {"message": "University FAQ Chatbot API", "docs": "/docs"}


@app.get("/health")
def health():
    """Liveness only; does not call Groq or download embedding weights."""
    return {"status": "ok"}


@app.post("/chat", response_model=Answer)
def chat(data: Question):
    try:
        return answer_question(data.question)
    except ChatServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from None
