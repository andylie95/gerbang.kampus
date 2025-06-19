import streamlit as st
import pandas as pd
import json

# Import page-rendering functions from modules
from utils import translate_text, get_translation_cache
import university_finder
import assessment
import about

# --- AZURE SECRETS (EMBEDDED AS REQUESTED) ---
# For production, it's highly recommended to use Streamlit's Secrets Management.
AZURE_TRANSLATOR_KEY = "8770f1a53459427d897f18904336bf9b"
AZURE_TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com/"

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Gerbang Kampus",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed" # Collapse sidebar for our custom navigation
)

# --- CUSTOM CSS FOR STYLING ---
st.markdown("""
<style>
    /* Main container styling */
    .stApp {
        background-color: #F0F2F6;
    }
    /* Hide Streamlit's default hamburger menu */
    .st-emotion-cache-18ni7ap {
        display: none;
    }
    /* Style for the main content block */
    .st-emotion-cache-1y4p8pa {
        padding-top: 2rem;
    }
    /* Custom button styling */
    .stButton > button {
        border-radius: 12px;
        border: 2px solid #E0E0E0;
        background-color: #FFFFFF;
        color: #333333;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
        padding: 1rem;
    }
    .stButton > button:hover {
        border-color: #4A90E2;
        color: #4A90E2;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    /* Center the title */
    h1 {
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING (CACHE AT APP START) ---
@st.cache_data
def load_all_data():
    try:
        # --- FIX APPLIED HERE ---
        # Switched to 'latin-1' encoding to handle special characters from the CSV file.
        uni_df = pd.read_csv('data/universities.csv', encoding='latin-1')
        
        with open('data/assessment_questions.json', 'r', encoding='utf-8') as f:
            assessment_data = json.load(f)
        return uni_df, assessment_data['questions'], assessment_data['career_mapping']
    except Exception as e:
        st.error(f"Failed to load data files: {e}")
        return pd.DataFrame(), [], {}

uni_df, questions, career_mapping = load_all_data()

# --- LANGUAGE & TRANSLATION SETUP ---
lang_code_map = {"English": "en", "Indonesian": "id", "Mandarin": "zh-Hans"}
lang_name_map = {v: k for k, v in lang_code_map.items()}

# Set default language if not set
if 'language_code' not in st.session_state:
    st.session_state.language_code = 'en'

translation_cache = get_translation_cache()
def T(text):
    return translate_text(text, st.session_state.language_code, translation_cache, AZURE_TRANSLATOR_KEY, AZURE_TRANSLATOR_ENDPOINT)

# --- NAVIGATION & PAGE ROUTING ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def set_page(page_name):
    st.session_state.page = page_name

# --- HEADER & NAVIGATION BAR ---
header_cols = st.columns([1, 2, 1])

with header_cols[0]:
    if st.session_state.page != 'home':
        if st.button(f"← {T('Back to Home')}", use_container_width=True):
            set_page('home')

with header_cols[2]:
    # Language Selector Widget
    selected_lang_name = st.selectbox(
        label=T("Language / Bahasa / 语言"),
        options=lang_code_map.keys(),
        index=list(lang_code_map.values()).index(st.session_state.language_code),
        label_visibility="collapsed"
    )
    st.session_state.language_code = lang_code_map[selected_lang_name]

# --- RENDER CURRENT PAGE ---
if st.session_state.page == 'home':
    st.title(T("Gerbang Kampus"))
    st.markdown(f"<h5 style='text-align: center; color: grey;'>{T('Your Gateway to Global Education')}</h5>", unsafe_allow_html=True)
    st.write("---")
    
    # Navigation buttons container
    with st.container():
        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            with st.container(border=True, height=200):
                st.markdown(f"### 🎓 {T('University Finder')}")
                st.write(T("Search and filter top universities worldwide."))
                if st.button(T('Explore Universities'), key='nav_finder', use_container_width=True):
                    set_page('finder')
        
        with col2:
            with st.container(border=True, height=200):
                st.markdown(f"### 📝 {T('Career Assessment')}")
                st.write(T("Take our chat-based test to find your path."))
                if st.button(T('Start Assessment'), key='nav_assessment', use_container_width=True):
                    set_page('assessment')

        with col3:
            with st.container(border=True, height=200):
                st.markdown(f"### ℹ️ {T('About Us')}")
                st.write(T("Learn more about the Gerbang Kampus mission."))
                if st.button(T('Learn More'), key='nav_about', use_container_width=True):
                    set_page('about')

elif st.session_state.page == 'finder':
    university_finder.show_page(T, uni_df)

elif st.session_state.page == 'assessment':
    assessment.show_page(T, questions, career_mapping)

elif st.session_state.page == 'about':
    about.show_page(T)
