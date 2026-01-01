import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- USC BRANDING & MAXIMUM CONTRAST UI ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    p, label, span, .stMarkdown, .stText { 
        color: #000000 !important; 
        font-weight: 800 !important; 
    }
    input, select, textarea, [data-baseweb="select"], [data-baseweb="input"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2.5px solid #990000 !important;
        border-radius: 8px !important;
    }
    div.stButton > button:first-child {
        background-color: #CC0000 !important;
        color: #FFC72C !important;
        height: 4em !important;
        width: 100% !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        border: 3px solid #FFC72C !important;
        border-radius: 15px !important;
    }
    .required { color: #CC0000 !important; font-size: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- COORDINATE LOGIC ---
CAMPUS_COORDS = {
    "leavey": [34.0217, -118.2828], "doheny": [34.0202, -118.2837],
    "fertitta": [34.0187, -118.2823], "village": [34.0250, -118.2851],
    "annenberg": [34.0210, -118.2863], "tutor": [34.0200, -118.2850]
}

def get_coords(loc_text):
    text = loc_text.lower()
    for key, coords in CAMPUS_COORDS.items():
        if key in text: return coords[0], coords[1]
    return 34.0205, -118.2856

# --- DATA STORAGE ---
if 'sessions' not in st.session_state:
    st.session_state.sessions = pd.DataFrame(columns=['Course', 'Location', 'Vibe', 'Description', 'Start_Time', 'End_Time', 'Key', 'lat', 'lon'])

now = datetime.now()
st.session_state.sessions = st.session_state.sessions[st.session_state.sessions['End_Time'] > now].reset_index(drop=True)

# --- UI CONTENT ---
st.title("✌️ USC Study Buddy")
# FIX: Current Time in AM/PM
st.write(f"Current Time: {now.strftime('%I:%M %p')}")
st.markdown("<span class='required'>*</span> = Required field", unsafe_allow_html=True)

# --- MAP SECTION ---
st.subheader("📍 Live Map")
if not st.session_state.sessions.empty:
    st.map(st.session_state.sessions[['lat', 'lon']])

# --- FORM SECTION ---
with st.form("main_form", clear_on_submit=True):
    st.subheader("🚀 Schedule a Session")
    
    st.markdown("Course Code <span class='required'>*</span>", unsafe_allow_html=True)
    course = st.text_input("c", label_visibility="collapsed", placeholder="e.g. CSCI 170")
    
    st.markdown("Location (e.g. Leavey, Village) <span class='required'>*</span>", unsafe_allow_html=True)
    location = st.text_input("l", label_visibility="collapsed", max_chars=50)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("Date <span class='required'>*</span>", unsafe_allow_html=True)
        study_date = st.date_input("d", label_visibility="collapsed")
    with c2:
        st.markdown("Start Time <span class='required'>*</span>", unsafe_allow_html=True)
        start_t = st.time_input("s", label_visibility="collapsed")
    with c3:
        st.markdown("End Time <span class='required'>*</span>", unsafe_allow_html=True)
        end_t = st.time_input("e", label_visibility="collapsed", value=(now + timedelta(hours=2)))

    v_col, k_col = st.columns(2)
    with v_col:
        st.markdown("Vibe <span class='required'>*</span>", unsafe_allow_html=True)
        vibe = st.selectbox("v", options=["Chill", "Cramming", "Group Project"], label_visibility="collapsed")
    with k_col:
        st.markdown("Secret Key <span class='required'>*</span>", unsafe_allow_html=True)
        user_key = st.text_input("k", type="password", label_visibility="collapsed")

    st.markdown("Description (Optional)", unsafe_allow_html=True)
    desc = st.text_area("de", label_visibility="collapsed", max_chars=100)

    submit = st.form_submit_button("POST TO USC MAP")

    if submit:
        if not course or not location or not user_key:
            st.error("Missing required fields!")
        else:
            fs, fe = datetime.combine(study_date, start_t), datetime.combine(study_date, end_t)
            if (fe - fs) > timedelta(hours=5):
                st.error("Max 5 hours allowed!")
            elif fe <= fs:
                st.error("End time must be after start time.")
            else:
                lat, lon = get_coords(location)
                new_data = {'Course': course.upper(), 'Location': location, 'Vibe': vibe, 'Description': desc, 
                            'Start_Time': fs, 'End_Time': fe, 'Key': user_key, 'lat': lat, 'lon': lon}
                st.session_state.sessions = pd.concat([st.session_state.sessions, pd.DataFrame([new_data])], ignore_index=True)
                # FIX: Success message in AM/PM
                st.success(f"Posted! Ends at {fe.strftime('%I:%M %p')}")
                st.rerun()

# --- ACTIVE LIST ---
st.markdown("### 🤝 Active Sessions")
for i, row in st.session_state.sessions.iterrows():
    # FIX: Expander Header in AM/PM
    start_str = row['Start_Time'].strftime('%I:%M %p')
    end_str = row['End_Time'].strftime('%I:%M %p')
    
    with st.expander(f"📖 {row['Course']} @ {row['Location']} ({start_str})"):
        st.write(f"**Vibe:** {row['Vibe']} | **Ends:** {end_str}")
        if row['Description']: st.write(f"_{row['Description']}_")
        
        c_join, c_edit, c_del = st.columns([2, 1, 1])
        with c_join:
            if st.button(f"Join {row['Course']}", key=f"j{i}"):
                st.balloons()
        with c_edit:
            with st.popover("Edit"):
                e_key = st.text_input("Key", type="password", key=f"ek{i}")
                if e_key == row['Key']:
                    new_l = st.text_input("New Loc", value=row['Location'], key=f"el{i}")
                    if st.button("Save", key=f"es{i}"):
                        st.session_state.sessions.at[i, 'Location'] = new_l
                        st.rerun()
        with c_del:
            with st.popover("Delete"):
                if st.button("Confirm Delete", key=f"dc{i}"):
                    st.session_state.sessions = st.session_state.sessions.drop(i)
                    st.rerun()
