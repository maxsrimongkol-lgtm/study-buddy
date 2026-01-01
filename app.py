import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- USC BRANDING & UI ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1A1A1A; }
    h1, h2, h3 { color: #990000 !important; font-family: 'Helvetica Neue', sans-serif; }
    p, label { color: #262626 !important; font-weight: 600; }
    .stButton>button { 
        background-color: #990000; 
        color: #FFC72C !important; 
        border-radius: 8px; 
        border: 2px solid #FFC72C;
        font-weight: bold;
    }
    .delete-btn>button {
        background-color: #f0f0f0;
        color: #990000 !important;
        border: 1px solid #990000;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✌️ USC Study Buddy")
st.write("Find your squad. Fight On!")

# --- LOCATION DATABASE ---
LOCATIONS = {
    "Leavey Library (LVL)": {"lat": 34.0217, "lon": -118.2828},
    "Doheny Library (DML)": {"lat": 34.0202, "lon": -118.2837},
    "Fertitta Hall (JFF)": {"lat": 34.0187, "lon": -118.2823},
    "USC Village": {"lat": 34.0250, "lon": -118.2851},
    "Annenberg Hall (ANN)": {"lat": 34.0210, "lon": -118.2863},
    "Tutor Campus Center (TCC)": {"lat": 34.0200, "lon": -118.2850}
}

# --- DATA INITIALIZATION ---
if 'sessions' not in st.session_state:
    st.session_state.sessions = pd.DataFrame(columns=[
        'Course', 'Location', 'Vibe', 'Description', 'End_Time', 'Key', 'lat', 'lon'
    ])

# Auto-cleanup expired sessions
now = datetime.now()
st.session_state.sessions = st.session_state.sessions[st.session_state.sessions['End_Time'] > now]

# --- MAP VIEW ---
st.subheader("📍 Live Campus Map")
if not st.session_state.sessions.empty:
    st.map(st.session_state.sessions[['lat', 'lon']])
else:
    st.info("No active sessions. Be the first to post!")

# --- POST A SESSION ---
st.divider()
st.subheader("🚀 Schedule a Session")

with st.form("study_form", clear_on_submit=True):
    course = st.text_input("Course Code (Required)", placeholder="e.g., WRIT 150")
    loc_name = st.selectbox("Location", list(LOCATIONS.keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        duration = st.select_slider("Length (Max 5 Hours)", options=[1, 2, 3, 4, 5], value=2)
    with col2:
        # The Secret Key Input
        user_key = st.text_input("Create a Secret Key (to delete later)", type="password", help="Use a simple PIN or word.")
        
    vibe = st.selectbox("Vibe", ["Chill", "Cramming", "Group Project"])
    desc = st.text_area("Description (Max 100 chars)", max_chars=100)
    
    if st.form_submit_button("Post to Map"):
        if course and user_key:
            end_time = datetime.now() + timedelta(hours=duration)
            new_row = {
                'Course': course.upper(), 'Location': loc_name, 'Vibe': vibe,
                'Description': desc, 'End_Time': end_time, 'Key': user_key,
                'lat': LOCATIONS[loc_name]['lat'], 'lon': LOCATIONS[loc_name]['lon']
            }
            st.session_state.sessions = pd.concat([st.session_state.sessions, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Posted! Active until {end_time.strftime('%I:%M %p')}")
            st.rerun()
        else:
            st.error("Course and Secret Key are required!")

# --- ACTIVE SESSIONS & DELETE LOGIC ---
st.divider()
st.subheader("🤝 Active Sessions")

for i, row in st.session_state.sessions.iterrows():
    with st.expander(f"📖 {row['Course']} at {row['Location']}"):
        st.write(f"**Ends at:** {row['End_Time'].strftime('%I:%M %p')} | **Vibe:** {row['Vibe']}")
        if row['Description']: st.write(f"_{row['Description']}_")
        
        col_j, col_d = st.columns([3, 1])
        with col_j:
            if st.button(f"Join {row['Course']}", key=f"join_{i}"):
                st.balloons()
                st.success("Joined! See you there.")
        
        with col_d:
            # Delete logic using the Key
            with st.popover("Delete"):
                check_key = st.text_input("Enter Secret Key to delete", type="password", key=f"del_key_{i}")
                if st.button("Confirm Delete", key=f"conf_del_{i}"):
                    if check_key == row['Key']:
                        st.session_state.sessions = st.session_state.sessions.drop(i)
                        st.rerun()
                    else:
                        st.error("Wrong key!")
