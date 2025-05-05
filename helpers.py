# --- Keyword Suggestion Dictionary ---
COMMON_TOPICS = {
    "Bluebook": {
        "Case Names": [
            ("Short form", "How do I cite a case in short form?"),
            ("Italicization", "Should case names be italicized in a law review article?"),
            ("Pending cases", "How do I cite a pending or unreported case?")
        ],
        "Statutes & Rules": [
            ("Federal statute", "How do I cite a federal statute in a court brief?"),
            ("Court rules", "What’s the format for citing local court rules?"),
        ],
        "Tables": [
            ("Table T6 Abbreviations", "Where do I find standard abbreviations for legal terms?"),
            ("Table T13 Journals", "How do I cite consecutively paginated law journals?")
        ]
    },
    "Redbook": {
        "Punctuation & Grammar": [
            ("Oxford comma", "Should I use a serial (Oxford) comma in legal writing?"),
            ("Ellipses", "How do I format an ellipsis in a quotation?"),
        ],
        "Typography": [
            ("Italics", "When should I italicize words in legal writing?"),
            ("Em dashes", "When should I use an em dash in a sentence?")
        ],
        "Capitalization": [
            ("Supreme Court", "Do I capitalize 'court' when referring to the Supreme Court?"),
            ("Government titles", "Should I capitalize job titles like 'senator' or 'justice'?")
        ]
    }
}

import streamlit as st

def render_keyword_suggestions(source_tag):
    suggestions = {
        "bluebook": [
            ("Short Form", "How do I cite a case in short form?"),
            ("Consecutively Paginated Journal", "How do I cite an article from a consecutively paginated journal?"),
            ("Italicization", "Which parts of a citation need to be italicized?")
        ],
        "redbook": [
            ("Oxford Comma", "Should I use the Oxford comma in legal writing?"),
            ("Em Dash", "How do I correctly use an em dash in formal writing?"),
            ("Capitalization", "When should 'court' be capitalized?")
        ]
    }

    st.markdown("#### 💡 Quick Topic Fill")
    topic_row = st.columns(len(suggestions[source_tag]))

    for i, (label, query_text) in enumerate(suggestions[source_tag]):
        if topic_row[i].button(label, key=f"suggest_{label}_{source_tag}"):
            return query_text

    return None

def choose_model(source_tag: str) -> str:
    """
    Choose the best free OpenRouter model for Bluebook vs. Redbook tasks.
    """
    if source_tag == "bluebook":
        return "meta-llama/llama-4-scout:free"  # Precise + rule-following
    elif source_tag == "redbook":
        return "mistralai/mistral-small-3.1-24b-instruct:free"  # Strong grammar
    else:
        return "deepseek/deepseek-chat-v3-0324:free"  # General fallback
