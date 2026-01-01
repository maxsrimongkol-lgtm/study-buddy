import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- USC BRANDING & HIGH-CONTRAST UI ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️", layout="centered")

st.markdown("""
    <style>
    /* Global Reset & Spacing */
    .stApp { background-color: #FFFFFF; color: #000000; }
    .block-container { padding-top: 2rem !important; padding-bottom: 1rem !important; }
    div[data-testid="stForm"] { padding: 1.5rem !important; border: 2px solid #990000 !important; }
    
    /* Headers - USC Cardinal */
    h1, h2, h3 { color: #990000 !important; margin-bottom: 0.5rem !important; }
    
    /* Text Visibility */
    p, label, .stMarkdown { color: #000000 !important; font-weight: 700 !important; margin-bottom: 0px !important; }
    .required { color: #990000; font-size: 16px; }

    /* UNIFIED INPUT BOXES: White Background, Thick Red Border, Black Text */
    input, select, textarea, div[data-baseweb="select"], div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1.5px solid #990000 !important;
        border-radius: 4px !important;
    }

    /* CLEAR & BIG POST BUTTON */
    div.stButton > button:first-child {
        background-color: #990000 !important;
        color: #FFC72C !important;
        height: 3.5em !important;
        width: 100% !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        border: 2px solid #FFC72C !important;
        border-radius: 10px !important;
        transition: 0.3s;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:first-child:hover {
        background-color: #7a0000 !important;
        border-color: #FFFFFF !important;
        transform: scale(1.01);
    }
    
    /* Remove unnecessary spacing between elements */
    .stTextInput, .stSelectbox, .stDateInput, .stTimeInput { margin-bottom: -10px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("✌️ USC Study Buddy")
st.write("Find your squad. Fight On!")
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
with st.form("study_form", clear_on_submit=True):
    st.subheader("🚀 Schedule a Session")
    
    st.markdown("Course Code <span class='required'>*</span>", unsafe_allow_html=True)
    course = st.text_input("c_in", label_visibility="collapsed", placeholder="e.g., MATH 125")
    
    st.markdown("Exact Location (50 char max) <span class='required'>*</span>", unsafe_allow_html=True)
    location = st.text_input("l_in", label_visibility="collapsed", max_chars=50, placeholder="e.g., Leavey 2nd Floor, Table 4")
    
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        st.markdown("Date <span class='required'>*</span>", unsafe_allow_html=True)
        study_date = st.date_input("d_in", label_visibility="collapsed", value=datetime.now())
    with t_col2:
        st.markdown("Start Time <span class='required'>*</span>", unsafe_allow_html=True)
        start_t = st.time_input("s_in", label_visibility="collapsed", value=datetime.now())
    with t_col3:
        st.markdown("End Time <span class='required'>*</span>", unsafe_allow_html=True)
        end_t = st.time_input("e_in", label_visibility="collapsed", value=(datetime.now() + timedelta(hours=2)))
    
    v_col, k_col = st.columns(2)
    with v_col:
        st.markdown("Vibe <span class='required'>*</span>", unsafe_allow_html=True)
        vibe = st.selectbox("v_in", label_visibility="collapsed", options=["Chill", "Cramming", "Group Project"])
    with k_col:
        st.markdown("Secret Key <span class='required'>*</span>", unsafe_allow_html=True)
        user_key = st.text_input("k_in", label_visibility="collapsed", type="password", placeholder="For deletion")
        
    st.markdown("Description (Optional)", unsafe_allow_html=True)
    desc = st.text_area("de_in", label_visibility="collapsed", max_chars=100, placeholder="What are you working on?")
    
    submit = st.form_submit_button("Post to USC Map")
    
    if submit:
        full_start = datetime.combine(study_date, start_t)
        full_end = datetime.combine(study_date, end_t)
        duration = full_end - full_start
        
        if not course or not location or not user_key:
            st.error("Missing required fields.")
        elif full_end <= full_start:
            st.error("Invalid time interval.")
        elif duration > timedelta(hours=5):
            st.error("Maximum limit is 5 hours.")
        else:
            new_row = {
                'Course': course.upper(), 'Location': location, 'Vibe': vibe,
                'Description': desc, 'Start_Time': full_start, 'End_Time': full_end, 'Key': user_key
            }
            st.session_state.sessions = pd.concat([st.session_state.sessions, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Session live until {full_end.strftime('%I:%M %p')}!")
            st.rerun()

# --- ACTIVE SESSIONS ---
st.markdown("### 🤝 Active Sessions")
if st.session_state.sessions.empty:
    st.info("No active sessions. Start one to invite others!")

for i, row in st.session_state.sessions.iterrows():
    header = f"📖 {row['Course']} @ {row['Location']} ({row['Start_Time'].strftime('%I:%M %p')})"
    with st.expander(header):
        st.write(f"**Vibe:** {row['Vibe']} | **Ends:** {row['End_Time'].strftime('%I:%M %p')}")
        if row['Description']: st.write(f"_{row['Description']}_")
        
        c1, c2 = st.columns([3, 1])
        with c1:
            if st.button(f"Join Group", key=f"j_{i}"):
                st.balloons()
                st.success("Fight On! ✌️")
        with c2:
            with st.popover("Delete"):
                check_key = st.text_input("Enter Key", type="password", key=f"dk_{i}")
                if st.button("Confirm", key=f"cd_{i}"):
                    if check_key == row['Key']:
                        st.session_state.sessions = st.session_state.sessions.drop(i)
                        st.rerun()
                    else:
                        st.error("Invalid.")
