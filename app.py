import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- USC BRANDING & UI ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1A1A1A; }
    h1, h2, h3 { color: #990000 !important; font-family: 'Helvetica Neue', sans-serif; }
    
    /* Make labels bold and visible */
    p, label, .stMarkdown { color: #262626 !important; font-weight: 700 !important; }

    /* BIG RED POST BUTTON */
    div.stButton > button:first-child {
        background-color: #990000 !important;
        color: #FFC72C !important;
        height: 4em !important;
        width: 100% !important;
        font-size: 24px !important;
        font-weight: bold !important;
        border: 3px solid #FFC72C !important;
        border-radius: 15px !important;
        text-transform: uppercase;
        margin-top: 20px;
    }
    
    /* Secondary buttons (Join/Delete) */
    .stButton>button { 
        background-color: #f0f0f0; 
        color: #990000; 
        border-radius: 8px; 
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✌️ USC Study Buddy")
st.write("Find your squad. Fight On!")

# --- DATA INITIALIZATION ---
if 'sessions' not in st.session_state:
    st.session_state.sessions = pd.DataFrame(columns=[
        'Course', 'Location', 'Vibe', 'Description', 'Start_Time', 'End_Time', 'Key'
    ])

# Auto-cleanup expired sessions
now = datetime.now()
st.session_state.sessions = st.session_state.sessions[st.session_state.sessions['End_Time'] > now]

# --- POST A SESSION ---
st.subheader("🚀 Schedule a Session")

with st.form("study_form", clear_on_submit=True):
    course = st.text_input("Course Code (Required)*", placeholder="e.g., BUAD 304")
    
    # 50-Character Location Text Box
    location = st.text_input("Exact Location (Required)*", max_chars=50, placeholder="e.g., Leavey 2nd Floor, Back Left Table")
    
    # Precision Timing Section
    st.write("---")
    date_col, start_col, end_col = st.columns(3)
    with date_col:
        study_date = st.date_input("Date", value=datetime.now())
    with start_col:
        start_t = st.time_input("Start Time", value=datetime.now())
    with end_col:
        # Default end time to 2 hours from now
        end_t = st.time_input("End Time", value=(datetime.now() + timedelta(hours=2)))
    
    st.write("---")
    col_a, col_b = st.columns(2)
    with col_a:
        vibe = st.selectbox("Vibe", ["Chill", "Cramming", "Group Project"])
    with col_b:
        user_key = st.text_input("Secret Key (to delete later)*", type="password")
        
    desc = st.text_area("Description (Max 100 chars)", max_chars=100)
    
    # Logic Checks on Submission
    submit = st.form_submit_button("Post Session")
    
    if submit:
        # Create full datetime objects
        full_start = datetime.combine(study_date, start_t)
        full_end = datetime.combine(study_date, end_t)
        duration = full_end - full_start
        
        if not course or not location or not user_key:
            st.error("Please fill in all required fields (*).")
        elif full_end <= full_start:
            st.error("End time must be after start time!")
        elif duration > timedelta(hours=5):
            st.error("❌ Session limit exceeded! USC rules: Maximum 5 hours per session.")
        else:
            new_row = {
                'Course': course.upper(), 'Location': location, 'Vibe': vibe,
                'Description': desc, 'Start_Time': full_start, 'End_Time': full_end, 'Key': user_key
            }
            st.session_state.sessions = pd.concat([st.session_state.sessions, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Success! Session live until {full_end.strftime('%I:%M %p')}")
            st.rerun()

# --- ACTIVE SESSIONS ---
st.divider()
st.subheader("🤝 Active Sessions")

if st.session_state.sessions.empty:
    st.info("No active sessions. Start one to get the party started!")

for i, row in st.session_state.sessions.iterrows():
    with st.expander(f"📖 {row['Course']} at {row['Location']}"):
        st.write(f"**Schedule:** {row['Start_Time'].strftime('%I:%M %p')} - {row['End_Time'].strftime('%I:%M %p')}")
        st.write(f"**Vibe:** {row['Vibe']}")
        if row['Description']: st.write(f"_{row['Description']}_")
        
        c1, c2 = st.columns([3, 1])
        with c1:
            if st.button(f"Join {row['Course']}", key=f"join_{i}"):
                st.balloons()
                st.success("Joined! See you there.")
        with c2:
            with st.popover("Delete"):
                check_key = st.text_input("Key", type="password", key=f"del_key_{i}")
                if st.button("Confirm", key=f"conf_del_{i}"):
                    if check_key == row['Key']:
                        st.session_state.sessions = st.session_state.sessions.drop(i)
                        st.rerun()
                    else:
                        st.error("Wrong key!")
