import re
import fitz


def extract_text_from_pdf(file_path):

    extracted_pages = []

    # Open the PDF document
    document = fitz.open(file_path)

    # Iterate through every page
    for page_number, page in enumerate(document, start=1):

        # Extract text from the current page
        text = page.get_text()

        # Store page number and extracted text
        extracted_pages.append({
            "page_number": page_number,
            "text": text
        })

    # Close the PDF document
    document.close()

    return extracted_pages


def clean_text(text):

    # Replace non-breaking spaces with normal spaces
    text = text.replace("\u00a0", " ")

    # Remove unnecessary spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove spaces at the beginning and end
    text = text.strip()

    return text


def chunk_text(text, chunk_size=500, overlap=100):

    # Convert text into individual words
    words = text.split()

    # Validate chunking parameters
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Overlap must be non-negative and smaller than chunk size")

    chunks = []

    start = 0

    while start < len(words):

        # Find the ending position of the current chunk
        end = min(start + chunk_size, len(words))

        # Join words to create the chunk
        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        # Stop when all words have been processed
        if end == len(words):
            break

        # Move forward while retaining overlapping words
        start = end - overlap

    return chunks



def process_pdf(file_path, chunk_size=500, overlap=100):

    # Step 1: Extract text from every PDF page
    pages = extract_text_from_pdf(file_path)

    processed_chunks = []

    # Step 2: Process each page separately
    for page in pages:

        # Clean extracted text
        cleaned_text = clean_text(page["text"])

        # Divide cleaned text into chunks
        chunks = chunk_text(cleaned_text, chunk_size, overlap)

        # Step 3: Store chunks with metadata
        for chunk_index, chunk in enumerate(chunks, start=1):

            processed_chunks.append({
                "page_number": page["page_number"],
                "chunk_index": chunk_index,
                "text": chunk
            })

    return processed_chunks
