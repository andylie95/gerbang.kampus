import streamlit as st
import requests
import uuid
import json

@st.cache_data
def get_translation_cache():
    """Initializes and returns a session-specific cache for translations."""
    return {}

def translate_text(text: str, to_language: str, cache: dict, azure_key: str, azure_endpoint: str, azure_region: str):
    """
    Translates text using a direct Azure REST API call to ensure headers are set correctly.
    """
    if to_language == "en" or not text:
        return text

    cache_key = (text, to_language)
    if cache_key in cache:
        return cache[cache_key]

    try:
        # Check if all required credentials are provided
        if not all([azure_key, azure_endpoint, azure_region]):
            st.warning("Azure credentials (key, endpoint, or region) are not set. Translation is disabled.")
            return text
        if "PASTE_YOUR" in azure_key or "PASTE_YOUR" in azure_region:
             st.warning("Azure credentials appear to be placeholders. Please update them. Translation is disabled.")
             return text


        # Construct the full URL for the REST API request
        path = '/translate'
        constructed_url = azure_endpoint.rstrip('/') + path

        # Set the required parameters for the API call
        params = {
            'api-version': '3.0',
            'to': [to_language]
        }
        
        # Set the required headers, including the key and now the region
        headers = {
            'Ocp-Apim-Subscription-Key': azure_key,
            'Ocp-Apim-Subscription-Region': azure_region,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        
        # The body of the request containing the text to translate
        body = [{'text': text}]

        # Make the API call using the 'requests' library
        response = requests.post(constructed_url, params=params, headers=headers, json=body)
        response.raise_for_status()  # This will raise an error for bad status codes (like 401)

        # Process the successful JSON response
        response_json = response.json()
        translation = response_json[0]['translations'][0]['text']
        
        cache[cache_key] = translation
        return translation
        
    except requests.exceptions.HTTPError as http_err:
        # Provide a much more detailed error message if authentication fails
        error_content = "Could not parse error response."
        try:
            error_content = http_err.response.json()
            error_message = error_content.get('error', {}).get('message', 'Unknown HTTP Error')
        except json.JSONDecodeError:
             error_message = http_err.response.text

        st.error(f"Translation failed: (HTTP {http_err.response.status_code}) {error_message}. Please double-check your Azure Key, Endpoint, AND Region.")
        cache[cache_key] = text
        return text
    except Exception as e:
        st.error(f"An unexpected error occurred during translation: {e}.")
        cache[cache_key] = text
        return text
