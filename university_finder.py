import streamlit as st
import pandas as pd

@st.cache_data
def convert_df_to_csv(df_to_convert):
    """Converts a DataFrame to a CSV string for download."""
    return df_to_convert.to_csv(index=False).encode('utf-8')

def show_page(T, df):
    """
    Renders the University Finder page with dynamic checkbox filters.
    """
    st.title(f"🎓 {T('University Finder')}")

    if df.empty:
        st.error(T("University data could not be loaded."))
        return

    # --- SIDEBAR FILTERS (Using Checkboxes) ---
    st.sidebar.header(T("Filter Options"))

    # Continent Checkboxes
    st.sidebar.subheader(T("Continent"))
    continents_english = sorted(df['Continent'].unique())
    selected_continents = [continent for continent in continents_english if st.sidebar.checkbox(T(continent), value=True, key=f"continent_{continent}")]

    # Subject Checkboxes
    st.sidebar.subheader(T("Subject"))
    all_subjects_english = sorted(list(set(subject.strip() for sublist in df['Subject'].str.split(';') for subject in sublist if subject)))
    selected_subjects = [subject for subject in all_subjects_english if st.sidebar.checkbox(T(subject), value=False, key=f"subject_{subject}")]

    # Level Checkboxes
    st.sidebar.subheader(T("Degree Level"))
    all_levels_english = sorted(list(set(level.strip() for levellist in df['Level'].str.split(';') for level in levellist if level)))
    selected_levels = [level for level in all_levels_english if st.sidebar.checkbox(T(level), value=False, key=f"level_{level}")]

    # --- MAIN CONTENT AREA ---
    search_query = st.text_input(T("Search by University Name, Subject, or Continent"), placeholder=T("e.g., Harvard, Engineering, Asia"))

    # --- FILTERING LOGIC ---
    filtered_df = df.copy()

    # General search query logic
    if search_query:
        filtered_df = filtered_df[
            filtered_df['University'].str.contains(search_query, case=False, na=False) |
            filtered_df['Subject'].str.contains(search_query, case=False, na=False) |
            filtered_df['Continent'].str.contains(search_query, case=False, na=False)
        ]

    # Checkbox filter logic
    if selected_continents:
        filtered_df = filtered_df[filtered_df['Continent'].isin(selected_continents)]
    else:
        # If no continents are selected, show nothing
        filtered_df = pd.DataFrame(columns=df.columns)

    if selected_subjects:
        # Create a regex pattern to match any of the selected subjects
        subject_pattern = '|'.join(selected_subjects)
        filtered_df = filtered_df[filtered_df['Subject'].str.contains(subject_pattern, case=False, na=False)]

    if selected_levels:
        # Create a regex pattern to match any of the selected levels
        level_pattern = '|'.join(selected_levels)
        filtered_df = filtered_df[filtered_df['Level'].str.contains(level_pattern, case=False, na=False)]

    # --- DISPLAY RESULTS ---
    st.write("---")
    st.write(f"**{T('Showing')} {len(filtered_df)} {T('results')}**")

    if not filtered_df.empty:
        # --- DOWNLOAD BUTTON ---
        st.download_button(
           label=T("Download results as CSV"),
           data=convert_df_to_csv(filtered_df),
           file_name='gerbang_kampus_universities.csv',
           mime='text/csv',
        )
        
        # Display each university in a bordered container
        for index, row in filtered_df.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"{row['University']}")
                    st.caption(f"{T('Continent')}: {row['Continent']} | {T('Rank')}: {row['Rank']}")
                with col2:
                    st.link_button(T("Visit Website"), row['Website'], use_container_width=True)

                st.markdown(f"**{T('Available Subjects')}:** {row['Subject'].replace(';', ', ')}")
                st.markdown(f"**{T('Degree Levels')}:** {row['Level'].replace(';', ', ')}")
                
                with st.expander(T("More Information")):
                    st.write(f"**{T('Email')}:** {row['Email']}")
                    st.write(f"**{T('Application Opens')}:** {row['Application_Open']}")
                    st.write(f"**{T('Tuition Range (USD)')}:** {row['Tuition_USD_Range']}")
                    st.write(f"**{T('Subject Expertise')}:** {row['Subject_Expertise']}")
    else:
        st.warning(T("No universities found for the selected criteria. Try adjusting your filters."))
