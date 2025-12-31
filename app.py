import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Setup Page Title
st.set_page_config(page_title="Campus Study Buddy", layout="centered")
st.title("📖 Campus Study Buddy")
st.write("Find someone to grind with. No login required.")

# 2. Connect to your Google Sheet (via URL)
# Replace 'YOUR_SHEET_URL' with your Google Sheet link (must be 'Anyone with link can view')
SHEET_ID = "YOUR_SHEET_ID_HERE"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

try:
    df = pd.read_csv(url)
    st.subheader("Current Sessions")
    st.table(df) # Displays your spreadsheet data
except:
    st.info("Add the first session below to get started!")

# 3. The "Add Session" Form
with st.form("add_session", clear_on_submit=True):
    st.subheader("Post a Session")
    course = st.text_input("Course Name")
    loc = st.text_input("Where are you?")
    goal = st.selectbox("Goal", ["Exam Prep", "Homework", "Reading"])
    
    submitted = st.form_submit_button("Post to Map")
    if submitted:
        # In a real app, this would append to the sheet
        st.success(f"Posted {course} at {loc}!")
        st.balloons()
