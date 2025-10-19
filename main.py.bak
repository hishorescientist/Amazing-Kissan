import streamlit as st
from login import app as login_page
from profile import app as profile_page
from ai_assistant import app as ai_page
from home import app as home_page
from about import app as about_page
from contact import app as contact_page
from message import app as message_page
from storage import save_state, load_state, clear_state
import streamlit.components.v1 as components
st.markdown("""
    <style>
    .chat-container {
        display: flex;
        margin-bottom: 10px;
    }
    .user-msg {
        background-color: #DCF8C6;
        padding: 10px;
        border-radius: 10px;
        max-width: 80%;
        margin-right: auto;
    }
    .ai-msg {
        background-color: #E6E6E6;
        padding: 10px;
        border-radius: 10px;
        max-width: 80%;
        margin-left: auto;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
    /* Find the container that holds the tab buttons */
    div[role="tablist"] {
        display: flex;
        justify-content: center;
        gap: 10px;
    }

    /* Optional: make the tabs prettier */
    button[role="tab"] {
        font-size: 17px;
        font-weight: 600;
        color: #2E8B57;
        border-radius: 8px;
        padding: 6px 18px;
    }

    /* Highlight the active tab */
    button[role="tab"][aria-selected="true"] {
        background-color: #2E8B57 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🌾 Agriculture Assistant", layout="wide")

# Hide default menu & toolbar
st.markdown("""
<style>
#MainMenu { visibility: hidden; }
[data-testid="stStatusWidget"] {display: none !important;}
[data-testid="stToolbarActions"] { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ------------------- DEFAULT SESSION STATE -------------------
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
        
# ------------------- INITIALIZE LOCAL STORAGE SYNC -------------------
if "initialized" not in st.session_state:
    from storage import load_state
    load_state()  # Triggers browser localStorage load
    st.session_state["initialized"] = True

# ------------------- LOAD STATE FROM LOCAL STORAGE -------------------
# Sync browser -> Streamlit (runs once)
components.html("""
<script>
const saved = localStorage.getItem("agri_app_state");
if (saved) {
  const data = JSON.parse(saved);
  window.parent.postMessage({ type: "RESTORE_STATE", data: data }, "*");
}
</script>
""", height=0)

if "state_loaded" not in st.session_state:
    try:
        saved_state = load_state()  # load from browser cache
        if saved_state:
            for k, v in saved_state.items():
                if k in default_state:
                    st.session_state[k] = v
        st.session_state["state_loaded"] = True
        if st.session_state["page"] != "Home":
            st.rerun()
    except Exception as e:
        st.warning(f"Could not load previous state: {e}")

# ------------------- SIDEBAR -------------------
st.sidebar.title("🌿 Navigation")

main_menu = ["Home", "Message"]

for item in main_menu:
    if st.sidebar.button(item, use_container_width=True, key=f"nav_{item}"):
        st.session_state.page = item
        st.session_state.redirect_done = False
        st.rerun()

# ------------------- AI OPTIONS -------------------
with st.sidebar.expander("⚙️ AI Assistant Options", expanded=False):
    if st.button("🆕 New Chat", key="ai_new", use_container_width=True):
        st.session_state.current_topic = None
        st.session_state.ai_history = []
        st.session_state.page = "AI Assistant"
#        st.rerun()

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
                except Exception:
                    pass

        if st.session_state.user_chats:
            topics = list(st.session_state.user_chats.keys())

            def set_old_topic():
                st.session_state.current_topic = st.session_state.selected_old_topic_main
                st.session_state.ai_history = st.session_state.user_chats.get(
                    st.session_state.current_topic, []
                )
                st.session_state.page = "AI Assistant"
#                st.rerun()

            st.selectbox(
                "📚 Select a saved chat:",
                topics[::-1],
                key="selected_old_topic_main",
                on_change=set_old_topic
            )

main_menu = ["About", "Contact"]
if st.session_state.logged_in:
    main_menu.append("Profile")
else:
    main_menu.append("Login")

for item in main_menu:
    if st.sidebar.button(item, use_container_width=True, key=f"nav_{item}"):
        st.session_state.page = item
        st.session_state.redirect_done = False
        st.rerun()
# ------------------- PAGE ROUTING -------------------
page = st.session_state.page
if page == "Home":
    home_page()
elif page == "About":
    about_page()
elif page == "AI Assistant":
    ai_page()
elif page == "Message":
    message_page()
elif page == "Contact":
    contact_page()
elif page == "Login":
    login_page()
elif page == "Profile":
    profile_page()

# ------------------- SAVE LOCAL STATE -------------------
try:
    keys_to_save = ["page", "logged_in", "user", "ai_history", "current_topic", "user_chats"]
    state_to_save = {k: st.session_state.get(k) for k in keys_to_save}
    save_state(state_to_save)
except Exception as e:
    st.warning(f"Could not save state: {e}")