import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- USC BRANDING & GLOBAL LIGHT-MODE RESET ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️", layout="centered")

st.markdown("""
    <style>
    /* 1. FORCE GLOBAL LIGHT MODE */
    /* This targets the main app container and every sub-container */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: #FFFFFF !important;
    }
    
    /* 2. FORCE BLACK TEXT EVERYWHERE */
    h1, h2, h3, p, label, span, li, div {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* 3. INPUT BOXES: White with 2px Red Border */
    div[data-baseweb="input"], 
    div[data-baseweb="select"], 
    div[data-baseweb="base-input"],
    textarea, input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #990000 !important;
        border-radius: 4px !important;
        -webkit-text-fill-color: #000000 !important;
    }
    
    /* Fix for date/time picker dropdown icons and text */
    div[data-baseweb="calendar"] { background-color: #FFFFFF !important; }
    
    /* 4. THE BIG CENTERED RED & GOLD BUTTON */
    .stForm div.stButton {
        display: flex;
        justify-content: center;
    }

    .stForm div.stButton > button {
        background: linear-gradient(90deg, #990000 0%, #FFCC00 100%) !important;
        color: #FFFFFF !important;
        border: 2px solid #FFCC00 !important;
        border-radius: 12px !important;
        height: 4em !important;
        width: 80% !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1) !important;
        margin-top: 20px;
    }

    /* 5. JOIN BUTTONS: Light Grey/White to prevent "Dark Parts" */
    [data-testid="stExpander"] div.stButton > button {
        background-color: #f8f9fa !important;
        color: #990000 !important;
        border: 1px solid #990000 !important;
    }
    
    /* Remove any dark hover states */
    button:hover {
        opacity: 0.8 !important;
        color: #990000 !important;
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

# --- DATA INITIALIZATION ---
if 'sessions' not in st.session_state:
    st.session_state.sessions = pd.DataFrame(columns=[
        'Course', 'Location', 'Vibe', 'Description', 'Start_Time', 'End_Time', 'Key', 'Joins', 'lat', 'lon'
    ])

now = datetime.now()
st.session_state.sessions = st.session_state.sessions[st.session_state.sessions['End_Time'] > now].reset_index(drop=True)

# --- APP UI ---
st.title("✌️ USC Study Buddy")
st.write(f"Current Time: **{now.strftime('%I:%M %p')}**")

# --- MAP SECTION ---
st.subheader("📍 Live Campus Map")
if not st.session_state.sessions.empty:
    st.map(st.session_state.sessions[['lat', 'lon']])
else:
    st.info("No active sessions on the map.")

# --- FORM SECTION ---
with st.form("main_form", clear_on_submit=True):
    st.subheader("🚀 Schedule Session")
    
    col_a, col_b = st.columns(2)
    with col_a:
        course = st.text_input("Course Code*")
    with col_b:
        location = st.text_input("Location*")
    
    st.markdown("**Study Date & Time Range***")
    date_col, t1_col, t2_col = st.columns([2, 1, 1])
    with date_col:
        study_date = st.date_input("Select Date", label_visibility="collapsed")
    with t1_col:
        start_t = st.time_input("Start", value=now.time(), label_visibility="collapsed")
    with t2_col:
        end_t = st.time_input("End", value=(now + timedelta(hours=2)).time(), label_visibility="collapsed")

    vibe = st.text_input("Vibe (e.g., Silent Cramming, Collaborative)*")
    user_key = st.text_input("Secret Key (to delete later)*", type="password")
    desc = st.text_area("Description (Optional)")

    submit = st.form_submit_button("Post to USC Map")
    
    if submit:
        if course and location and vibe and user_key:
            fs = datetime.combine(study_date, start_t)
            fe = datetime.combine(study_date, end_t)
            if fe > fs:
                lat, lon = get_coords(location)
                new_row = {
                    'Course': course.upper(), 'Location': location, 'Vibe': vibe, 
                    'Description': desc, 'Start_Time': fs, 'End_Time': fe, 
                    'Key': user_key, 'Joins': 0, 'lat': lat, 'lon': lon
                }
                st.session_state.sessions = pd.concat([st.session_state.sessions, pd.DataFrame([new_row])], ignore_index=True)
                st.rerun()

# --- ACTIVE SESSIONS ---
st.write("---")
st.subheader("🤝 Active Sessions")

for i, row in st.session_state.sessions.iterrows():
    s_str = row['Start_Time'].strftime('%I:%M %p')
    e_str = row['End_Time'].strftime('%I:%M %p')
    
    with st.expander(f"📖 {row['Course']} @ {row['Location']} ({s_str} - {e_str})"):
        st.write(f"**Vibe:** {row['Vibe']}")
        if row['Description']: st.write(f"_{row['Description']}_")
        
        join_label = f"Join Group ({row['Joins']} attending)"
        if st.button(join_label, key=f"join_{i}"):
            st.session_state.sessions.at[i, 'Joins'] += 1
            st.balloons()
            st.rerun()
