import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- USC BRANDING & TOTAL UI UNIFICATION ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️", layout="centered")

# UNIVERSAL CSS: Forcing every element to be a simple red box
st.markdown("""
    <style>
    /* 1. Global Page Reset */
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, label { color: #000000 !important; font-weight: 800 !important; }

    /* 2. UNIVERSAL BOX STYLE: Simple white box, 2px red border */
    /* This overrides the different styles for text, date, and time containers */
    div[data-baseweb="input"], 
    div[data-baseweb="select"], 
    div[data-baseweb="base-input"],
    input, select, textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #990000 !important;
        border-radius: 0px !important;
        -webkit-text-fill-color: #000000 !important;
        box-shadow: none !important;
    }

    /* 3. POST BUTTON: Cardinal Red Box, White Text (High Contrast) */
    div.stButton > button:first-child {
        background-color: #990000 !important;
        color: #FFFFFF !important;
        height: 3.5em !important;
        width: 100% !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        border: none !important;
        border-radius: 4px !important;
        text-transform: uppercase;
        margin-top: 15px;
    }
    
    /* Hover effect */
    div.stButton > button:first-child:hover {
        background-color: #7a0000 !important;
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
    return 34.0205, -118.2856 # Default: Tommy Trojan

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
    st.info("No active sessions on the map yet.")

# --- FORM SECTION ---
with st.form("main_form", clear_on_submit=True):
    st.subheader("🚀 Post a Session")
    
    st.markdown("Course Code *")
    course = st.text_input("c", label_visibility="collapsed", placeholder="e.g., CSCI 104")
    
    st.markdown("Location (e.g., Leavey, Village) *")
    location = st.text_input("l", label_visibility="collapsed", placeholder="e.g., Leavey 2nd Floor")
    
    # REQUIRED LAYOUT: Date, Start, and End on one line
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("Date *")
        study_date = st.date_input("d", label_visibility="collapsed")
    with col2:
        st.markdown("Start Time *")
        start_t = st.time_input("s", label_visibility="collapsed")
    with col3:
        st.markdown("End Time *")
        end_t = st.time_input("e", label_visibility="collapsed", value=(now + timedelta(hours=2)))

    v_col, k_col = st.columns(2)
    with v_col:
        st.markdown("Vibe *")
        vibe = st.selectbox("v", options=["Chill", "Cramming", "Group Project"], label_visibility="collapsed")
    with k_col:
        st.markdown("Secret Key *")
        user_key = st.text_input("k", type="password", label_visibility="collapsed", placeholder="Required for deletion")

    st.markdown("Description (Optional)")
    desc = st.text_area("de", label_visibility="collapsed")

    if st.form_submit_button("Post to USC Map"):
        if course and location and user_key:
            fs, fe = datetime.combine(study_date, start_t), datetime.combine(study_date, end_t)
            if fe > fs:
                lat, lon = get_coords(location)
                new_row = {
                    'Course': course.upper(), 'Location': location, 'Vibe': vibe, 'Description': desc, 
                    'Start_Time': fs, 'End_Time': fe, 'Key': user_key, 'Joins': 0, 'lat': lat, 'lon': lon
                }
                st.session_state.sessions = pd.concat([st.session_state.sessions, pd.DataFrame([new_row])], ignore_index=True)
                st.rerun()

# --- ACTIVE SESSIONS ---
st.write("---")
st.subheader("🤝 Active Sessions")

for i, row in st.session_state.sessions.iterrows():
    s_pm = row['Start_Time'].strftime('%I:%M %p')
    e_pm = row['End_Time'].strftime('%I:%M %p')
    
    with st.expander(f"📖 {row['Course']} @ {row['Location']} (Starts {s_pm})"):
        st.write(f"**Vibe:** {row['Vibe']} | **Ends:** {e_pm}")
        if row['Description']: st.write(f"_{row['Description']}_")
        
        # JOIN BUTTON WITH COUNTER
        join_label = f"Join Group ({row['Joins']} attending)"
        c_join, c_del = st.columns([3, 1])
        with c_join:
            if st.button(join_label, key=f"join_{i}"):
                st.session_state.sessions.at[i, 'Joins'] += 1
                st.balloons()
                st.rerun()
        with c_del:
            if st.button("Delete", key=f"del_{i}"):
                # Key check popover could be added here
                st.session_state.sessions = st.session_state.sessions.drop(i)
                st.rerun()
