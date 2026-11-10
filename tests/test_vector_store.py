
from backend.app.services.pdf_processor import process_pdf
from backend.app.services.vector_store import (
    store_chunks,
    search_similar_chunks
)

# Step 1: Process the PDF
chunks = process_pdf(
    "data/sample.pdf",
    chunk_size=150,
    overlap=30
)

print("Total chunks generated:", len(chunks))

# Step 2: Store chunks and their embeddings
stored_count = store_chunks(
    chunks,
    document_id="healthcare_module_2"
)

print("Chunks stored successfully:", stored_count)

# Step 3: Ask a sample question
query = "How is reinforcement learning used in treatment planning?"

results = search_similar_chunks(
    query,
    n_results=3,
    document_id="healthcare_module_2"
)

# Step 4: Display retrieved results
print("\nRelevant chunks retrieved:")

for index, result in enumerate(results, start=1):
    print("\n" + "=" * 60)
    print("Result:", index)
    print("Page:", result["metadata"]["page_number"])
    print("Chunk:", result["metadata"]["chunk_index"])
    print("Distance:", result["distance"])
    print("Content:", result["text"][:500])
