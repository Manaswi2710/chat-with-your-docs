
from backend.app.services.pdf_processor import process_pdf
from backend.app.services.embedding_service import generate_embeddings

# Process the sample PDF
chunks = process_pdf(
    "data/sample.pdf",
    chunk_size=150,
    overlap=30
)

# Extract only the text from each chunk
texts = [chunk["text"] for chunk in chunks]

# Generate embeddings
embeddings = generate_embeddings(texts)

print("Embedding generation successful!")
print("Total chunks:", len(texts))
print("Total embeddings:", len(embeddings))

if embeddings:
    print("Dimensions of first embedding:", len(embeddings[0]))
    print("First embedding (first 5 values):", embeddings[0][:5])
