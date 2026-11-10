
from sentence_transformers import SentenceTransformer

# Name of the pre-trained embedding model
MODEL_NAME = "all-MiniLM-L6-v2"

# Load the model only when it is first needed
_model = None


def get_embedding_model():
    global _model

    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def generate_embeddings(texts):
    """
    Convert a list of text chunks into numerical vectors.

    Args:
        texts: A list of text strings.

    Returns:
        A list of embedding vectors.
    """
    if not texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    return embeddings.tolist()


def generate_query_embedding(query):
    """
    Convert a user's question into an embedding vector.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    return generate_embeddings([query])[0]
