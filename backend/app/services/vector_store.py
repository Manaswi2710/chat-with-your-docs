
import chromadb

from backend.app.services.embedding_service import (
    generate_embeddings,
    generate_query_embedding
)

# Store the database locally inside the data folder
DB_PATH = "data/chroma_db"

# Name of the collection that stores document chunks
COLLECTION_NAME = "document_chunks"


def get_vector_collection():
    """
    Create or retrieve the ChromaDB collection.
    """
    client = chromadb.PersistentClient(path=DB_PATH)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    return collection


def store_chunks(chunks, document_id="sample_document"):
    """
    Generate embeddings and store chunks with their metadata.
    """
    if not chunks:
        raise ValueError("No chunks provided for storage")

    # Extract text from each chunk
    texts = [chunk["text"] for chunk in chunks]

    # Generate embeddings for all chunks
    embeddings = generate_embeddings(texts)

    # Create unique IDs for each chunk
    ids = [
        f"{document_id}_page_{chunk['page_number']}_chunk_{chunk['chunk_index']}"
        for chunk in chunks
    ]

    # Preserve page and chunk information
    metadatas = [
        {
            "document_id": document_id,
            "page_number": chunk["page_number"],
            "chunk_index": chunk["chunk_index"]
        }
        for chunk in chunks
    ]

    collection = get_vector_collection()

    # Upsert inserts new records or updates existing records with the same IDs
    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(ids)


def search_similar_chunks(query, n_results=3, document_id=None):
    """
    Find the most relevant chunks for a user's question.
    """
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")

    if n_results <= 0:
        raise ValueError("n_results must be positive")

    collection = get_vector_collection()

    if collection.count() == 0:
        return []

    # Convert the question into an embedding
    query_embedding = generate_query_embedding(query)

    # Limit the search to a particular document when requested
    where_filter = (
        {"document_id": document_id}
        if document_id
        else None
    )

    # Avoid requesting more results than are available
    result_count = min(n_results, collection.count())

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=result_count,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )

    # Convert ChromaDB's response into a convenient list
    matches = []

    for i in range(len(results["ids"][0])):
        matches.append({
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return matches
