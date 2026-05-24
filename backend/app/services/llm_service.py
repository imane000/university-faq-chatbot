import os
from dotenv import load_dotenv
from groq import Groq

from app.rag.retriever import retrieve_context

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def ask_llm(question):

    context = retrieve_context(question)

    prompt = f"""
Tu es un assistant FAQ universitaire.

Réponds uniquement à partir du contexte suivant :

{context}

Question :
{question}

Réponse :
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=300
    )

    return response.choices[0].message.content