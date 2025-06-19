import streamlit as st
import json
from collections import Counter
from utils import translate_text, language_selector, get_translation_cache

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Career Assessment", layout="centered")

# --- LANGUAGE SELECTION & TRANSLATION SETUP ---
target_lang = language_selector()
translation_cache = get_translation_cache()

def T(text):
    """A wrapper for the translation function."""
    return translate_text(text, target_lang, translation_cache)

# --- DATA LOADING ---
@st.cache_data
def load_assessment_data():
    """Loads questions and career mappings from the JSON file."""
    try:
        with open('data/assessment_questions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['questions'], data['career_mapping']
    except FileNotFoundError:
        st.error(T("The 'assessment_questions.json' file was not found. Please make sure it's in the 'data' folder."))
        return [], {}

questions, career_mapping = load_assessment_data()

# --- MAIN PAGE ---
st.title(f"📝 {T('Career Assessment')}")
st.write(T("Answer the following questions to get a recommended subject based on your strengths."))

if questions:
    if 'answers' not in st.session_state:
        st.session_state.answers = {}

    # Define response options in English (the source language)
    response_options_english = ('Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree')
    # Create a translated list for the UI
    response_options_translated = [T(opt) for opt in response_options_english]

    # Display questions one by one
    for i, q_data in enumerate(questions):
        question_text = T(q_data['question'])
        
        # The radio button displays translated options
        selected_translated_option = st.radio(
            question_text, 
            response_options_translated, 
            key=f"q_{i}",
            horizontal=True
        )
        # Find the index of the selected translated option
        selected_index = response_options_translated.index(selected_translated_option)
        # Store the original English value for processing
        st.session_state.answers[i] = response_options_english[selected_index]

    # Submit button
    if st.button(T("Get Recommendation")):
        # Initialize scores for each category
        scores = {category: 0 for category in career_mapping.keys()}
        value_map = {'Strongly Disagree': -2, 'Disagree': -1, 'Neutral': 0, 'Agree': 1, 'Strongly Agree': 2}

        # Calculate scores based on user's answers
        for i, q_data in enumerate(questions):
            category = q_data['category']
            answer = st.session_state.answers.get(i)
            if answer:
                scores[category] += value_map[answer]

        # Get top 3 categories where the score is positive
        positive_scores = {cat: score for cat, score in scores.items() if score > 0}
        top_categories = sorted(positive_scores, key=positive_scores.get, reverse=True)[:3]

        # Generate and display recommendations
        if top_categories:
            recommendations = []
            for category in top_categories:
                recommendations.extend(career_mapping.get(category, []))
            
            final_recommendations = Counter(recommendations).most_common(5)

            st.success(f"### {T('Your Recommended Subjects')}:")
            for subject, count in final_recommendations:
                st.write(f"- **{T(subject)}**") # Translate the final subject names
            
            st.info(T("Use the University Finder to search for universities offering these subjects!"))
        else:
            st.warning(T("Your responses did not strongly point to a specific category. Try answering more questions with 'Agree' or 'Strongly Agree' to get a recommendation."))
