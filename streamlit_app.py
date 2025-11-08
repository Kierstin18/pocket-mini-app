import streamlit as st
import json
import random
from datetime import datetime

# try optional auto-refresh helper (install via requirements if missing)
try:
    from streamlit_autorefresh import st_autorefresh
    _HAS_AUTOREFRESH = True
except Exception:
    _HAS_AUTOREFRESH = False

# Page config
st.set_page_config(page_title="Pocket Mini App", page_icon="❤️", layout="wide")

# Initialize session state
st.session_state.setdefault("count", 0)
st.session_state.setdefault("notes", [])
st.session_state.setdefault("score", 0)
st.session_state.setdefault("round", 1)
st.session_state.setdefault("target", random.randrange(25))  # 5x5 grid index 0..24

# Sidebar: upload / import / export / controls
with st.sidebar:
    st.title("Pocket Mini App")
    st.markdown("Controls & data")

    # HEART SPEED: slider to control auto-move interval (ms). Lower = faster.
    st.markdown("### Heart speed (hardness)")
    speed_ms = st.slider("Move interval (ms) — lower = faster", min_value=200, max_value=3000, value=900, step=100)

    uploaded = st.file_uploader("Upload CSV / JSON / TXT", type=["csv", "json", "txt"])
    if uploaded:
        name = uploaded.name
        st.write(f"Uploaded: {name} ({uploaded.size} bytes)")
        ext = name.split(".")[-1].lower()
        try:
            if ext == "csv":
                import pandas as pd
                df = pd.read_csv(uploaded)
                st.write(df.head())
            elif ext == "json":
                data = json.load(uploaded)
                st.json(data)
            else:
                text = uploaded.read().decode("utf-8")
                st.text_area("Contents", text, height=200)
        except Exception as e:
            st.error(f"Error reading file: {e}")

    st.divider()
    st.subheader("Import / Export")
    if st.button("Export app data (download)"):
        payload = {
            "notes": st.session_state.notes,
            "score": st.session_state.score,
            "count": st.session_state.count,
            "round": st.session_state.round,
        }
        st.download_button(
            "Download JSON",
            data=json.dumps(payload, indent=2),
            file_name="pocket-data.json",
            mime="application/json",
        )

    st.markdown("---")
    st.caption("Tip: Upload sample_data.csv to preview CSV")

# if autorefresh helper available, register it to trigger reruns
if _HAS_AUTOREFRESH:
    # This causes the app to rerun every speed_ms milliseconds.
    st_autorefresh(interval=speed_ms, key="auto_refresh")

# Small CSS tweaks for larger buttons and spacing
st.markdown(
    """
    <style>
    .stButton>button { padding: .8rem 1rem; font-size:1rem; }
    .grid-btn { width:64px; height:64px; font-size:24px; }
    .note-box { background:#fff; padding:8px; border-radius:8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Main layout: left wide for counter/notes, right for mini-game
left, right = st.columns([2, 1])

with left:
    st.header("Counter & Notes")
    # Counter
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("Increment +1"):
            st.session_state.count += 1
    with c2:
        if st.button("Reset Counter"):
            st.session_state.count = 0
    with c3:
        st.metric("Clicks", st.session_state.count)

    st.markdown("### Notes")
    note_col1, note_col2 = st.columns([4,1])
    with note_col1:
        note_text = st.text_input("Write a quick note", key="note_input")
    with note_col2:
        if st.button("Add Note", key="add_note"):
            if note_text.strip():
                st.session_state.notes.insert(
                    0, {"id": datetime.now().timestamp(), "text": note_text.strip()}
                )
                st.experimental_rerun()

    if st.session_state.notes:
        for n in st.session_state.notes:
            st.markdown(f"<div class='note-box'>{n['text']}</div>", unsafe_allow_html=True)
            if st.button("Delete", key=f"del_{n['id']}"):
                st.session_state.notes = [x for x in st.session_state.notes if x["id"] != n["id"]]
                st.experimental_rerun()
    else:
        st.info("No notes yet. Add one in the input above.")

with right:
    st.header("Catch the Heart 🎯")
    st.write("Click the heart in the 5×5 grid. Each hit increases score and round.")

    # Display metrics
    st.metric("Score", st.session_state.score, delta=st.session_state.round - 1)
    st.metric("Round", st.session_state.round)

    # Auto-move the target on each refresh to increase difficulty
    # If streamlit_autorefresh isn't available the game still works (manual clicks only).
    if _HAS_AUTOREFRESH:
        # move to a different random cell (ensure it's different for visible movement)
        old = st.session_state.target
        new = old
        attempt = 0
        while new == old and attempt < 5:
            new = random.randrange(25)
            attempt += 1
        st.session_state.target = new

    # 5x5 grid of buttons; target is a random index
    grid_cols = 5
    clicked = False
    new_target = st.session_state.target

    for row in range(5):
        cols = st.columns(5)
        for col_index, col in enumerate(cols):
            idx = row * grid_cols + col_index
            label = "❤️" if idx == st.session_state.target else "○"
            btn_key = f"cell_{idx}"
            if col.button(label, key=btn_key):
                clicked = True
                if idx == st.session_state.target:
                    st.session_state.score += 1
                    st.session_state.round += 1
                    # on hit, jump to a new random cell immediately
                    new_target = random.randrange(25)
                else:
                    st.warning("Missed! Try again.")
                    # on miss, move target faster by selecting a new one
                    new_target = random.randrange(25)

    if clicked:
        st.session_state.target = new_target
        st.experimental_rerun()

    st.markdown("---")
    if st.button("Restart Game"):
        st.session_state.score = 0
        st.session_state.round = 1
        st.session_state.target = random.randrange(25)
        st.success("Game reset.")

st.markdown("---")
st.caption("Made with ❤️ — Run locally with: streamlit run streamlit_app.py")