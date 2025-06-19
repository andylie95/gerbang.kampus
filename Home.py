import streamlit as st
from utils import translate_text, language_selector, get_translation_cache

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Gerbang Kampus",
    page_icon="👋",
    layout="wide"
)

# --- LANGUAGE SELECTION & TRANSLATION SETUP ---
# Initialize the language selector and the translation cache for this session
target_lang = language_selector()
translation_cache = get_translation_cache()

def T(text):
    """A wrapper for the translation function for cleaner code."""
    return translate_text(text, target_lang, translation_cache)

# --- PAGE CONTENT ---
st.title(T("Welcome to Gerbang Kampus! 👋"))

st.sidebar.success(T("Select a feature above."))

# The content is written in English and will be dynamically translated by the T() function.
st.markdown(
    f"""
    **{T("Gerbang Kampus")}** {T("is your one-stop portal to discover your future career path and the perfect university to achieve your dreams.")}

    ### {T("What we offer:")}
    - **{T("University Finder:")}** {T("A comprehensive database of universities worldwide. Filter by continent, subject, and degree level to find the best fit for you.")}
    - **{T("Career Assessment:")}** {T("Not sure which major to choose? Take our assessment test to get a recommendation based on your skills and interests.")}
    - **{T("Detailed Information:")}** {T("Get all the essential details about universities, including tuition fees, rankings, and application dates.")}

    ### {T("How to get started:")}
    - {T("Use the menu on the left to navigate to the University Finder or the Assessment.")}
    - {T("On the University Finder page, use the filters to narrow down your options.")}
    - {T("Click on a university to see more detailed information.")}
    - {T("Take the Assessment to discover subject recommendations tailored to you.")}

    {T("We hope to be your trusted gateway to higher education!")}
    """
)
