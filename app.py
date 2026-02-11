import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- USC BRANDING & TOTAL UI RESET ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️", layout="centered")

# This CSS is designed to override "Dark Mode" at the root level
st.markdown("""
    <style>
    /* 1. Global Reset: Everything white and black */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
    }
    
    /* 2. Unified Input Styling: Force consistency across ALL boxes */
    /* This targets text, date, time, and text-area simultaneously */
    input, div[data-baseweb="input"], div[data-baseweb="base-input"], textarea, .stSelectbox div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #990000 !important;
        border-radius: 4px !important;
        -webkit-text-fill-color: #000000 !important;
        box-shadow: none !important;
    }

    /* Fix labels to be high-contrast black */
    label, p, h3, [data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    /* 3. The Post Button: Vivid Red & Gold */
    /* Center-aligned, high-contrast, no 'dark' shadows */
    .stForm div.stButton {
        display: flex;
        justify-content: center;
    }

    .stForm div.stButton > button {
        background: #990000 !important; /* Cardinal Base */
        color: #FFCC00 !important; /* Gold Text */
        border: 4px solid #FFCC00 !important; /* Gold Border */
        border-radius: 10px !important;
        height: 3.5em !important;
        width: 100% !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        margin-top: 20px;
        opacity: 1 !important;
    }

    /* 4. The Join Button: Clean and Consistent */
    [data-testid="stExpander"] div.stButton > button {
        background-color: #FFFFFF !important;
        color: #990000 !important;
        border: 2px solid #990000 !important;
        border-radius: 5px !important;
        width: auto !important;
        padding: 0px 20px !important;
    }

    /* 5. Hide the dark 'decoration' line at the top */
    [data-testid="stDecoration"] {
        display: none;
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

# --- UI ---
st.title("✌️ USC Study Buddy")
st.write(f"Current Time: **{now.strftime('%I:%M %p')}**")

if not st.session_state.sessions.empty:
    st.map(st.session_state.sessions[['lat', 'lon']])

# --- SCHEDULING FORM ---
with st.form("main_form", clear_on_submit=True):
    st.subheader("🚀 Schedule Session")
    
    col1, col2 = st.columns(2)
    with col1:
        course = st.text_input("Course Code*")
    with col2:
        location = st.text_input("Location (Building Name)*")
    
    st.write("Study Window")
    # Date, Start, and End on one line to keep borders tight and consistent
    d_col, t1_col, t2_col = st.columns([2, 1, 1])
    with d_col:
        study_date = st.date_input("Date")
    with t1_col:
        start_t = st.time_input("Start")
    with t2_col:
        end_t = st.time_input("End", value=(now + timedelta(hours=2)).time())

    vibe = st.text_input("Vibe (e.g., Silent Grinding)*")
    user_key = st.text_input("Secret Key*", type="password")
    desc = st.text_area("Description (Optional)")

    if st.form_submit_button("Post to USC Map"):
        if course and location and vibe and user_key:
            fs, fe = datetime.combine(study_date, start_t), datetime.combine(study_date, end_t)
            if fe > fs:
                lat, lon = get_coords(location)
                new_row = pd.DataFrame([{'Course': course.upper(), 'Location': location, 'Vibe': vibe, 'Description': desc, 'Start_Time': fs, 'End_Time': fe, 'Key': user_key, 'Joins': 0, 'lat': lat, 'lon': lon}])
                st.session_state.sessions = pd.concat([st.session_state.sessions, new_row], ignore_index=True)
                st.rerun()

# --- ACTIVE FEED ---
st.write("---")
st.subheader("🤝 Active Sessions")
for i, row in st.session_state.sessions.iterrows():
    with st.expander(f"📖 {row['Course']} @ {row['Location']} ({row['Start_Time'].strftime('%I:%M %p')} - {row['End_Time'].strftime('%I:%M %p')})"):
        st.write(f"**Vibe:** {row['Vibe']}")
        if st.button(f"Join Group ({row['Joins']} attending)", key=f"j_{i}"):
            st.session_state.sessions.at[i, 'Joins'] += 1
            st.balloons()
            st.rerun()
            
