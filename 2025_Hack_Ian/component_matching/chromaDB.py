import chromadb
from llm_rag import get_embedding



def create_chroma_db(page_content):
    # setup Chroma in-memory, for easy prototyping. Can add persistence easily!
    chroma_client = chromadb.Client()

    # Create collection. get_collection, get_or_create_collection, delete_collection also available!
    db = chroma_client.get_or_create_collection("all-my-documents")

    # # Add docs to the collection. Can also update and delete. Row-based API coming soon!

    for i, content in enumerate(page_content):
        document = content["text"]
        embedding = content["embedding"]
        title = content["title"]

        db.add(
            documents=document, # we handle tokenization, embedding, and indexing automatically. You can skip that and add your own embeddings as well
            metadatas={"title": title,
                        "source": "page4, lineXXX PlaceHolder"}, # filter on these!
            ids=f"id_{i}", # unique for each doc
            embeddings=embedding
        )
    return db

def query(query, db, n_results):
    query_embeddings = get_embedding(query, model="text-embedding-ada-002")
    results = db.query(
      query_embeddings= query_embeddings,
      n_results=n_results,
      # where={"metadata_field": "is_equal_to_this"}, # optional filter
      # where_document={"$contains":"search_string"}  # optional filter
  )
    return results