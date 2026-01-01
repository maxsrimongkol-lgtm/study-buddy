import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- USC BRANDING & HIGH-CONTRAST UI ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️")

st.markdown("""
    <style>
    /* Main Background and Text */
    .stApp { background-color: #FFFFFF; color: #000000; }
    
    /* Headers - USC Cardinal */
    h1, h2, h3 { color: #990000 !important; font-family: 'Helvetica Neue', Arial, sans-serif; }
    
    /* Labels and Body Text - High Contrast Black */
    p, label, .stMarkdown { color: #000000 !important; font-weight: 700 !important; }
    
    /* Required Asterisk Style */
    .required { color: #990000; font-size: 18px; }

    /* Input Boxes - Ensure white background and black text */
    input, select, textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #990000 !important;
    }

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
    
    /* Expander styling for visibility */
    .streamlit-expanderHeader {
        background-color: #f8f9fa !important;
        color: #990000 !important;
        border: 1px solid #dee2e6 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✌️ USC Study Buddy")
st.write("Find your squad. Fight On!")
st.markdown("---")
st.markdown("<span class='required'>*</span> = Required field", unsafe_allow_html=True)

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
    # Required Fields with Asterisks
    st.markdown("Course Code <span class='required'>*</span>", unsafe_allow_html=True)
    course = st.text_input("course_input", label_visibility="collapsed", placeholder="e.g., WRIT 150")
    
    st.markdown("Exact Location (50 char max) <span class='required'>*</span>", unsafe_allow_html=True)
    location = st.text_input("loc_input", label_visibility="collapsed", max_chars=50, placeholder="e.g., Leavey 3rd floor, back corner")
    
    # Precision Timing Section
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        st.markdown("Date <span class='required'>*</span>", unsafe_allow_html=True)
        study_date = st.date_input("date_input", label_visibility="collapsed", value=datetime.now())
    with t_col2:
        st.markdown("Start Time <span class='required'>*</span>", unsafe_allow_html=True)
        # AM/PM is handled by the browser's native time picker in Streamlit
        start_t = st.time_input("start_input", label_visibility="collapsed", value=datetime.now())
    with t_col3:
        st.markdown("End Time <span class='required'>*</span>", unsafe_allow_html=True)
        end_t = st.time_input("end_input", label_visibility="collapsed", value=(datetime.now() + timedelta(hours=2)))
    
    v_col, k_col = st.columns(2)
    with v_col:
        st.markdown("Vibe <span class='required'>*</span>", unsafe_allow_html=True)
        vibe = st.selectbox("vibe_input", label_visibility="collapsed", options=["Chill", "Cramming", "Group Project"])
    with k_col:
        st.markdown("Secret Key <span class='required'>*</span>", unsafe_allow_html=True)
        user_key = st.text_input("key_input", label_visibility="collapsed", type="password", placeholder="To delete later")
        
    st.markdown("Description (Optional)", unsafe_allow_html=True)
    desc = st.text_area("desc_input", label_visibility="collapsed", max_chars=100, placeholder="What are you working on?")
    
    # Logic Checks on Submission
    submit = st.form_submit_button("Post Session")
    
    if submit:
        full_start = datetime.combine(study_date, start_t)
        full_end = datetime.combine(study_date, end_t)
        duration = full_end - full_start
        
        if not course or not location or not user_key:
            st.error("Please fill in all required fields marked with *")
        elif full_end <= full_start:
            st.error("End time must be after start time!")
        elif duration > timedelta(hours=5):
            st.error("❌ Session limit exceeded! Maximum allowed is 5 hours.")
        else:
            new_row = {
                'Course': course.upper(), 'Location': location, 'Vibe': vibe,
                'Description': desc, 'Start_Time': full_start, 'End_Time': full_end, 'Key': user_key
            }
            st.session_state.sessions = pd.concat([st.session_state.sessions, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Success! Posted until {full_end.strftime('%I:%M %p')}")
            st.rerun()

# --- ACTIVE SESSIONS ---
st.divider()
st.subheader("🤝 Active Sessions")

if st.session_state.sessions.empty:
    st.info("No active sessions currently. Be the first to post!")

for i, row in st.session_state.sessions.iterrows():
    # Expander uses AM/PM formatting for display
    header_text = f"📖 {row['Course']} | {row['Location']} ({row['Start_Time'].strftime('%I:%M %p')})"
    with st.expander(header_text):
        st.write(f"**Exact Time:** {row['Start_Time'].strftime('%I:%M %p')} to {row['End_Time'].strftime('%I:%M %p')}")
        st.write(f"**Vibe:** {row['Vibe']}")
        if row['Description']: st.write(f"_{row['Description']}_")
        
        c1, c2 = st.columns([3, 1])
        with c1:
            if st.button(f"Join Group", key=f"join_{i}"):
                st.balloons()
                st.success("You're in! Fight On!")
        with c2:
            with st.popover("Delete"):
                check_key = st.text_input("Enter Key", type="password", key=f"del_key_{i}")
                if st.button("Confirm", key=f"conf_del_{i}"):
                    if check_key == row['Key']:
                        st.session_state.sessions = st.session_state.sessions.drop(i)
                        st.rerun()
                    else:
                        st.error("Incorrect key.")
