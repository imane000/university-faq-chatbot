from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import chromadb
import os

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="university_documents"
)

DATA_PATH = "./data"

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

all_chunks = []

for filename in os.listdir(DATA_PATH):

    if filename.endswith(".pdf"):

        file_path = os.path.join(DATA_PATH, filename)

        loader = PyPDFLoader(file_path)

        documents = loader.load()

        chunks = text_splitter.split_documents(documents)

        all_chunks.extend(chunks)

documents_text = []
ids = []

for index, chunk in enumerate(all_chunks):

    documents_text.append(chunk.page_content)

    ids.append(f"doc_{index}")

collection.add(
    documents=documents_text,
    ids=ids
)

print("PDFs indexés avec succès.")