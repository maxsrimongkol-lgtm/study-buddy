import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- USC BRANDING & UNIFIED FLAT UI ---
st.set_page_config(page_title="USC Study Buddy", page_icon="✌️", layout="centered")

st.markdown("""
    <style>
    /* 1. Reset Background */
    .stApp { background-color: #FFFFFF !important; }
    
    /* 2. Bold Black Headings */
    h1, h2, h3 { 
        color: #990000 !important; 
        font-weight: 800 !important;
        margin-bottom: 5px !important;
    }
    
    /* 3. Universal Label Style */
    label, p, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 700 !important; 
    }

    /* 4. UNIFIED SIMPLE RED BOXES FOR ALL INPUTS */
    /* Targets every input type to ensure 2px solid red borders */
    input, select, textarea, [data-baseweb="select"], [data-baseweb="input"], 
    .stDateInput div, .stTimeInput div, div[role="listbox"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #990000 !important; /* Simple Red Box */
        border-radius: 4px !important;
        box-shadow: none !important; /* Removes inconsistent shadows */
    }

    /* 5. HIGH-CONTRAST POST BUTTON (Black background with Gold Text) */
    /* Using Black/Gold makes the button stand out from the Red/White form */
    div.stButton > button:first-child {
        background-color: #000000 !important; 
        color: #FFC72C !important; 
        height: 4em !important;
        width: 100% !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        border: 2px solid #FFC72C !important;
        border-radius: 4px !important;
        text-transform: uppercase;
        margin-top: 20px;
    }
    
    /* Small Fix for Date/Time picker text color */
    div[data-baseweb="input"] input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }
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
st.write(f"Current Time: **{now.strftime('%I:%M %p')}**")
st.write("---")

# --- MAP SECTION ---
st.subheader("📍 Live Map")
if not st.session_state.sessions.empty:
    st.map(st.session_state.sessions[['lat', 'lon']])

# --- FORM SECTION ---
with st.form("main_form", clear_on_submit=True):
    st.subheader("🚀 Post a Session")
    
    st.markdown("Course Code *")
    course = st.text_input("c", label_visibility="collapsed", placeholder="e.g. CSCI 103")
    
    st.markdown("Exact Location *")
    location = st.text_input("l", label_visibility="collapsed", max_chars=50, placeholder="e.g. Leavey 2nd Floor")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("Date *")
        study_date = st.date_input("d", label_visibility="collapsed")
    with c2:
        st.markdown("Start Time *")
        start_t = st.time_input("s", label_visibility="collapsed") # Will show AM/PM based on browser
    with c3:
        st.markdown("End Time *")
        end_t = st.time_input("e", label_visibility="collapsed", value=(now + timedelta(hours=2)))

    v_col, k_col = st.columns(2)
    with v_col:
        st.markdown("Vibe *")
        vibe = st.selectbox("v", options=["Chill", "Cramming", "Group Project"], label_visibility="collapsed")
    with k_col:
        st.markdown("Secret Key *")
        user_key = st.text_input("k", type="password", label_visibility="collapsed", placeholder="To edit/delete")

    st.markdown("Description (Optional)")
    desc = st.text_area("de", label_visibility="collapsed", max_chars=100)

    # REFINED POST BUTTON
    submit = st.form_submit_button("POST TO USC MAP")

    if submit:
        if not course or not location or not user_key:
            st.error("Please fill in required fields.")
        else:
            fs, fe = datetime.combine(study_date, start_t), datetime.combine(study_date, end_t)
            if (fe - fs) > timedelta(hours=5):
                st.error("Maximum 5 hours.")
            elif fe <= fs:
                st.error("End time must be after start.")
            else:
                lat, lon = get_coords(location)
                new_data = {'Course': course.upper(), 'Location': location, 'Vibe': vibe, 'Description': desc, 
                            'Start_Time': fs, 'End_Time': fe, 'Key': user_key, 'lat': lat, 'lon': lon}
                st.session_state.sessions = pd.concat([st.session_state.sessions, pd.DataFrame([new_data])], ignore_index=True)
                st.success(f"Posted! Active until {fe.strftime('%I:%M %p')}")
                st.rerun()

# --- ACTIVE LIST ---
st.write("---")
st.subheader("🤝 Active Sessions")
for i, row in st.session_state.sessions.iterrows():
    start_str = row['Start_Time'].strftime('%I:%M %p')
    end_str = row['End_Time'].strftime('%I:%M %p')
    
    with st.expander(f"📖 {row['Course']} @ {row['Location']} (Starts {start_str})"):
        st.write(f"**Vibe:** {row['Vibe']} | **Ends:** {end_str}")
        if row['Description']: st.write(f"_{row['Description']}_")
        
        c_join, c_del = st.columns([3, 1])
        with c_join:
            if st.button(f"Join Group", key=f"j{i}"):
                st.balloons()
        with c_del:
            with st.popover("Delete"):
                d_key = st.text_input("Enter Key", type="password", key=f"dk{i}")
                if st.button("Confirm", key=f"dc{i}"):
                    if d_key == row['Key']:
                        st.session_state.sessions = st.session_state.sessions.drop(i)
                        st.rerun()
