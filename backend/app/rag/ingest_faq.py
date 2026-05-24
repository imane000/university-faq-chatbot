import json
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(name="university_faq")

with open("./data/faq.json", "r", encoding="utf-8") as file:
    faq_data = json.load(file)

documents = []
ids = []

for index, item in enumerate(faq_data):
    text = f"Question: {item['question']}\nRéponse: {item['answer']}"
    documents.append(text)
    ids.append(f"faq_{index}")

collection.add(
    documents=documents,
    ids=ids
)

print("FAQ indexée avec succès dans ChromaDB.")