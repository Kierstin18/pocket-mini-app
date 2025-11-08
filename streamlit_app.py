import streamlit as st
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Pocket Mini App",
    page_icon="❤️",
    layout="wide"
)

# Initialize session state
if 'count' not in st.session_state:
    st.session_state.count = 0
if 'notes' not in st.session_state:
    st.session_state.notes = []
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'round' not in st.session_state:
    st.session_state.round = 1

# Header with custom CSS for gradient background
st.markdown("""
    <style>
    .main {
        background: linear-gradient(180deg, #fce7f3 0%, #f3e8ff 100%);
    }
    .stButton button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🎮 Pocket Mini App")
st.markdown("A tiny pack: counter, notes, and mini-game!")

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Counter & Notes 📝")
    
    # Counter
    st.write(f"Clicks: {st.session_state.count}")
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        if st.button("Increment (+1)"):
            st.session_state.count += 1
    with col1_2:
        if st.button("Reset Counter"):
            st.session_state.count = 0
    
    # Notes
    st.divider()
    note_text = st.text_input("Write a quick note...")
    if st.button("Add Note") and note_text.strip():
        st.session_state.notes.insert(0, {
            'id': datetime.now().timestamp(),
            'text': note_text.strip()
        })
    
    if st.session_state.notes:
        for note in st.session_state.notes:
            col_note, col_del = st.columns([4,1])
            with col_note:
                st.text(note['text'])
            with col_del:
                if st.button("🗑️", key=f"del_{note['id']}"):
                    st.session_state.notes = [n for n in st.session_state.notes if n['id'] != note['id']]
                    st.rerun()

with col2:
    st.subheader("Score Board 🎯")
    score_col, round_col = st.columns(2)
    with score_col:
        st.metric("Score", st.session_state.score)
    with round_col:
        st.metric("Round", st.session_state.round)
    
    game_col1, game_col2 = st.columns(2)
    with game_col1:
        if st.button("Next Round ➡️"):
            st.session_state.round += 1
            st.session_state.score += 1
    with game_col2:
        if st.button("Reset Game 🔄"):
            st.session_state.score = 0
            st.session_state.round = 1

# Export section
st.divider()
st.subheader("Share & Export 💾")
exp_col1, exp_col2 = st.columns(2)

with exp_col1:
    if st.button("Export as JSON"):
        data = {
            "notes": st.session_state.notes,
            "score": st.session_state.score,
            "count": st.session_state.count
        }
        st.download_button(
            "📥 Download JSON",
            data=json.dumps(data, indent=2),
            file_name="pocket-data.json",
            mime="application/json"
        )

with exp_col2:
    uploaded_file = st.file_uploader("Import JSON data", type=['json'])
    if uploaded_file:
        try:
            data = json.load(uploaded_file)
            if st.button("Load Data"):
                st.session_state.notes = data.get('notes', [])
                st.session_state.score = data.get('score', 0)
                st.session_state.count = data.get('count', 0)
                st.success("Data loaded successfully!")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")

st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")