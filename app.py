import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- USC BRANDING & UI ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1, h2, h3 { color: #990000 !important; }
    input, select, textarea, [data-baseweb="select"], [data-baseweb="input"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #990000 !important;
        border-radius: 6px !important;
    }
    div.stButton > button:first-child {
        background-color: #990000 !important;
        color: #FFC72C !important;
        height: 4em !important;
        width: 100% !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        border: 2px solid #FFC72C !important;
        border-radius: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- COORDINATE LOGIC ---
# Standard GPS for USC Hubs
CAMPUS_COORDS = {
    "leavey": [34.0217, -118.2828],
    "doheny": [34.0202, -118.2837],
    "fertitta": [34.0187, -118.2823],
    "village": [34.0250, -118.2851],
    "annenberg": [34.0210, -118.2863],
    "tutor": [34.0200, -118.2850],
    "marshall": [34.0189, -118.2838],
    "viterbi": [34.0205, -118.2890]
}

def get_coords(loc_text):
    text = loc_text.lower()
    for key, coords in CAMPUS_COORDS.items():
        if key in text:
            return coords[0], coords[1]
    return 34.0205, -118.2856 # Default to Tommy Trojan

# --- DATA INITIALIZATION ---
if 'sessions' not in st.session_state:
    st.session_state.sessions = pd.DataFrame(columns=[
        'Course', 'Location', 'Vibe', 'Description', 'Start_Time', 'End_Time', 'Key', 'lat', 'lon'
    ])

# Auto-cleanup
now = datetime.now()
st.session_state.sessions = st.session_state.sessions[st.session_state.sessions['End_Time'] > now].reset_index(drop=True)

st.title("✌️ USC Study Buddy")

# --- THE MAP ---
st.subheader("📍 Live Session Map")
if not st.session_state.sessions.empty:
    # This creates the actual interactive map
    st.map(st.session_state.sessions[['lat', 'lon']])
else:
    st.info("No active sessions on the map yet.")

# --- POSTING FORM ---
with st.form("study_form", clear_on_submit=True):
    st.subheader("🚀 Schedule a Session")
    course = st.text_input("Course Code*", placeholder="e.g., BISC 120")
    location = st.text_input("Exact Location*", max_chars=50, placeholder="e.g., Leavey 2nd floor")
    
    col1, col2, col3 = st.columns(3)
    with col1: study_date = st.date_input("Date*", value=datetime.now())
    with col2: start_t = st.time_input("Start*", value=datetime.now())
    with col3: end_t = st.time_input("End*", value=(datetime.now() + timedelta(hours=2)))
    
    v_col, k_col = st.columns(2)
    with v_col: vibe = st.selectbox("Vibe*", options=["Chill", "Cramming", "Group Project"])
    with k_col: user_key = st.text_input("Secret Key*", type="password")
    
    desc = st.text_area("Description", max_chars=100)
    
    if st.form_submit_button("Post to USC Map"):
        if course and location and user_key:
            full_start = datetime.combine(study_date, start_t)
            full_end = datetime.combine(study_date, end_t)
            lat, lon = get_coords(location)
            
            new_row = {
                'Course': course.upper(), 'Location': location, 'Vibe': vibe,
                'Description': desc, 'Start_Time': full_start, 'End_Time': full_end, 
                'Key': user_key, 'lat': lat, 'lon': lon
            }
            st.session_state.sessions = pd.concat([st.session_state.sessions, pd.DataFrame([new_row])], ignore_index=True)
            st.rerun()

# --- ACTIVE SESSIONS LIST ---
st.divider()
for i, row in st.session_state.sessions.iterrows():
    header = f"📖 {row['Course']} @ {row['Location']} ({row['Start_Time'].strftime('%I:%M %p')})"
    with st.expander(header):
        st.write(f"**Vibe:** {row['Vibe']} | **Ends:** {row['End_Time'].strftime('%I:%M %p')}")
        if st.button(f"Join Group", key=f"j_{i}"):
            st.balloons()
