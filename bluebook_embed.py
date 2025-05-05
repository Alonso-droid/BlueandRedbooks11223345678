# bluebook_embed.py — Part 1 of 3
"""
Preprocessing script to extract and embed paragraphs from the Bluebook PDF.

✅ Outputs:
- ./private_docs/bluebook_embeddings.pkl (paragraphs + vectors + metadata)
"""

import os
import fitz  # PyMuPDF
import pickle
import re
from sentence_transformers import SentenceTransformer

# --- Configuration ---
BLUEBOOK_PATH = "./private_docs/bluebook.pdf"
OUTPUT_PATH = "./private_docs/bluebook_embeddings.pkl"
EMBED_MODEL = "all-MiniLM-L6-v2"

# --- Section-aware Paragraph Extraction ---
def extract_paragraphs(pdf_path):
    doc = fitz.open(pdf_path)
    paragraphs = []
    current_section = None

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 50]

        for chunk in chunks:
            heading_match = re.match(r"^(Rule|Table|B\d+|T\d+)?\.?\s?(.*?)\s*$", chunk)
            if heading_match and chunk.lower().startswith(("rule", "table", "b", "bluepages")):
                current_section = chunk.strip()

            paragraphs.append({
                "text": chunk,
                "section": current_section or "Unknown",
                "page": page_num
            })

    return paragraphs

# bluebook_embed.py — Part 2 of 3
from tqdm import tqdm
import torch

# Load model (cached by default)
def load_model():
    print("🔌 Loading embedding model...")
    return SentenceTransformer(EMBED_MODEL)

# Embed all paragraphs
def embed_paragraphs(paragraphs, model):
    print("🧠 Generating embeddings...")
    texts = [p["text"] for p in paragraphs]
    embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
    return embeddings

# Save to disk with metadata
def save_embeddings(paragraphs, embeddings, output_path):
    print(f"💾 Saving {len(paragraphs)} paragraphs to {output_path}...")
    data = []
    for i, para in enumerate(paragraphs):
        data.append({
            "text": para["text"],
            "embedding": embeddings[i].cpu().numpy(),
            "section": para["section"],
            "page": para["page"]
        })

    with open(output_path, "wb") as f:
        pickle.dump(data, f)

    print("✅ Done. Embeddings saved.")

# bluebook_embed.py — Part 3 of 3

def main():
    if not os.path.exists(BLUEBOOK_PATH):
        raise FileNotFoundError(f"Missing Bluebook file at: {BLUEBOOK_PATH}")

    print("📖 Extracting paragraphs from PDF...")
    paragraphs = extract_paragraphs(BLUEBOOK_PATH)

    print(f"📚 Found {len(paragraphs)} paragraphs for embedding.")
    model = load_model()
    embeddings = embed_paragraphs(paragraphs, model)
    save_embeddings(paragraphs, embeddings, OUTPUT_PATH)

if __name__ == "__main__":
    main()
