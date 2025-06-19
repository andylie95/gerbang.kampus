import streamlit as st
import pandas as pd
from utils import translate_text, language_selector, get_translation_cache

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="University Finder", layout="wide")

# --- LANGUAGE SELECTION & TRANSLATION SETUP ---
target_lang = language_selector()
translation_cache = get_translation_cache()

def T(text):
    """A wrapper for the translation function."""
    return translate_text(text, target_lang, translation_cache)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    """Loads university data from CSV and cleans it."""
    try:
        df = pd.read_csv('data/universities.csv')
        # Ensure essential columns are strings to avoid errors
        for col in ['Subject', 'Level', 'University', 'Continent']:
            df[col] = df[col].astype(str).fillna('')
        return df
    except FileNotFoundError:
        st.error(T("The 'universities.csv' file was not found. Please make sure it's in the 'data' folder."))
        return pd.DataFrame()

df = load_data()

# --- UTILITY FUNCTION FOR CSV CONVERSION ---
@st.cache_data
def convert_df_to_csv(df_to_convert):
    """Converts a DataFrame to a CSV string for download."""
    return df_to_convert.to_csv(index=False).encode('utf-8')

# --- MAIN PAGE & FILTERS ---
st.title(f"🎓 {T('University Finder')}")

if not df.empty:
    st.sidebar.header(T("Filter Options"))

    # --- Sidebar Filters ---
    continents_english = sorted(df['Continent'].unique())
    continents_translated = [T(c) for c in continents_english]
    selected_continents_translated = st.sidebar.multiselect(T("Continent"), continents_translated, default=continents_translated)
    
    # Map translated selections back to English for filtering
    selected_continents_english = [continents_english[continents_translated.index(c)] for c in selected_continents_translated]

    all_subjects_english = sorted(list(set(subject.strip() for sublist in df['Subject'].str.split(';') for subject in sublist if subject)))
    all_subjects_translated = [T("All")] + [T(s) for s in all_subjects_english]
    selected_subject_translated = st.sidebar.selectbox(T("Subject"), all_subjects_translated)

    all_levels_english = sorted(list(set(level.strip() for levellist in df['Level'].str.split(';') for level in levellist if level)))
    all_levels_translated = [T("All")] + [T(l) for l in all_levels_english]
    selected_level_translated = st.sidebar.selectbox(T("Level"), all_levels_translated)

    # --- Main search bar ---
    search_query = st.text_input(T("Search by University Name"))

    # --- Filtering Logic ---
    filtered_df = df[df['Continent'].isin(selected_continents_english)]

    if selected_subject_translated != T("All"):
        # Find the original English subject to filter the dataframe
        selected_index = all_subjects_translated.index(selected_subject_translated)
        selected_subject_english = all_subjects_english[selected_index - 1] # -1 to account for "All"
        filtered_df = filtered_df[filtered_df['Subject'].str.contains(selected_subject_english, case=False, na=False)]

    if selected_level_translated != T("All"):
        # Find the original English level to filter the dataframe
        selected_index = all_levels_translated.index(selected_level_translated)
        selected_level_english = all_levels_english[selected_index - 1] # -1 to account for "All"
        filtered_df = filtered_df[filtered_df['Level'].str.contains(selected_level_english, case=False, na=False)]
    
    if search_query:
        # Search is performed on the original, non-translated university names
        filtered_df = filtered_df[filtered_df['University'].str.contains(search_query, case=False, na=False)]

    # --- DOWNLOAD BUTTON ---
    if not filtered_df.empty:
        st.download_button(
           label=T("Download results as CSV"),
           data=convert_df_to_csv(filtered_df),
           file_name='gerbang_kampus_universities.csv',
           mime='text/csv',
        )

    # --- DISPLAY RESULTS ---
    if not filtered_df.empty:
        st.write(f"{T('Displaying')} {len(filtered_df)} {T('universities')}")
        for index, row in filtered_df.iterrows():
            # Use an expander to show details for each university
            with st.expander(f"**{row['University']}** ({T('Rank')}: {row['Rank']})"):
                st.write(f"**{T('Continent')}:** {row['Continent']}")
                st.write(f"**{T('Subjects')}:** {row['Subject'].replace(';', ', ')}")
                st.write(f"**{T('Levels')}:** {row['Level'].replace(';', ', ')}")
                
                st.info(f"""
                **{T('Website')}:** [{row['Website']}]({row['Website']})
                \n**{T('Email')}:** {row['Email']}
                \n**{T('Application Opens')}:** {row['Application_Open']}
                \n**{T('Tuition Range (USD)')}:** {row['Tuition_USD_Range']}
                \n**{T('Subject Expertise')}:** {row['Subject_Expertise']}
                """)
    else:
        st.warning(T("No universities found for the selected criteria."))
