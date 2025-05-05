# CiteWise

**CiteWise** is a private legal reference assistant that allows attorneys, students, law review editors, and legal professionals to ask precise citation and grammar-related questions based on *The Bluebook (21st Edition)* and *The Redbook (5th Edition)*. This tool uses AI and embedded data from licensed copies of these reference books to return answers supported by the most relevant rules, examples, and best practices.

## Overview

CiteWise runs as a Streamlit app and can be deployed locally or privately through Streamlit Cloud. It uses semantic search over embedded Bluebook and Redbook content, combined with OpenRouter-hosted large language models to generate professional legal writing guidance and citation recommendations.

## Features

* Interactive query interface for both Bluebook and Redbook topics
* Context-aware answers tailored to whitepages, bluepages, and legal grammar
* Source-matching with paragraph-level rule preview and page numbers
* Smart topic suggestions and quick reference formatting guidance
* Private PDF processing with no public distribution of licensed materials
* Fully configurable model selection using OpenRouter

## Requirements

* Python 3.9 or later
* Streamlit
* PyMuPDF
* SentenceTransformers
* FAISS (optional, if using advanced retrieval)
* Access to OpenRouter with an API key

See `requirements.txt` for the full list of dependencies.

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org-or-user/citewise.git
cd citewise
```

### 2. Add Your Licensed PDFs

Place your private, licensed copies of the Bluebook and Redbook into the `private_docs/` directory:

```
private_docs/
├── bluebook.pdf
├── redbook.pdf
```

Do **not** upload these files to any public platform. These are used locally for embedding only.

### 3. Generate Embeddings

Run the embed scripts locally:

```bash
python bluebook_embed.py
python redbook_embed.py
```

This will generate:

```
private_docs/
├── bluebook_embeddings.pkl
├── redbook_embeddings.pkl
```

Only the `.pkl` files are needed by the app. You may upload them to Streamlit Cloud if your app is hosted there.

### 4. Configure Streamlit Secrets

In Streamlit Cloud or in `.streamlit/secrets.toml` (local only), add your OpenRouter API key:

```toml
OPENROUTER_API_KEY = "sk-..."
```

### 5. Run the App

```bash
streamlit run streamlit_app.py
```

## File Structure

```
/citewise
├── streamlit_app.py
├── bluebook_embed.py
├── redbook_embed.py
├── helpers.py
├── private_docs/
│   ├── bluebook_embeddings.pkl
│   └── redbook_embeddings.pkl
├── requirements.txt
├── .streamlit/
│   └── config.toml
```

## Deployment Notes

* Streamlit secrets are used to store API credentials securely.

## License

CiteWise is provided for private educational and professional use only. You are responsible for ensuring your use of any reference materials complies with applicable license agreements.

## Disclaimer

This application uses AI to provide writing and citation assistance. CiteWise does not guarantee accuracy and is not a substitute for official legal reference materials.
