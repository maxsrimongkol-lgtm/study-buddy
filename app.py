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

# --- THE POSTING SECTION ---
st.markdown("---")
with st.form("main_form", clear_on_submit=True):
    st.subheader("🚀 Create a Study Session")
    
    # Grid Layout for inputs
    c1, c2 = st.columns(2)
    with c1: course = st.text_input("Course Code (e.g., WRIT 150)")
    with c2: location = st.text_input("Location (e.g., Leavey Basement)")
    
    st.markdown("**When are you studying?**")
    d_col, t1_col, t2_col = st.columns([2, 1, 1])
    with d_col: study_date = st.date_input("Date", label_visibility="collapsed")
    with t1_col: start_t = st.time_input("Start Time", label_visibility="collapsed")
    with t2_col: end_t = st.time_input("End Time", value=(now + timedelta(hours=2)).time(), label_visibility="collapsed")

    vibe = st.text_input("Session Vibe (e.g., No Talking, Group Discussion)")
    user_key = st.text_input("Secret Key (to delete)", type="password")
    desc = st.text_area("What are you working on? (Optional)")

    # The Big Red/Gold Button
    if st.form_submit_button("Post to USC Map"):
        if course and location and vibe and user_key:
            fs, fe = datetime.combine(study_date, start_t), datetime.combine(study_date, end_t)
            if fe > fs:
                lat, lon = get_coords(location)
                new_row = pd.DataFrame([{'Course': course.upper(), 'Location': location, 'Vibe': vibe, 'Description': desc, 'Start_Time': fs, 'End_Time': fe, 'Key': user_key, 'Joins': 0, 'lat': lat, 'lon': lon}])
                st.session_state.sessions = pd.concat([st.session_state.sessions, new_row], ignore_index=True)
                st.rerun()

# --- ACTIVE FEED ---
st.markdown("### 🤝 Join a Session")
if st.session_state.sessions.empty:
    st.write("_Check back later for active groups._")

for i, row in st.session_state.sessions.iterrows():
    s_time = row['Start_Time'].strftime('%I:%M %p')
    e_time = row['End_Time'].strftime('%I:%M %p')
    
    with st.expander(f"📖 {row['Course']} @ {row['Location']} ({s_time} - {e_time})"):
        st.write(f"**Vibe:** {row['Vibe']}")
        if row['Description']: st.info(row['Description'])
        
        # Consistent Join Button
        if st.button(f"Join Group • {row['Joins']} attending", key=f"join_{i}"):
            st.session_state.sessions.at[i, 'Joins'] += 1
            st.balloons()
            st.rerun()
