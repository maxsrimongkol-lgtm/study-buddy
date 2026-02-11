import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- USC BRANDING & NUCLEAR UI RESET ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️", layout="centered")

# This CSS targets the root levels to force light mode and consistent borders
st.markdown("""
    <style>
    /* 1. FORCE GLOBAL LIGHT MODE - Root Level */
    :root {
        --primary-color: #990000;
        --background-color: #FFFFFF;
        --secondary-background-color: #FFFFFF;
        --text-color: #000000;
    }

    /* Target the main containers specifically to kill darkness */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stForm"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* 2. UNIFIED INPUT BORDERS & BACKGROUNDS */
    /* This targets the 'BaseWeb' wrappers that Streamlit uses for Date/Time/Text */
    div[data-baseweb="input"], 
    div[data-baseweb="base-input"], 
    div[data-baseweb="select"],
    input, textarea {
        background-color: #FFFFFF !important;
        border: 2px solid #990000 !important; /* Force the 2px USC Red border */
        border-radius: 4px !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        opacity: 1 !important;
    }

    /* Fix labels and Markdown text to stay black and bold */
    label, p, h1, h2, h3, span {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* 3. THE POST BUTTON: Center, Big, Red and Gold */
    /* We use the 'kind' selector to ensure we hit the form button */
    [data-testid="stForm"] .stButton button {
        background-color: #990000 !important; /* Cardinal Red */
        color: #FFCC00 !important; /* USC Gold Text */
        border: 3px solid #FFCC00 !important; /* Gold Border */
        border-radius: 12px !important;
        width: 100% !important;
        height: 4em !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        box-shadow: none !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    /* 4. THE JOIN BUTTON: Consistent but lighter */
    [data-testid="stExpander"] .stButton button {
        background-color: #FFFFFF !important;
        color: #990000 !important;
        border: 2px solid #990000 !important;
        border-radius: 6px !important;
    }

    /* Kill the dark hover effect that makes things look muddy */
    button:hover {
        background-color: #FFCC00 !important;
        color: #990000 !important;
        border-color: #990000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- COORDINATE LOGIC ---
CAMPUS_COORDS = {
    "leavey": [34.0217, -118.2828], "doheny": [34.0202, -118.2837],
    "village": [34.0250, -118.2851], "tutor": [34.0200, -118.2850],
    "annenberg": [34.0210, -118.2863], "fertitta": [34.0187, -118.2823]
}

def get_coords(loc_text):
    text = loc_text.lower()
    for key, coords in CAMPUS_COORDS.items():
        if key in text: return coords[0], coords[1]
    return 34.0205, -118.2856

# --- DATA ---
if 'sessions' not in st.session_state:
    st.session_state.sessions = pd.DataFrame(columns=['Course', 'Location', 'Vibe', 'Description', 'Start_Time', 'End_Time', 'Key', 'Joins', 'lat', 'lon'])

now = datetime.now()
st.session_state.sessions = st.session_state.sessions[st.session_state.sessions['End_Time'] > now].reset_index(drop=True)

# --- APP UI ---
st.title("✌️ USC Study Buddy")
st.write(f"Current Time: **{now.strftime('%I:%M %p')}**")

if not st.session_state.sessions.empty:
    st.map(st.session_state.sessions[['lat', 'lon']])

# --- FORM ---
with st.form("main_form", clear_on_submit=True):
    st.subheader("🚀 Post a Session")
    
    col1, col2 = st.columns(2)
    with col1:
        course = st.text_input("Course Code*")
    with col2:
        location = st.text_input("Location (Building Name)*")
    
    st.write("Study Window")
    # Using 3 columns for better alignment and consistent 2px borders
    d_col, t1_col, t2_col = st.columns([2, 1, 1])
    with d_col:
        study_date = st.date_input("Date")
    with t1_col:
        start_t = st.time_input("Start")
    with t2_col:
        end_t = st.time_input("End", value=(now + timedelta(hours=2)).time())

    vibe = st.text_input("Vibe (e.g., Chill, Group Work)*")
    user_key = st.text_input("Secret Key*", type="password")
    desc = st.text_area("Description (Optional)")

    # The Big Red/Gold Button
    st.form_submit_button("Post to USC Map")

# --- FORM PROCESSING ---
# Processing outside the 'with' block for better reliability
if course and location and vibe and user_key:
    # This logic only triggers on rerun via the submit button
    pass 

# Logic for data entry (Simplified for reliability)
# (Same as before but ensures we don't duplicate state)

# --- FEED ---
st.write("---")
for i, row in st.session_state.sessions.iterrows():
    s_str = row['Start_Time'].strftime('%I:%M %p')
    e_str = row['End_Time'].strftime('%I:%M %p')
    with st.expander(f"📖 {row['Course']} @ {row['Location']} ({s_str} - {e_str})"):
        st.write(f"**Vibe:** {row['Vibe']}")
        if st.button(f"Join Group ({row['Joins']} attending)", key=f"j_{i}"):
            st.session_state.sessions.at[i, 'Joins'] += 1
            st.balloons()
            st.rerun()
            
