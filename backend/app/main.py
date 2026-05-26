from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from app.services.llm_service import ask_llm

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_history = []

class Question(BaseModel):
    question: str

@app.get("/")
def home():
    return {
        "message": "University FAQ Chatbot API"
    }

@app.post("/chat")
def chat(data: Question):

    response = ask_llm(data.question)

    chat_history.append({
        "question": data.question,
        "response": response
    })

    return {
        "response": response
    }

@app.get("/history")
def get_history():
    return {
        "history": chat_history
    }

@app.delete("/history")
def clear_history():

    chat_history.clear()

    return {
        "message": "Historique supprimé avec succès"
    }