# streamlit_app.py — Part 1 of 7
import streamlit as st
import pickle
import torch
import os
from sentence_transformers import SentenceTransformer, util
import numpy as np
from datetime import datetime
import re
from helpers import render_keyword_suggestions
from helpers import choose_model

# --- Page Configuration ---
st.set_page_config(page_title="CiteWise", layout="wide")




# --- Sidebar Branding & Instructions ---
st.sidebar.markdown("## ⚖️ CiteWise")
st.sidebar.markdown("""
Your AI-powered assistant for citation and writing support using **The Bluebook (21st Ed.)** and **The Redbook (5th Ed.)**.



### How to Use:
- Select whether you're writing **academically** or **practitioner-style**
- Ask a citation or formatting question
- Review sourced guidance and citation rules

---

🔍 **Verify everything** before use.
This tool uses AI and **may not always reflect correct citation standards**.
""")

# --- Disclaimer Notice ---
st.warning("⚠️ AI-generated output. Always verify against The Bluebook and Redbook manually before submitting formal work.")

# --- Visual Style ---
st.markdown("""
<style>
h1, h2, h3 {
    font-family: 'Georgia', serif;
}
.st-emotion-cache-10trblm {
    font-family: 'Georgia', serif;
}
</style>
""", unsafe_allow_html=True)

# streamlit_app.py — Part 2 of 7


# --- Step 0: Choose Source (Book) ---
st.subheader("Step 1: Choose Your Sourcebook")

sourcebook = st.radio(
    "Which source do you want to search?",
    ["Bluebook (21st ed.)", "Redbook (5th ed.)"],
    index=0,
    help="Choose Bluebook for citation rules or Redbook for grammar, punctuation, and legal writing style."
)

# Internal identifier for logic
source_tag = "bluebook" if sourcebook.startswith("Blue") else "redbook"
st.sidebar.markdown(f"🤖 Using model: `{choose_model(source_tag)}`")


# --- 1. Style Context Toggle ---
st.subheader("Step 2: Choose Your Legal Writing Context")
style_context = st.radio(
    "Which citation style are you working with?",
    ["Academic (Law Review)", "Practitioner (Court Brief or Memo)", "Grammar/Writing (Redbook)"],
    index=0,
    help="This will affect formatting guidance. Bluebook and Redbook rules differ."
)

context_label = {
    "Academic (Law Review)": "Whitepages",
    "Practitioner (Court Brief or Memo)": "Bluepages",
    "Grammar/Writing (Redbook)": "Redbook"
}[style_context]

st.markdown(f"✍️ Using: **{context_label}** formatting rules")

# --- Step 2: Load Embeddings for Bluebook & Redbook ---
@st.cache_resource(show_spinner="Loading legal sources...")
def load_all_embeddings():
    sources = {}

    EMBEDDING_PATHS = {
        "bluebook": os.path.join("private_docs", "bluebook_embeddings.pkl"),
        "redbook": os.path.join("private_docs", "redbook_embeddings.pkl")
    }

    for tag, path in EMBEDDING_PATHS.items():
        if os.path.exists(path):
            with open(path, "rb") as f:
                sources[tag] = pickle.load(f)
        else:
            st.warning(f"⚠️ Missing embedding file: {path}")
    return sources


# All loaded data (dict: "bluebook" → [...], "redbook" → [...])
embedding_sources = load_all_embeddings()

# Select based on user's radio choice (from Part A)
selected_data = embedding_sources.get(source_tag)
if not selected_data:
    st.error(f"No data found for {source_tag}. Please check the embedding files.")
    st.stop()


# --- 3. Load Sentence Embedding Model ---
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

embed_model = load_model()

# --- 4. User Query + Auto-Suggest ---
st.subheader("Step 3: Ask a Citation or Writing Question")

# --- Maintain Query Input State ---
if "query_input" not in st.session_state:
    st.session_state["query_input"] = ""

# Auto-fill from keyword buttons
preset_query = render_keyword_suggestions(source_tag)
if preset_query:
    st.session_state["query_input"] = preset_query


query = st.text_input(
    "What do you need help with?",
    placeholder="e.g., How do I cite a federal statute in a court brief?",
    value=st.session_state["query_input"],
    key="query_input"
)

if st.button("🔄 Clear Question"):
    st.session_state["query_input"] = ""
    st.experimental_rerun()

with st.form("search_form"):
    query = st.text_input(
        "What do you need help with?",
        placeholder="e.g., How do I cite a federal statute in a court brief?",
        value=st.session_state["query_input"],
        key="query_input"
    )
    submitted = st.form_submit_button("🔍 Run Search")

if not query or not submitted:
    st.stop()


# --- Step 4b: Format Preview Examples ---
st.subheader("Formatting Preview")

if source_tag == "bluebook":
    if style_context == "Whitepages":
        st.markdown("""
        ##### **Academic (Whitepages) Example**
        *Marbury v. Madison*, 5 U.S. (1 Cranch) 137 (1803).
        - Use *italics* for case names
        - Parenthetical date
        """)
    else:
        st.markdown("""
        ##### **Practitioner (Bluepages) Example**
        Marbury v. Madison, 5 U.S. (1 Cranch) 137 (1803).
        - No italics (use underlining in print)
        - Use full case names
        """)
elif source_tag == "redbook":
    st.markdown("""
    ##### **Redbook Writing Style Example**
    ✅ Correct: "The Court held that..."
    ❌ Incorrect: "the court held that..."

    - Capitalize “Court” when referring to the U.S. Supreme Court  
    - Use one space between sentences (Redbook § 1.1)
    """)



# streamlit_app.py — Part 3 of 7

# --- 5. Embed Query and Search ---
def search_source_embeddings(query, embeddings_data, k=3):
    query_vec = embed_model.encode(query, convert_to_tensor=True)
    results = []

    for item in embeddings_data:
        sim = util.pytorch_cos_sim(query_vec, torch.tensor(item["embedding"]))[0][0]
        results.append((sim.item(), item))

    top_hits = sorted(results, key=lambda x: x[0], reverse=True)[:k]
    
    return [{
        "score": round(score, 4),
        "text": item["text"],
        "section": item["section"],
        "page": item["page"]
    } for score, item in top_hits]

# --- 6. Run Search ---
top_matches = search_source_embeddings(query, selected_data, k=3)

st.subheader(f"Step 4: Relevant {'Bluebook' if source_tag == 'bluebook' else 'Redbook'} Content")
for match in top_matches:
    with st.expander(f"📘 Rule Match: {match['section']} (p. {match['page']}) — Score: {match['score']}"):
        st.markdown(f"> {match['text']}")


# --- 7. Prompt Building ---
import requests

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")  # Loaded securely from Streamlit Cloud
if not OPENROUTER_API_KEY:
    st.error("❌ OpenRouter API key not found. Did you set it in Streamlit secrets?")


@st.cache_data
def build_contextual_prompt(query, style_context, matches, source_tag):
    book_label = "The Bluebook (21st ed.)" if source_tag == "bluebook" else "The Redbook (5th ed.)"

    context_block = "\n\n".join([
        f"Section: {m['section']} (Page {m['page']})\n{m['text']}" for m in matches
    ])

    return f"""You are a legal writing and citation assistant for professionals using {book_label}.

The user is working in a **{style_context}** context and has asked the following question:

"{query}"

Your answer should:
- Reference specific rule numbers or sections (e.g., Rule 10.2.1 or Redbook § 3.5)
- Format citations based on whether the context is Bluepages, Whitepages, or Redbook grammar rules
- Include page numbers where applicable
- Clearly state which source the information comes from
- Remind users that all AI output must be verified against the official text

### Relevant Source Material:
{context_block}

### Your Answer:
"""


# --- 8. Ask the OpenRouter LLM (with fallback model)
def ask_llama(prompt, source_tag):
    try:
        model_name = choose_model(source_tag)
    except Exception:
        model_name = "r1-free"  # fallback

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://yourdomain.com",  # optional
        "X-Title": "CiteWise"
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json={
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4
        }
    )

    if response.status_code != 200:
        st.error(f"❌ API Error {response.status_code}: {response.text}")
        return "Sorry, the model could not respond."

    return response.json()["choices"][0]["message"]["content"]



# streamlit_app.py — Part 5 of 7

# --- 7. Build Prompt and Send to OpenRouter ---
st.subheader("Step 5: AI-Powered Answer")

with st.spinner("Analyzing legal style and generating response..."):
    try:
        prompt = build_contextual_prompt(query, context_label, top_matches, source_tag)
        answer = ask_llama(prompt, source_tag)
    except Exception as e:
        st.error("An error occurred while contacting the model. Please check your OpenRouter key and try again.")
        st.stop()

# --- 8. Display AI Output with Clear Warning ---
st.markdown("#### 🧠 Suggested Answer")
st.markdown(f"""
<div style='border:1px solid #ccc; padding:16px; border-radius:8px; background:#f9f9f9; font-family:Georgia,serif'>
{answer}
</div>
""", unsafe_allow_html=True)

st.info("⚠️ This answer was generated using AI (Deep Hermes LLaMA 3 Preview via OpenRouter). Always confirm against the latest editions of the Bluebook or Redbook.")

# streamlit_app.py — Part 6 of 7

# --- 9. Optional Markdown Export ---


st.subheader("Step 6: Export or Copy Answer")

book_label = "The Bluebook (21st ed.)" if source_tag == "bluebook" else "The Redbook (5th ed.)"

md_text = f"""### Query: {query}

**Context**: {style_context}  
**Source**: {book_label}  

**AI-Generated Answer (Verify Before Use):**

{answer}

---

**Top Source Match(es):**
""" + "\n".join(
    f"- {m['section']} (Page {m['page']}) — relevance: {m['score']}" for m in top_matches
)

st.download_button(
    "⬇️ Download as Markdown",
    data=md_text.encode("utf-8"),
    file_name=f"citewise_{source_tag}_answer.md",
    mime="text/markdown"
)

st.code(md_text, language="markdown")


# --- 10. Store Interaction History (per session) ---
if "query_history" not in st.session_state:
    st.session_state.query_history = []

st.session_state.query_history.append({
    "question": query,
    "style": context_label,
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "sources": [f"{m['section']} (p. {m['page']})" for m in top_matches]
})

# --- Show History Log ---
st.markdown("#### 📜 Session Query Log")
for item in reversed(st.session_state.query_history[-5:]):
    st.markdown(f"""
- **{item['timestamp']}**: *{item['question']}* — _{item['style']}_
    - Cited: {", ".join(item['sources'])}
    """)

# streamlit_app.py — Part 7 of 7
from PIL import Image

# --- 11. Header Logo ---
logo_path = "./Citewise logo.png"
if os.path.exists(logo_path):
    col1, col2 = st.columns([1, 8])
    with col1:
        st.image(Image.open(logo_path), width=80)
    with col2:
        st.title("CiteWise")
else:
    st.title("⚖️ CiteWise")

st.caption("An AI-powered assistant for The Bluebook (21st Ed.) and The Redbook (5th Ed.)")

# --- 12. About Section ---
with st.expander("ℹ️ About This App"):
    st.markdown("""
**CiteWise** is designed for:
- Law students
- Legal practitioners
- Law review editors
- Professors and researchers

It uses embeddings + AI (Deep Hermes LLaMA 3 Preview from OpenRouter) to:
- Search the Bluebook and Redbook privately (no public access)
- Return styled, rule-cited answers
- Respect formatting differences (e.g., Bluepages vs. Whitepages)

> ❗ Results are **AI-generated** and may contain errors. You must always verify against official sources before submitting work.
""")

# --- 13. Friendly Footer ---
st.markdown("""
---
© 2025 Citewise.  
This tool does **not replace legal training** — it enhances it.
""")
