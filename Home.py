import streamlit as st
import os
from vector_db import initialize_vector_db_if_needed

st.set_page_config(page_title="AI Summarizer", layout="wide")
st.title("📄 AI Meeting Summarizer")

# Initialize vector database on app startup
vector_db = initialize_vector_db_if_needed()

# Inject custom CSS for better button styling
st.markdown("""
    <style>
    .button-style {
        display: inline-block;
        padding: 1em 2em;
        margin: 0.5em;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 12px;
        width: 100%;
        transition: 0.3s ease-in-out;
    }
    .button-style:hover {
        background-color: #45a049;
        transform: scale(1.03);
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

transcript_dir = "data/Meetings"
meeting_files = [f for f in os.listdir(transcript_dir) if f.endswith(".pdf")]

def sort_by_date(filename):
    try:
        return tuple(map(int, filename.replace(".pdf", "").split(".")))
    except Exception:
        return (0, 0, 0)

meeting_files.sort(key=sort_by_date, reverse=True)

st.subheader("Select a meeting to summarize:")
st.divider()

# Display buttons in a grid (3 per row)
cols = st.columns(3)

for idx, meeting in enumerate(meeting_files):
    col = cols[idx % 3]
    label = meeting.replace(".pdf", "")
    with col:
        if st.button(f"📅 {label}", key=meeting):
            st.session_state["selected_meeting"] = meeting
            st.switch_page("pages/1_Summarizer.py")
