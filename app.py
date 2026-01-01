import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- USC BRANDING & TOTAL UI UNIFICATION ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️", layout="centered")

st.markdown("""
    <style>
    /* 1. Global Page Style */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 2. Heading and Label Clarity */
    h1, h2, h3, p, label { 
        color: #000000 !important; 
        font-weight: 800 !important; 
    }

    /* 3. THE "UNIFORM RED BOX" FIX */
    /* This forces every input type to look identical */
    div[data-baseweb="input"], 
    div[data-baseweb="select"], 
    div[data-baseweb="base-input"],
    .stNumberInput div, .stTextInput div, .stDateInput div, .stTimeInput div, .stSelectbox div {
        background-color: #FFFFFF !important;
        border: 2px solid #990000 !important; /* Solid Cardinal Red */
        border-radius: 4px !important;
        min-height: 45px !important;
    }

    /* 4. TEXT COLOR FIX */
    /* Forces user input text to be Pure Black in all browsers/modes */
    input, textarea, .stSelectbox div[data-baseweb="select"] > div {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 600 !important;
    }

    /* 5. THE POST BUTTON - RED BOX / WHITE TEXT */
    div.stButton > button:first-child {
        background-color: #990000 !important; /* Cardinal Red */
        color: #FFFFFF !important; /* Pure White Text */
        height: 3.5em !important;
        width: 100% !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        border: none !important;
        border-radius: 8px !important;
        text-transform: uppercase;
        margin-top: 15px;
    }
    
    /* Hover effect for clarity */
    div.stButton > button:first-child:hover {
        background-color: #7a0000 !important;
        color: #FFFFFF !important;
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

# --- DATA STORAGE ---
if 'sessions' not in st.session_state:
    st.session_state.sessions = pd.DataFrame(columns=['Course', 'Location', 'Vibe', 'Description', 'Start_Time', 'End_Time', 'Key', 'lat', 'lon'])

now = datetime.now()
st.session_state.sessions = st.session_state.sessions[st.session_state.sessions['End_Time'] > now].reset_index(drop=True)

st.title("✌️ USC Study Buddy")
st.write(f"Current Time: **{now.strftime('%I:%M %p')}**")

# --- FORM SECTION ---
with st.form("main_form", clear_on_submit=True):
    st.subheader("🚀 Post a Session")
    
    st.markdown("Course Code *")
    course = st.text_input("c", label_visibility="collapsed", placeholder="e.g. WRIT 150")
    
    st.markdown("Exact Location *")
    location = st.text_input("l", label_visibility="collapsed", placeholder="e.g. Leavey 3rd Floor")
    
    # Timing Row
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("Date *")
        study_date = st.date_input("d", label_visibility="collapsed")
    with c2:
        st.markdown("Start Time *")
        start_t = st.time_input("s", label_visibility="collapsed")
    with c3:
        st.markdown("End Time *")
        end_t = st.time_input("e", label_visibility="collapsed", value=(now + timedelta(hours=2)))

    # Vibe and Key Row
    v_col, k_col = st.columns(2)
    with v_col:
        st.markdown("Vibe *")
        vibe = st.selectbox("v", options=["Chill", "Cramming", "Group Project"], label_visibility="collapsed")
    with k_col:
        st.markdown("Secret Key *")
        user_key = st.text_input("k", type="password", label_visibility="collapsed", placeholder="Create a PIN")

    st.markdown("Description (Optional)")
    desc = st.text_area("de", label_visibility="collapsed")

    # The Logic
    if st.form_submit_button("Post to USC Map"):
        if course and location and user_key:
            fs, fe = datetime.combine(study_date, start_t), datetime.combine(study_date, end_t)
            if (fe - fs) > timedelta(hours=5):
                st.error("Maximum limit is 5 hours.")
            elif fe <= fs:
                st.error("End time must be after start time.")
            else:
                lat, lon = get_coords(location)
                new_data = {'Course': course.upper(), 'Location': location, 'Vibe': vibe, 'Description': desc, 
                            'Start_Time': fs, 'End_Time': fe, 'Key': user_key, 'lat': lat, 'lon': lon}
                st.session_state.sessions = pd.concat([st.session_state.sessions, pd.DataFrame([new_data])], ignore_index=True)
                st.rerun()

# --- ACTIVE LIST ---
st.write("---")
st.subheader("🤝 Active Sessions")

if not st.session_state.sessions.empty:
    # Optional: Display map
    st.map(st.session_state.sessions[['lat', 'lon']])

for i, row in st.session_state.sessions.iterrows():
    # Force AM/PM Display for User List
    s_disp = row['Start_Time'].strftime('%I:%M %p')
    e_disp = row['End_Time'].strftime('%I:%M %p')
    
    with st.expander(f"📖 {row['Course']} @ {row['Location']} ({s_disp})"):
        st.write(f"**Ends at:** {e_disp} | **Vibe:** {row['Vibe']}")
        if row['Description']: st.write(f"_{row['Description']}_")
        
        c_join, c_del = st.columns([3, 1])
        with c_join:
            if st.button(f"Join {row['Course']}", key=f"j{i}"):
                st.balloons()
                st.success("Fight On! ✌️")
        with c_del:
            with st.popover("Delete"):
                d_check = st.text_input("Key", type="password", key=f"dk{i}")
                if st.button("Confirm", key=f"dcon{i}"):
                    if d_check == row['Key']:
                        st.session_state.sessions = st.session_state.sessions.drop(i)
                        st.rerun()
