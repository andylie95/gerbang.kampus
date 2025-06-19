import streamlit as st
import pandas as pd

@st.cache_data
def convert_df_to_csv(df_to_convert):
    """Converts a DataFrame to a CSV string for download."""
    return df_to_convert.to_csv(index=False).encode('utf-8')

def show_page(T, df):
    """
    Renders the University Finder page.
    """
    st.title(f"🎓 {T('University Finder')}")

    if not df.empty:
        # Sidebar Filters
        continents_english = sorted(df['Continent'].unique())
        continents_translated = [T(c) for c in continents_english]
        selected_continents_translated = st.sidebar.multiselect(T("Continent"), continents_translated, default=continents_translated)
        selected_continents_english = [continents_english[continents_translated.index(c)] for c in selected_continents_translated]

        all_subjects_english = sorted(list(set(subject.strip() for sublist in df['Subject'].str.split(';') for subject in sublist if subject)))
        all_subjects_translated = [T("All")] + [T(s) for s in all_subjects_english]
        selected_subject_translated = st.sidebar.selectbox(T("Subject"), all_subjects_translated)

        all_levels_english = sorted(list(set(level.strip() for levellist in df['Level'].str.split(';') for level in levellist if level)))
        all_levels_translated = [T("All")] + [T(l) for l in all_levels_english]
        selected_level_translated = st.sidebar.selectbox(T("Level"), all_levels_translated)

        search_query = st.text_input(T("Search by University Name"))

        # Filtering Logic
        filtered_df = df[df['Continent'].isin(selected_continents_english)]

        if selected_subject_translated != T("All"):
            selected_index = all_subjects_translated.index(selected_subject_translated)
            selected_subject_english = all_subjects_english[selected_index - 1]
            filtered_df = filtered_df[filtered_df['Subject'].str.contains(selected_subject_english, case=False, na=False)]

        if selected_level_translated != T("All"):
            selected_index = all_levels_translated.index(selected_level_translated)
            selected_level_english = all_levels_english[selected_index - 1]
            filtered_df = filtered_df[filtered_df['Level'].str.contains(selected_level_english, case=False, na=False)]
        
        if search_query:
            filtered_df = filtered_df[filtered_df['University'].str.contains(search_query, case=False, na=False)]

        # Download Button
        if not filtered_df.empty:
            st.download_button(
               label=T("Download results as CSV"),
               data=convert_df_to_csv(filtered_df),
               file_name='gerbang_kampus_universities.csv',
               mime='text/csv',
            )

        # Display Results
        if not filtered_df.empty:
            st.write(f"{T('Displaying')} {len(filtered_df)} {T('universities')}")
            for index, row in filtered_df.iterrows():
                with st.expander(f"**{row['University']}** ({T('Rank')}: {row['Rank']})"):
                    st.write(f"**{T('Continent')}:** {row['Continent']}")
                    st.write(f"**{T('Subjects')}:** {row['Subject'].replace(';', ', ')}")
                    # ... (rest of the display logic) ...
        else:
            st.warning(T("No universities found for the selected criteria."))
    else:
        st.error(T("University data could not be loaded."))
