import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_collection(name="university_faq")

def retrieve_context(question):

    results = collection.query(
        query_texts=[question],
        n_results=2
    )

    documents = results["documents"][0]

    context = "\n".join(documents)

    return context