import streamlit as st
import json
import random
from datetime import datetime

# Optional autofresh helper for smooth gliding (add to requirements: streamlit-autorefresh)
try:
    from streamlit_autorefresh import st_autorefresh
    _HAS_AUTOREFRESH = True
except Exception:
    _HAS_AUTOREFRESH = False

GRID = 5

def idx_to_xy(i):
    return i % GRID, i // GRID

def xy_to_idx(x, y):
    return y * GRID + x

def manhattan_path(start, end):
    sx, sy = idx_to_xy(start)
    ex, ey = idx_to_xy(end)
    path = []
    cx, cy = sx, sy
    while (cx, cy) != (ex, ey):
        if cx < ex: cx += 1
        elif cx > ex: cx -= 1
        elif cy < ey: cy += 1
        elif cy > ey: cy -= 1
        path.append(xy_to_idx(cx, cy))
    return path

# Page config and styles to mimic the React UI look
st.set_page_config(page_title="Pocket Mini App", page_icon="❤️", layout="wide")
st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg,#fff4f8 0%,#f3e8ff 100%); }
    .card { background: white; border-radius:16px; padding:18px; box-shadow: 0 6px 18px rgba(15,23,42,0.06); }
    .small { font-size:0.9rem; color:#6b7280; }
    .btn-wide > button { width:100%; padding:10px 14px; border-radius:10px; }
    .heart { font-size:28px; }
    .grid-btn button { width:56px; height:56px; border-radius:10px; font-size:20px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# session defaults
st.session_state.setdefault("count", 0)
st.session_state.setdefault("notes", [])
st.session_state.setdefault("note_text", "")
st.session_state.setdefault("score", 0)
st.session_state.setdefault("round", 1)
st.session_state.setdefault("target", random.randrange(GRID * GRID))
st.session_state.setdefault("path", [])
st.session_state.setdefault("next_target", None)
st.session_state.setdefault("speed_ms", 700)

# Sidebar controls (upload/export/speed)
with st.sidebar:
    st.markdown("### Controls & Data")
    st.write("Heart speed (lower = faster)")
    st.session_state.speed_ms = st.slider("Move interval (ms)", 200, 2000, st.session_state.speed_ms, 100)
    uploaded = st.file_uploader("Upload CSV / JSON / TXT", type=["csv","json","txt"])
    if uploaded:
        name = uploaded.name
        st.write(f"Uploaded: {name} ({uploaded.size} bytes)")
        ext = name.split(".")[-1].lower()
        try:
            if ext == "csv":
                import pandas as pd
                df = pd.read_csv(uploaded)
                st.dataframe(df.head())
            elif ext == "json":
                data = json.load(uploaded)
                st.json(data)
            else:
                txt = uploaded.read().decode("utf-8")
                st.text_area("Contents", txt, height=200)
        except Exception as e:
            st.error(f"Error: {e}")
    st.divider()
    if st.button("Export app data (download)"):
        payload = {"notes": st.session_state.notes, "score": st.session_state.score, "count": st.session_state.count}
        st.download_button("Download JSON", data=json.dumps(payload, indent=2), file_name="pocket-data.json", mime="application/json")
    st.markdown("---")
    if not _HAS_AUTOREFRESH:
        st.info("Install streamlit-autorefresh in requirements for smooth gliding (optional).")

# auto-refresh registration for gliding
if _HAS_AUTOREFRESH:
    st_autorefresh(interval=st.session_state.speed_ms, key="autorefresh")

# Advance glide path one step per refresh/run
if st.session_state.get("path"):
    # move one step along path
    st.session_state.target = st.session_state["path"].pop(0)
    if not st.session_state["path"]:
        st.session_state["next_target"] = None

# Choose a new destination (when idle)
if not st.session_state.get("path") and st.session_state.get("next_target") is None:
    cur = st.session_state.target
    dest = cur
    attempts = 0
    while dest == cur and attempts < 10:
        dest = random.randrange(GRID * GRID)
        attempts += 1
    if dest != cur:
        st.session_state.next_target = dest
        st.session_state.path = manhattan_path(cur, dest)

# Layout: two columns like the React UI
left, right = st.columns([2, 1])

with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h2>Pocket Mini App</h2><div class='small'>A tiny pack: counter, notes, and a catch-the-heart mini-game.</div>", unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)

    # Counter card
    st.markdown("<div class='card' style='margin-top:12px'>", unsafe_allow_html=True)
    st.subheader("Counter")
    cols = st.columns([1,1,1])
    with cols[0]:
        if st.button("+1", key="inc"):
            st.session_state.count += 1
    with cols[1]:
        if st.button("Reset", key="reset_count"):
            st.session_state.count = 0
    with cols[2]:
        st.markdown(f"<div class='small'>Clicks: <strong>{st.session_state.count}</strong></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Notes card
    st.markdown("<div class='card' style='margin-top:14px'>", unsafe_allow_html=True)
    st.subheader("Notes")
    note_col, btn_col = st.columns([4,1])
    with note_col:
        st.session_state.note_text = st.text_input("", value=st.session_state.note_text, placeholder="Write a quick note...", key="note_input")
    with btn_col:
        if st.button("Add", key="add_note_btn"):
            txt = st.session_state.note_text.strip()
            if txt:
                st.session_state.notes.insert(0, {"id": datetime.now().timestamp(), "text": txt})
                st.session_state.note_text = ""
    st.write("")
    if not st.session_state.notes:
        st.info("No notes yet.")
    else:
        for n in st.session_state.notes:
            cols = st.columns([9,1])
            cols[0].write(n["text"])
            if cols[1].button("Delete", key=f"del_{n['id']}"):
                st.session_state.notes = [x for x in st.session_state.notes if x["id"] != n["id"]]
                st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # end left header card

with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Catch the Heart")
    st.markdown(f"<div class='small'>Round {st.session_state.round}</div>", unsafe_allow_html=True)
    st.write("")
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Game area: display a 5x5 grid; heart position from session_state.target
    st.markdown("<div class='card' style='padding:12px'>", unsafe_allow_html=True)
    st.markdown("<div class='small' style='margin-bottom:8px'>Click the moving heart!</div>", unsafe_allow_html=True)

    clicked = False
    for r in range(GRID):
        cols = st.columns(GRID, gap="small")
        for c_idx, col in enumerate(cols):
            idx = r * GRID + c_idx
            label = "❤️" if idx == st.session_state.target else "○"
            if col.button(label, key=f"cell_{idx}", help=f"cell {idx}"):
                clicked = True
                if idx == st.session_state.target:
                    st.session_state.score += 1
                    st.session_state.round += 1
                    # on hit, jump to new random dest and compute glide
                    dest = random.randrange(GRID * GRID)
                    attempts = 0
                    while dest == idx and attempts < 10:
                        dest = random.randrange(GRID * GRID)
                        attempts += 1
                    st.session_state.next_target = dest
                    st.session_state.path = manhattan_path(idx, dest)
                else:
                    st.warning("Missed! Try again.")
                    # on miss, nudge target
                    dest = random.randrange(GRID * GRID)
                    st.session_state.next_target = dest
                    st.session_state.path = manhattan_path(st.session_state.target, dest)

    st.write("")
    st.markdown(f"<div class='small'>Hits: <strong>{st.session_state.score}</strong></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # end game card

    st.write("")
    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        if st.button("Restart"):
            st.session_state.score = 0
            st.session_state.round = 1
            st.session_state.target = random.randrange(GRID * GRID)
            st.session_state.path = []
            st.session_state.next_target = None
    with c2:
        if st.button("Next Round"):
            st.session_state.round += 1
    with c3:
        st.markdown("<div class='small'>Best of quick reflexes</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # end right card

# Bottom full-width: Share & Export
st.markdown("<div class='card' style='margin-top:16px'>", unsafe_allow_html=True)
st.subheader("Share & Export")
st.write("You can copy your notes, export as JSON, or snapshot your score.")
col_a, col_b, col_c = st.columns([1,1,1])
with col_a:
    if st.button("Copy JSON to clipboard"):
        payload = {"notes": st.session_state.notes, "score": st.session_state.score, "count": st.session_state.count}
        # streamlit can't write to system clipboard server-side; provide download instead
        st.download_button("Download JSON", data=json.dumps(payload, indent=2), file_name="pocket-data.json", mime="application/json")
with col_b:
    if st.button("Download JSON"):
        payload = {"notes": st.session_state.notes, "score": st.session_state.score, "count": st.session_state.count}
        st.download_button("Download JSON File", data=json.dumps(payload, indent=2), file_name="pocket-data.json", mime="application/json")
with col_c:
    if st.button("Share (placeholder)"):
        st.info("Share feature placeholder.")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Made with ❤️ — Run locally with: streamlit run streamlit_app.py")
