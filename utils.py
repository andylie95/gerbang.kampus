import streamlit as st
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential

@st.cache_data
def get_translation_cache():
    """Initializes and returns a session-specific cache for translations."""
    return {}

def translate_text(text: str, to_language: str, cache: dict, azure_key: str, azure_endpoint: str):
    """
    Translates text using Azure, accepting secrets as arguments.
    """
    if to_language == "en" or not text:
        return text

    cache_key = (text, to_language)
    if cache_key in cache:
        return cache[cache_key]

    try:
        if not azure_key or not azure_endpoint:
            st.warning("Azure credentials are not set. Translation is disabled.")
            return text

        credential = AzureKeyCredential(azure_key)
        text_translator = TextTranslationClient(endpoint=azure_endpoint, credential=credential)
        
        request_body = [{'text': text}]
        result = text_translator.translate(body=request_body, to_language=[to_language])
        
        translation = result[0].translations[0].text
        cache[cache_key] = translation
        return translation
    except Exception as e:
        st.error(f"Translation failed: {e}. Please check your Azure credentials.")
        cache[cache_key] = text 
        return text
