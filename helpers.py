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

def render_keyword_suggestions(source_tag: str) -> str:
    """
    Display topic buttons by source (bluebook/redbook) and return a pre-filled query if selected.
    """
    from helpers import COMMON_TOPICS  # ensure COMMON_TOPICS is defined in the same file

    source_label = "Bluebook" if source_tag == "bluebook" else "Redbook"
    selected_query = ""

    if source_label not in COMMON_TOPICS:
        st.warning(f"No suggestions available for {source_label}.")
        return ""

    st.markdown("##### 🔎 Quick-Select Common Topics")

    for group_label, topic_list in COMMON_TOPICS[source_label].items():
        st.markdown(f"**{group_label}**")
        cols = st.columns(min(len(topic_list), 4))
        for idx, (label, query_text) in enumerate(topic_list):
            if cols[idx % len(cols)].button(label, key=f"kw_{label}_{source_label}"):
                selected_query = query_text
        st.markdown("---")

    return selected_query
