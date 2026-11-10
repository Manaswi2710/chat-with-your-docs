
from backend.app.services.pdf_processor import process_pdf
from backend.app.services.vector_store import (
    store_chunks,
    search_similar_chunks
)
from backend.app.services.llm_service import generate_answer

# Step 1: Process the PDF
chunks = process_pdf(
    "data/sample.pdf",
    chunk_size=150,
    overlap=30
)

# Step 2: Store the chunks in ChromaDB
store_chunks(
    chunks,
    document_id="healthcare_module_2"
)

# Step 3: Ask a question
question = "How is reinforcement learning used in treatment planning?"

# Step 4: Retrieve relevant chunks
retrieved_chunks = search_similar_chunks(
    question,
    n_results=3,
    document_id="healthcare_module_2"
)

print("\nRelevant chunks retrieved:", len(retrieved_chunks))

# Step 5: Generate an answer using Gemini
answer = generate_answer(question, retrieved_chunks)

print("\n" + "=" * 60)
print("USER QUESTION:")
print(question)

print("\nGENERATED ANSWER:")
print(answer)
print("=" * 60)
