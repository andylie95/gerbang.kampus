import streamlit as st
from collections import Counter
import time

def show_page(T, questions, career_mapping, uni_df):
    """
    Renders the chat-based assessment and provides university recommendations.
    """
    st.title(f"📝 {T('Career Assessment')}")
    st.write(T("Answer the questions as they appear to discover your recommended subjects."))

    # Initialize session state for the chat
    if "assessment_step" not in st.session_state:
        st.session_state.assessment_step = 0
        st.session_state.assessment_answers = []
        st.session_state.chat_history = [{"role": "assistant", "content": T("Hi there! Ready to start your assessment?")}]

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Main chat logic
    if st.session_state.assessment_step < len(questions):
        current_q = questions[st.session_state.assessment_step]
        q_text = T(current_q['question'])

        if st.session_state.chat_history[-1]["content"] != q_text:
            st.session_state.chat_history.append({"role": "assistant", "content": q_text})
            st.rerun()

        response_options_english = ('Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree')
        response_options_translated = [T(opt) for opt in response_options_english]
        
        cols = st.columns(len(response_options_translated))
        for i, option_translated in enumerate(response_options_translated):
            if cols[i].button(option_translated, use_container_width=True, key=f"q_{st.session_state.assessment_step}_{i}"):
                st.session_state.chat_history.append({"role": "user", "content": option_translated})
                st.session_state.assessment_answers.append({
                    "category": current_q['category'],
                    "answer": response_options_english[i]
                })
                st.session_state.assessment_step += 1
                st.rerun()

    else: # Assessment is finished
        if "results_calculated" not in st.session_state:
            with st.spinner(T("Analyzing your answers...")):
                time.sleep(1)
                scores = {category: 0 for category in career_mapping.keys()}
                value_map = {'Strongly Disagree': -2, 'Disagree': -1, 'Neutral': 0, 'Agree': 1, 'Strongly Agree': 2}

                for ans in st.session_state.assessment_answers:
                    scores[ans['category']] += value_map[ans['answer']]

                positive_scores = {cat: score for cat, score in scores.items() if score > 0}
                top_categories = sorted(positive_scores, key=positive_scores.get, reverse=True)[:2] # Get top 2 categories

                results_text = f"### {T('Your Top 2 Recommended Subjects')}:\n"
                recommended_subjects = []
                if top_categories:
                    recommendations = []
                    for category in top_categories:
                        recommendations.extend(career_mapping.get(category, []))
                    
                    final_recommendations = Counter(recommendations).most_common(2) # Get top 2 subjects
                    for subject, count in final_recommendations:
                        recommended_subjects.append(subject)
                        results_text += f"- **{T(subject)}**\n"
                else:
                    results_text += T("Your responses did not strongly point to a specific category. Try again to get a recommendation.")
                
                st.session_state.chat_history.append({"role": "assistant", "content": results_text})

                # --- NEW: AI RECOMMENDATION PART ---
                if recommended_subjects:
                    reco_text = f"\n---\n\n### {T('AI University Recommendations')}\n"
                    reco_text += f"{T('Based on your results, here are the top-ranked universities for your recommended subjects:')}\n"
                    
                    for subject in recommended_subjects:
                        reco_text += f"\n#### {T('Top 5 for')} **{T(subject)}**\n"
                        # Filter universities that offer the subject and sort by rank
                        subject_df = uni_df[uni_df['Subject'].str.contains(subject, case=False, na=False)].sort_values(by='Rank').head(5)
                        if not subject_df.empty:
                            for i, row in subject_df.iterrows():
                                reco_text += f"1. **{row['University']}** ({T('Rank')}: {row['Rank']})\n"
                        else:
                            reco_text += f"_{T('No specific top universities found in our database for this subject.')}_\n"
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": reco_text})


                st.session_state.results_calculated = True
                st.rerun()

        if st.button(T("Take Assessment Again")):
            # Reset all relevant session state keys
            for key in ["assessment_step", "assessment_answers", "chat_history", "results_calculated"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
