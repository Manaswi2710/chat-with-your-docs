
import os
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from backend.app.services.pdf_processor import process_pdf

from backend.app.services.vector_store import (
    store_chunks,
    search_similar_chunks
)

from backend.app.services.llm_service import generate_answer


# -----------------------------------------
# 1. CREATE FASTAPI APPLICATION
# -----------------------------------------

app = FastAPI(
    title="Chat with Your Docs",
    description="A RAG-based document question-answering system",
    version="1.0.0"
)


# -----------------------------------------
# 2. CONFIGURATION
# -----------------------------------------

UPLOAD_DIR = "data/uploads"
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

os.makedirs(UPLOAD_DIR, exist_ok=True)


# -----------------------------------------
# 3. REQUEST MODEL
# -----------------------------------------

class QuestionRequest(BaseModel):
    document_id: str
    question: str


# -----------------------------------------
# 4. HOME ENDPOINT
# -----------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to Chat with Your Docs API!"
    }


# -----------------------------------------
# 5. HEALTH CHECK ENDPOINT
# -----------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "Chat with Your Docs"
    }


# -----------------------------------------
# 6. PDF UPLOAD ENDPOINT
# -----------------------------------------

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # Validate filename
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # Read uploaded file
    file_content = await file.read()

    # Check empty file
    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF is empty."
        )

    # Check file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must not exceed 20 MB."
        )

    # Verify PDF signature
    if not file_content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid PDF."
        )

    # Generate unique document ID
    document_id = str(uuid.uuid4())

    # Generate safe filename
    file_path = os.path.join(
        UPLOAD_DIR,
        f"{document_id}.pdf"
    )

    # Save PDF
    with open(file_path, "wb") as pdf_file:
        pdf_file.write(file_content)

    try:
        # Extract, clean and chunk PDF
        chunks = process_pdf(
            file_path,
            chunk_size=150,
            overlap=30
        )

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="No extractable text found in the PDF."
            )

        # Generate embeddings and store in ChromaDB
        stored_count = store_chunks(
            chunks,
            document_id=document_id
        )

        # Count pages containing extracted text
        page_count = len({
            chunk["page_number"] for chunk in chunks
        })

        return {
            "message": "PDF uploaded and processed successfully!",
            "document_id": document_id,
            "filename": file.filename,
            "pages_with_text": page_count,
            "total_chunks": stored_count
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(error)}"
        )


# -----------------------------------------
# 7. QUESTION ANSWERING ENDPOINT
# -----------------------------------------

@app.post("/ask")
def ask_question(request: QuestionRequest):

    # Validate question
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # Retrieve relevant chunks from selected document
    retrieved_chunks = search_similar_chunks(
        query=request.question,
        n_results=3,
        document_id=request.document_id
    )

    # Check if relevant content exists
    if not retrieved_chunks:
        raise HTTPException(
            status_code=404,
            detail="No relevant content found for this document."
        )

    try:
        # Generate answer using Gemini
        answer = generate_answer(
            question=request.question,
            retrieved_chunks=retrieved_chunks
        )

        # Extract unique source page numbers
        source_pages = sorted({
            chunk["metadata"]["page_number"]
            for chunk in retrieved_chunks
        })

        return {
            "question": request.question,
            "answer": answer,
            "source_pages": source_pages,
            "retrieved_chunks": len(retrieved_chunks)
        }

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Answer generation failed: {str(error)}"
        )
