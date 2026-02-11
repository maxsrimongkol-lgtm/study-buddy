import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- USC BRANDING & UI OVERHAUL ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️", layout="centered")

st.markdown("""
    <style>
    /* 1. THE FOUNDATION: Clean White & Black */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
    }
    
    /* 2. REMOVE FORM SHADOWS: Makes the UI feel like a seamless app */
    [data-testid="stForm"] {
        border: none !important;
        padding: 0px !important;
        background-color: #FFFFFF !important;
    }

    /* 3. UNIFIED INPUTS: 2px Cardinal Red Borders, No Grey Backgrounds */
    div[data-baseweb="input"], div[data-baseweb="base-input"], textarea, input {
        background-color: #FFFFFF !important;
        border: 2px solid #990000 !important;
        border-radius: 8px !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    
    /* Force Labels to be Bold & Black */
    label, p, h1, h2, h3 {
        color: #000000 !important;
        font-family: 'Inter', sans-serif;
    }

    /* 4. THE POST BUTTON: Big, Centered, Red/Gold */
    .stButton button[kind="primaryFormSubmit"] {
        background: #990000 !important; /* Cardinal Red */
        color: #FFCC00 !important; /* Gold Text */
        border: 3px solid #FFCC00 !important; /* Gold Border */
        border-radius: 50px !important; /* Rounded pill shape */
        width: 100% !important;
        height: 3.5em !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        letter-spacing: 1px;
        box-shadow: 0px 4px 10px rgba(153, 0, 0, 0.2) !important;
        transition: 0.3s;
    }
    
    .stButton button[kind="primaryFormSubmit"]:hover {
        transform: scale(1.02);
        background: #7a0000 !important;
    }

    /* 5. ACTIVE SESSIONS: Clean Light Cards */
    [data-testid="stExpander"] {
        border: 1px solid #e0e0e0 !important;
        border-radius: 12px !important;
        background-color: #fafafa !important;
        margin-bottom: 10px !important;
    }

    /* 6. HIDE DECORATION */
    [data-testid="stDecoration"] { display: none; }
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

# --- DATA PERSISTENCE ---
if 'sessions' not in st.session_state:
    st.session_state.sessions = pd.DataFrame(columns=['Course', 'Location', 'Vibe', 'Description', 'Start_Time', 'End_Time', 'Key', 'Joins', 'lat', 'lon'])

now = datetime.now()
st.session_state.sessions = st.session_state.sessions[st.session_state.sessions['End_Time'] > now].reset_index(drop=True)

# --- HEADER ---
st.title("✌️ USC Study Buddy")
st.caption(f"Current Time: {now.strftime('%I:%M %p')} • University of Southern California")

# --- MAP (Visible only if active) ---
if not st.session_state.sessions.empty:
    st.map(st.session_state.sessions[['lat', 'lon']], zoom=14)
else:
    st.info("📍 No active sessions. Be the first to start one below!")

# ---
