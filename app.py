import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- USC BRANDING & UI ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️")

# Custom CSS for USC Cardinal and Gold
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .stButton>button { 
        background-color: #990000; 
        color: #FFC72C; 
        border-radius: 20px; 
        font-weight: bold;
        border: 2px solid #FFC72C;
    }
    h1, h2, h3 { color: #990000; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("✌️ USC Study Buddy")
st.write("Find your squad. No login, no limits. Fight On!")

# --- LOCATION DATABASE ---
LOCATIONS = {
    "Leavey Library (LVL)": {"lat": 34.0217, "lon": -118.2828},
    "Doheny Library (DML)": {"lat": 34.0202, "lon": -118.2837},
    "Fertitta Hall (JFF)": {"lat": 34.0187, "lon": -118.2823},
    "USC Village": {"lat": 34.0250, "lon": -118.2851},
    "Annenberg Hall (ANN)": {"lat": 34.0210, "lon": -118.2863},
    "Tutor Campus Center (TCC)": {"lat": 34.0200, "lon": -118.2850},
    "Other / Outdoor": {"lat": 34.0224, "lon": -118.2851}
}

# --- DATA HANDLING ---
# For this MVP, we use 'st.session_state' to simulate the database
# In Step 6, we can connect this to your Google Sheet
if 'sessions' not in st.session_state:
    st.session_state.sessions = pd.DataFrame(columns=[
        'Course', 'Location', 'Vibe', 'Description', 'End_Time', 'lat', 'lon'
    ])

# Auto-delete expired sessions
now = datetime.now()
st.session_state.sessions = st.session_state.sessions[st.session_state.sessions['End_Time'] > now]

# --- MAP VIEW ---
st.subheader("📍 Live Map")
if not st.session_state.sessions.empty:
    st.map(st.session_state.sessions)
else:
    st.info("No active sessions right now. Start one below!")

# --- POST A SESSION ---
st.divider()
st.subheader("🚀 Post a Session")

with st.form("study_form", clear_on_submit=True):
    course = st.text_input("Course Code*", placeholder="e.g., CSCI 103")
    loc_name = st.selectbox("Select USC Location*", list(LOCATIONS.keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        duration = st.number_input("Duration (Max 5 Hours)*", min_value=0.5, max_value=5.0, value=2.0, step=0.5)
    with col2:
        vibe = st.selectbox("Vibe", ["Chill", "Cramming", "Deep Work"])
    
    details = st.text_area("Description (Max 100 chars)", max_chars=100)
    
    if st.form_submit_button("Post to Map"):
        if course:
            new_session = {
                'Course': course.upper(),
                'Location': loc_name,
                'Vibe': vibe,
                'Description': details,
                'End_Time': datetime.now() + timedelta(hours=duration),
                'lat': LOCATIONS[loc_name]['lat'],
                'lon': LOCATIONS[loc_name]['lon']
            }
            st.session_state.sessions = pd.concat([st.session_state.sessions, pd.DataFrame([new_session])], ignore_index=True)
            st.success("Session posted! ✌️")
            st.rerun()
        else:
            st.error("Course Code is required!")

# --- ACTIVE LIST & JOIN ---
st.divider()
st.subheader("🤝 Active Sessions")

for i, row in st.session_state.sessions.iterrows():
    with st.expander(f"📖 {row['Course']} at {row['Location']}"):
        st.write(f"**Vibe:** {row['Vibe']}")
        st.write(f"**Ends at:** {row['End_Time'].strftime('%I:%M %p')}")
        if row['Description']:
            st.write(f"_{row['Description']}_")
        
        if st.button(f"Join {row['Course']} Group", key=f"join_{i}"):
            st.balloons()
            st.success(f"Awesome! Head to {row['Location']} and look for the group!")
    
