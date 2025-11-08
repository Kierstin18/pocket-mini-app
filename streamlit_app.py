import streamlit as st
import json
from datetime import datetime

# Page config
st.set_page_config(page_title="Pocket Mini App", page_icon="❤️", layout="wide")

# Initialize session state
st.session_state.setdefault("count", 0)
st.session_state.setdefault("notes", [])
st.session_state.setdefault("score", 0)
st.session_state.setdefault("round", 1)

# Simple styles
st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg,#fce7f3 0%,#f3e8ff 100%); }
    .stButton>button { width:100% }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎮 Pocket Mini App")
st.markdown("A tiny pack: counter, notes, file upload and export.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Counter & Notes")
    st.write(f"Clicks: {st.session_state.count}")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Increment +1"):
            st.session_state.count += 1
    with c2:
        if st.button("Reset Counter"):
            st.session_state.count = 0

    st.divider()
    note = st.text_input("Write a quick note")
    if st.button("Add Note") and note.strip():
        st.session_state.notes.insert(0, {"id": datetime.now().timestamp(), "text": note.strip()})

    if st.session_state.notes:
        for n in st.session_state.notes:
            r1, r2 = st.columns([8,1])
            with r1:
                st.write(n["text"])
            with r2:
                if st.button("Delete", key=f"del_{n['id']}"):
                    st.session_state.notes = [x for x in st.session_state.notes if x["id"] != n["id"]]
                    st.experimental_rerun()
    else:
        st.info("No notes yet.")

with col2:
    st.subheader("Game & Export")
    st.metric("Score", st.session_state.score)
    st.metric("Round", st.session_state.round)
    g1, g2 = st.columns(2)
    with g1:
        if st.button("Next Round"):
            st.session_state.round += 1
            st.session_state.score += 1
    with g2:
        if st.button("Reset Game"):
            st.session_state.round = 1
            st.session_state.score = 0

st.divider()
st.subheader("File Upload / Import")
uploaded = st.file_uploader("Upload CSV / JSON / TXT", type=["csv", "json", "txt"])
if uploaded:
    name = uploaded.name
    st.write(f"Uploaded: {name} ({uploaded.size} bytes)")
    ext = name.split(".")[-1].lower()
    try:
        if ext == "csv":
            import pandas as pd
            df = pd.read_csv(uploaded)
            st.dataframe(df)
        elif ext == "json":
            data = json.load(uploaded)
            st.json(data)
        else:
            text = uploaded.read().decode("utf-8")
            st.text_area("Contents", text, height=200)
    except Exception as e:
        st.error(f"Error reading file: {e}")

st.divider()
st.subheader("Export / Save")
if st.button("Export app data as JSON"):
    payload = {"notes": st.session_state.notes, "score": st.session_state.score, "count": st.session_state.count}
    st.download_button("Download JSON", data=json.dumps(payload, indent=2), file_name="pocket-data.json", mime="application/json")

st.markdown("---")
st.caption("Made with ❤️ — run with: streamlit run streamlit_app.py")