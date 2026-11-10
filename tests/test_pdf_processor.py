
from backend.app.services.pdf_processor import process_pdf

pdf_path = "data/sample.pdf"

# Process the PDF
chunks = process_pdf(
    pdf_path,
    chunk_size=150,
    overlap=30
)

print("PDF processing completed successfully!")

print("Total chunks:", len(chunks))

for chunk in chunks:

    print("\n" + "=" * 50)
    print("Page:", chunk["page_number"])
    print("Chunk:", chunk["chunk_index"])
    print("=" * 50)

    print(chunk["text"][:300])
