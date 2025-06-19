import streamlit as st
from utils import translate_text, language_selector, get_translation_cache

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="About Gerbang Kampus", layout="centered")

# --- LANGUAGE SELECTION & TRANSLATION SETUP ---
target_lang = language_selector()
translation_cache = get_translation_cache()

def T(text):
    """A wrapper for the translation function for cleaner code."""
    return translate_text(text, target_lang, translation_cache)

# --- PAGE CONTENT ---
st.title(f"ℹ️ {T('About Gerbang Kampus')}")

# The content is written in English and will be dynamically translated by the T() function.
st.markdown(f"""
## {T('Our Mission')}

**{T('Gerbang Kampus')}** ({T('Campus Gateway')}) {T('is dedicated to simplifying the university and career selection process for students everywhere. We believe that with the right information and self-understanding, every student can find the path that leads to a fulfilling career and a successful future.')}

## {T('Our Features')}

- **{T('In-depth University Database')}:** {T('We provide a curated list of universities with essential information to help you make informed decisions.')}
- **{T('Personalized Career Assessment')}:** {T('Our assessment tool is designed to align your innate strengths and interests with potential fields of study.')}
- **{T('Intuitive and User-Friendly')}:** {T('We strive to create a seamless experience, making your search for the perfect university as easy as possible.')}

## {T('Contact Us')}

{T('For any inquiries or feedback, please feel free to reach out to us at')} [contact@gerbangkampus.com](mailto:contact@gerbangkampus.com).
""")
