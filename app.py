import streamlit as st
import pandas as pd
from datetime import datetime

# --- USC BRANDING & UI OVERHAUL ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️", layout="centered")

st.markdown("""
    <style>
    /* 1. GLOBAL LIGHT MODE & TEXT */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
    }
    
    label, p, h1, h2, h3 {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* 2. UNIFIED BORDERS FOR ALL INPUTS */
    /* Targeting text inputs, text areas, and data-baseweb wrappers */
    input, div[data-baseweb="input"], textarea {
        background-color: #FFFFFF !important;
        border: 2px solid #990000 !important;
        border-radius: 8px !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* 3. ULTRA-VISIBLE POST BUTTON */
    div.stButton > button[kind="primaryFormSubmit"] {
        background: linear-gradient(135deg, #990000 0%, #FFCC00 100%) !important;
        color: #FFFFFF !important;
        border: 2px solid #FFCC00 !important;
        border-radius: 12px !important;
        width: 100% !important;
        height: 4.5em !important;
        font-size: 26px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        box-shadow: 0px 8px 20px rgba(153, 0, 0, 0.4) !important; /* Makes it "pop" */
        margin-top: 30px !important;
        cursor: pointer;
    }

    div.stButton > button[kind="primaryFormSubmit"]:hover {
        transform: translateY(-2px);
        box-shadow: 0px 12px 25px rgba(153, 0, 0, 0.5) !important;
    }

    /* 4. CLEAN EXPANDERS */
    [data-testid="stExpander"] {
        border: 1px solid #990000 !important;
        background-color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC ---
CAMPUS_COORDS = {
    "leavey": [34.0217, -118.2828], "doheny": [34.0202, -118.2837],
    "village": [34.0250, -118.2851], "tutor": [34.0200, -118.2850]
}

def get_coords(loc_text):
    text = loc_text.lower()
    for key, coords in CAMPUS_COORDS.items():
        if key in text: return coords[0], coords[1]
    return 34.0205, -118.2856

if 'sessions' not in st.session_state:
    st.session_state.sessions = pd.DataFrame(columns=['Course', 'Location', 'Vibe', 'Description', 'Start_Time', 'End_Time', 'Key', 'Joins', 'lat', 'lon'])

now = datetime.now()
st.session_state.sessions = st.session_state.sessions[st.session_state.sessions['End_Time'] > now].reset_index(drop=True)

# --- UI ---
st.title("✌️ USC Study Buddy")

if not st.session_state.sessions.empty:
    st.map(st.session_state.sessions[['lat', 'lon']])

with st.form("main_form", clear_on_submit=True):
    st.subheader("🚀 Schedule Session")
    
    col1, col2 = st.columns(2)
    with col1: course = st.text_input("Course Code*")
    with col2: location = st.text_input("Location (Building)*")
    
    st.write("**Study Window**")
    d_col, t1_col, t2_col = st.columns([2, 1, 1])
    with d_col: 
        study_date = st.date_input("Date")
    with t1_col: 
        # CHANGED TO TEXT INPUT
        start_str = st.text_input("Start (00:00 AM/PM)")
    with t2_col: 
        # CHANGED TO TEXT INPUT
        end_str = st.text_input("End (00:00 AM/PM)")

    vibe = st.text_input("Vibe (e.g. Grinding, Quiet)*")
    user_key = st.text_input("Secret Key*", type="password")
    desc = st.text_area("Description (Optional)")

    if st.form_submit_button("Post to USC Map"):
        if course and location and vibe and user_key and start_str and end_str:
            try:
                # Convert text input to actual time objects
                start_t = datetime.strptime(start_str.strip(), "%I:%M %p").time()
                end_t = datetime.strptime(end_str.strip(), "%I:%M %p").time()
                
                fs = datetime.combine(study_date, start_t)
                fe = datetime.combine(study_date, end_t)
                
                if fe > fs:
                    lat, lon = get_coords(location)
                    new_row = pd.DataFrame([{'Course': course.upper(), 'Location': location, 'Vibe': vibe, 'Description': desc, 'Start_Time': fs, 'End_Time': fe, 'Key': user_key, 'Joins': 0, 'lat': lat, 'lon': lon}])
                    st.session_state.sessions = pd.concat([st.session_state.sessions, new_row], ignore_index=True)
                    st.rerun()
                else:
                    st.error("End time must be after start time!")
            except ValueError:
                st.error("Please use the format: 02:30 PM")

# --- FEED ---
st.subheader("🤝 Join a Session")
for i, row in st.session_state.sessions.iterrows():
    s_display = row['Start_Time'].strftime('%I:%M %p')
    e_display = row['End_Time'].strftime('%I:%M %p')
    with st.expander(f"📖 {row['Course']} @ {row['Location']} ({s_display} - {e_display})"):
        st.write(f"**Vibe:** {row['Vibe']}")
        if st.button(f"Join Group ({row['Joins']} attending)", key=f"j_{i}"):
            st.session_state.sessions.at[i, 'Joins'] += 1
            st.balloons()
            st.rerun()
