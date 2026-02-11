import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- USC BRANDING & UI UNIFICATION ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️", layout="centered")

# UNIVERSAL CSS: Fixing button contrast and box styling
st.markdown("""
    <style>
    /* 1. Page Background & Text */
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, label { color: #000000 !important; font-weight: 800 !important; }
    
    /* Ensure input labels are visible and black */
    .stMarkdown p, .stSelectbox label, .stTextInput label, .stDateInput label, .stTimeInput label {
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* 2. UNIVERSAL BOX STYLE: White background, 2px Cardinal Red border */
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

    /* 3. MAIN POST BUTTON: High Contrast (Cardinal Red + White Text) */
    div.stButton > button[kind="primary"], .stForm div.stButton > button {
        background-color: #990000 !important;
        color: #FFFFFF !important;
        border: 2px solid #990000 !important;
        border-radius: 8px !important;
        height: 3.5em !important;
        width: 100% !important;
        font-size: 18px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        display: block;
        opacity: 1 !important;
    }
    
    /* 4. JOIN BUTTONS: Secondary Style (White background + Dark Text) */
    div.stButton > button {
        background-color: #f0f2f6;
        color: #31333F;
        border: 1px solid #d3d3d3;
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
    st.subheader("🚀 Post a Session")
    
    course = st.text_input("Course Code (e.g., BUAD 304)*")
    location = st.text_input("Location (e.g., Fertitta Hall)*")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        study_date = st.date_input("Date*")
    with col2:
        # Time input widgets default to system format, but display logic below uses AM/PM
        start_t = st.time_input("Start Time*")
    with col3:
        end_t = st.time_input("End Time*", value=(now + timedelta(hours=2)))

    v_col, k_col = st.columns(2)
    with v_col:
        vibe = st.selectbox("Vibe*", options=["Chill", "Cramming", "Group Project"])
    with k_col:
        user_key = st.text_input("Secret Key (to delete later)*", type="password")

    desc = st.text_area("Description (Optional)")

    # The Submit Button
    submit = st.form_submit_button("Post to USC Map")
    if submit:
        if course and location and user_key:
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
    # TIME FORMATTING: Forcing 1-12 AM/PM Format
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