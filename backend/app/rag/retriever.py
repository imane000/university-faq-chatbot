import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

faq_collection = client.get_collection(name="university_faq")
docs_collection = client.get_collection(name="university_documents")

def retrieve_context(question: str):
    faq_results = faq_collection.query(
        query_texts=[question],
        n_results=2
    )

    docs_results = docs_collection.query(
        query_texts=[question],
        n_results=3
    )

    faq_docs = faq_results["documents"][0]
    pdf_docs = docs_results["documents"][0]

    context = "\n\n".join(faq_docs + pdf_docs)

    return context