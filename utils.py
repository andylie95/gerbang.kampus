import streamlit as st
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential

# Dictionary to cache translations to avoid repeated API calls for the same text
@st.cache_data
def get_translation_cache():
    """Initializes and returns a session-specific cache for translations."""
    return {}

def translate_text(text: str, to_language: str, cache: dict):
    """
    Translates a single text string to a target language using Azure Translator.
    Caches the results to avoid redundant API calls. Relies on Streamlit Secrets.
    """
    # No translation needed if the target is English or the text is empty
    if to_language == "en" or not text:
        return text

    # Use a tuple of (text, language) as the key for the cache
    cache_key = (text, to_language)
    if cache_key in cache:
        return cache[cache_key]

    try:
        # Get Azure credentials securely from Streamlit secrets
        credential = AzureKeyCredential(st.secrets["AZURE_TRANSLATOR_KEY"])
        endpoint = st.secrets["AZURE_TRANSLATOR_ENDPOINT"]
        
        # Initialize the translation client
        text_translator = TextTranslationClient(endpoint=endpoint, credential=credential)
        
        # --- FIX APPLIED HERE ---
        # The new library version requires the text to be in a list of dictionaries passed to the 'body' argument.
        request_body = [{'text': text}]
        result = text_translator.translate(body=request_body, to_language=[to_language])
        
        translation = result[0].translations[0].text
        
        # Store the successful translation in the cache
        cache[cache_key] = translation
        return translation
    except Exception as e:
        # Show an error in the app if translation fails
        st.error(f"Translation failed: {e}. Please check your Azure credentials in Streamlit Secrets.")
        # Cache the failed attempt with the original text to avoid retrying
        cache[cache_key] = text 
        return text # Return original text on error

def language_selector():
    """
    Creates a language selector widget in the sidebar and returns the selected language code.
    Updated to include English, Indonesian, and Mandarin.
    """
    st.sidebar.header("Language / Bahasa / 语言")
    lang = st.sidebar.selectbox(
        "Select Language", 
        ["English", "Indonesian", "Mandarin"]
    )

    # Map the display name to the language code required by the Azure API
    lang_code_map = {
        "English": "en", 
        "Indonesian": "id", 
        "Mandarin": "zh-Hans" # Code for Simplified Chinese
    }
    return lang_code_map[lang]

