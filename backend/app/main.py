from fastapi import FastAPI
from pydantic import BaseModel
from app.services.llm_service import ask_llm

app = FastAPI()

class Question(BaseModel):
    question: str

@app.get("/")
def home():
    return {"message": "University FAQ Chatbot API"}

@app.post("/chat")
def chat(data: Question):

    response = ask_llm(data.question)

    return {
        "response": response
    }