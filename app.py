import os
import re
import pickle
import hashlib
import fitz
import faiss
import numpy as np

# Updated modern SDK import
from google import genai
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# ===============================
# Load API Key & Init SDK
# ===============================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Correct initialization for modern SDK
client = genai.Client(api_key=api_key)

# ===============================
# Config
# ===============================

PDF_FILE = "Customer_Analytics_Report.pdf"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 4

INDEX_FILE = "faiss_store.index"
CHUNK_FILE = "chunks.pkl"
HASH_FILE = "source.hash"


def file_hash(path: str) -> str:
    """Hash the PDF so we know if it changed since the index was built."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def clean_text(raw: str) -> str:
    """Collapse excess whitespace left over from PDF extraction."""
    raw = re.sub(r"[ \t]+", " ", raw)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Split into overlapping chunks, breaking on whitespace where possible."""
    if overlap >= size:
        raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + size, text_len)

        # try not to cut a word in half
        if end < text_len:
            boundary = text.rfind(" ", start, end)
            if boundary != -1 and boundary > start:
                end = boundary

        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)

        if end >= text_len:
            break

        start = end - overlap

    return chunks


# ===============================
# Read PDF
# ===============================

if not os.path.exists(PDF_FILE):
    raise FileNotFoundError(f"'{PDF_FILE}' not found in current directory.")

print("Loading PDF...")

try:
    doc = fitz.open(PDF_FILE)
    text = "".join(page.get_text() for page in doc)
    doc.close()
except Exception as e:
    raise RuntimeError(f"Failed to read PDF: {e}")

text = clean_text(text)

if not text:
    raise ValueError("No extractable text found in PDF (it may be scanned/image-based).")

# ===============================
# Split into chunks
# ===============================

chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
print(f"Created {len(chunks)} chunks")

# ===============================
# Embeddings
# ===============================

print("Loading embedding model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

current_hash = file_hash(PDF_FILE)

cache_valid = (
    os.path.exists(INDEX_FILE)
    and os.path.exists(CHUNK_FILE)
    and os.path.exists(HASH_FILE)
    and open(HASH_FILE).read().strip() == current_hash
)

if cache_valid:
    print("Loading cached FAISS index...")
    index = faiss.read_index(INDEX_FILE)
    with open(CHUNK_FILE, "rb") as f:
        stored_chunks = pickle.load(f)
else:
    print("Building FAISS index (source changed or no cache found)...")

    embeddings = embedder.encode(chunks, convert_to_numpy=True, show_progress_bar=True)
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, INDEX_FILE)

    with open(CHUNK_FILE, "wb") as f:
        pickle.dump(chunks, f)

    with open(HASH_FILE, "w") as f:
        f.write(current_hash)

    stored_chunks = chunks

# ===============================
# Chat Loop
# ===============================

print("\nChatbot Ready!")
print("Type 'exit' to quit.\n")

while True:
    try:
        question = input("You: ").strip()
    except EOFError:
        break

    if not question:
        continue

    if question.lower() == "exit":
        break

    query_embedding = embedder.encode([question], convert_to_numpy=True)

    k = min(TOP_K, len(stored_chunks))
    distances, indices = index.search(query_embedding, k)

    context_parts = []
    for idx in indices[0]:
        if idx == -1:
            continue
        context_parts.append(stored_chunks[idx])

    context = "\n\n".join(context_parts)

    if not context:
        print("\nBot:\nI couldn't find that information in the report.\n")
        continue

    prompt = f"""You are an AI Customer Analytics Assistant.

Answer ONLY using the information below.

If the answer is not present in the context, say:
"I couldn't find that information in the report."

Context:

{context}

Question:
{question}
"""

    try:
        # Correct structural call for the new SDK
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )
        answer = response.text
    except Exception as e:
        answer = f"[Error contacting Gemini API: {e}]"

    print("\nBot:")
    print(answer)
    print()
