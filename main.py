# main.py
import streamlit as st
from login import app as login_page
from profile import app as profile_page
from ai_assistant import app as ai_page
from home import app as home_page
from about import app as about_page
from contact import app as contact_page

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🌾 Agriculture Assistant", layout="wide")

# Hide default menu & toolbar
st.markdown("""
<style>
#MainMenu { visibility: hidden; }
footer {visibility: hidden;}
[data-testid="stToolbarActions"] { visibility: hidden; }
[data-testid="stSidebar"] button[aria-label="Toggle sidebar"]::before {
    content: "🛠️";
    font-size: 20px;
    color: #FF5733;
}
</style>
""", unsafe_allow_html=True)

# ------------------- SESSION STATE -------------------
default_state = {
    "page": "Home",
    "logged_in": False,
    "user": None,
    "ai_history": [],
    "current_topic": None,
    "user_chats": {},
    "redirect_done": False
}
for k, v in default_state.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------------------- SIDEBAR MENU -------------------
st.sidebar.title("🌿 Navigation")
main_menu = ["Home", "About", "AI Assistant", "Contact"]
if st.session_state.logged_in:
    main_menu.append("Profile")
else:
    main_menu.append("Login")

for item in main_menu:
    if st.sidebar.button(item, use_container_width=True, key=f"nav_{item}"):
        st.session_state.page = item
        st.session_state.redirect_done = False
        st.rerun()

# ------------------- AI OPTIONS -------------------
st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ AI Assistant Options", expanded=False):
    if st.button("🆕 New Chat", key="ai_new", use_container_width=True):
        st.session_state.current_topic = None
        st.session_state.ai_history = []
        st.session_state.page = "AI Assistant"
        st.rerun()

    # Load old chats for logged-in user
    if st.session_state.logged_in and st.session_state.user:
        if not st.session_state.user_chats:
            from ai_assistant import connect_google_sheet
            sheet = connect_google_sheet()
            if sheet:
                try:
                    rows = sheet.get_all_records()
                    user_chats = {}
                    username = st.session_state.user.get("username", "")
                    for row in rows:
                        if row.get("username") == username:
                            topic = row.get("topic", "Untitled")
                            if topic not in user_chats:
                                user_chats[topic] = []
                            user_chats[topic].append({
                                "timestamp": row.get("timestamp", ""),
                                "question": row.get("question", ""),
                                "answer": row.get("answer", "")
                            })
                    st.session_state.user_chats = user_chats
                except:
                    pass

        if st.session_state.user_chats:
            topics = list(st.session_state.user_chats.keys())
            def set_old_topic():
                st.session_state.current_topic = st.session_state.selected_old_topic_main
                st.session_state.ai_history = st.session_state.user_chats.get(
                    st.session_state.current_topic, []
                )
                st.session_state.page = "AI Assistant"
                st.rerun()
            st.selectbox(
                "📚 Select a saved chat:",
                topics[::-1],
                key="selected_old_topic_main",
                on_change=set_old_topic
            )

# ------------------- PAGE ROUTING -------------------
page = st.session_state.page
if page == "Home":
    home_page()
elif page == "About":
    about_page()
elif page == "AI Assistant":
    ai_page()
elif page == "Contact":
    contact_page()
elif page == "Login":
    login_page()
elif page == "Profile":
    profile_page()