# redbook_embed.py — Part 1 of 4
"""
Extracts paragraphs and section headers from the Redbook (5th ed.) PDF.

Generates structured data including:
- Paragraph text
- Section numbers and titles
- Page numbers
"""

import os
import fitz  # PyMuPDF
import re
import pickle

# --- File Paths ---
REDBOOK_PDF_PATH = "./private_docs/redbook.pdf"
OUTPUT_PATH = "./private_docs/redbook_embeddings.pkl"

# --- Extraction Logic ---
def extract_redbook_paragraphs(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"❌ Could not find file at: {pdf_path}")

    doc = fitz.open(pdf_path)
    paragraphs = []
    current_section = None

    section_pattern = re.compile(r"^(\d{1,2}(\.\d{1,2})?)\s+(.*)$")  # e.g., 1.2 Capitalization

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        blocks = [blk.strip() for blk in text.split("\n\n") if len(blk.strip()) > 50]

        for block in blocks:
            match = section_pattern.match(block)
            if match:
                current_section = f"{match.group(1)} {match.group(3)}"

            paragraphs.append({
                "text": block,
                "section": current_section or "Unknown",
                "page": page_num
            })

    print(f"✅ Extracted {len(paragraphs)} Redbook paragraphs.")
    return paragraphs

# redbook_embed.py — Part 2 of 4
from sentence_transformers import SentenceTransformer
import torch
from tqdm import tqdm

# --- Model Setup ---
EMBED_MODEL = "all-MiniLM-L6-v2"

def load_model():
    print("🔌 Loading SentenceTransformer model...")
    return SentenceTransformer(EMBED_MODEL)

def embed_paragraphs(paragraphs, model):
    texts = [p["text"] for p in paragraphs]
    print(f"🧠 Embedding {len(texts)} paragraphs...")
    
    embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
    return embeddings

# redbook_embed.py — Part 3 of 4

def save_embeddings(paragraphs, embeddings, output_path):
    print(f"💾 Saving {len(paragraphs)} embedded paragraphs to: {output_path}")
    output_data = []

    for i, para in enumerate(paragraphs):
        output_data.append({
            "text": para["text"],
            "embedding": embeddings[i].cpu().numpy(),
            "section": para["section"],
            "page": para["page"]
        })

    with open(output_path, "wb") as f:
        pickle.dump(output_data, f)

    print("✅ Saved embeddings with section and page metadata.")

# redbook_embed.py — Part 4 of 4

def main():
    print("📕 Starting Redbook preprocessing...")

    # Step 1: Extract paragraphs with sections
    paragraphs = extract_redbook_paragraphs(REDBOOK_PDF_PATH)

    # Step 2: Load model
    model = load_model()

    # Step 3: Generate embeddings
    embeddings = embed_paragraphs(paragraphs, model)

    # Step 4: Save results
    save_embeddings(paragraphs, embeddings, OUTPUT_PATH)

    print("🎉 Done! Redbook is ready for CiteWise.")

if __name__ == "__main__":
    main()
