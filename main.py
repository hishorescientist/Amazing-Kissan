# main.py
import streamlit as st
from utils import connect_google_sheet
from login import app as login_page
from profile import app as profile_page
from ai_assistant import app as ai_page
from home import app as home_page
from about import app as about_page
from contact import app as contact_page

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🌾 Agriculture Assistant", layout="wide")
hide_menu = """
<style>
/* Sidebar toggle emoji */
[data-testid="stSidebar"] button[aria-label="Toggle sidebar"]::before {
    content: "🛠️";
    font-size: 20px;
    color: #FF5733;
}
#MainMenu { visibility:hidden; }
[data-testid="stToolbarActions"] { visibility:hidden; }
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

# ------------------- SESSION STATE -------------------
default_state = {
    "page": "Home",
    "logged_in": False,
    "user": None,
    "ai_history": [],
    "ai_mode": "guest",
    "current_topic": None,
    "user_chats": {},
    "redirect_done": False
}
for k, v in default_state.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------------------- GOOGLE SHEET -------------------
sheet_users = connect_google_sheet("User")
init_ai_sheet("ai data")  # initializes AI chat sheet

# ------------------- SIDEBAR MENU -------------------
st.sidebar.title("🌿 Navigation")
main_menu = ["Home", "About", "AI Assistant", "Contact", "Login"]
for item in main_menu:
    if st.sidebar.button(item, use_container_width=True):
        st.session_state.page = item
        st.session_state.redirect_done = False
        st.rerun()

# ------------------- AI ASSISTANT OPTIONS -------------------
st.sidebar.markdown("---")
from utils import load_user_chats  # import after init_ai_sheet
with st.sidebar.expander("⚙️ AI Assistant Options", expanded=False):
    if st.button("🆕 New Chat", key="ai_new", use_container_width=True):
        st.session_state.ai_mode = "new"
        st.session_state.current_topic = None
        st.session_state.ai_history = []
        st.session_state.page = "AI Assistant"
        st.rerun()

    if st.button("👤 Guest Chat", key="ai_guest", use_container_width=True):
        st.session_state.ai_mode = "guest"
        st.session_state.current_topic = None
        st.session_state.ai_history = []
        st.session_state.page = "AI Assistant"
        st.rerun()

    # Load old chats for logged-in users
    if st.session_state.logged_in and st.session_state.user:
        if not st.session_state.user_chats:
            try:
                st.session_state.user_chats = load_user_chats(st.session_state.user["username"])
            except:
                st.warning("⚠️ Could not load your previous chats.")
        
        if st.session_state.user_chats:
            topics = list(st.session_state.user_chats.keys())
            def _set_topic():
                st.session_state.current_topic = st.session_state.selected_old_topic
                st.session_state.ai_history = st.session_state.user_chats.get(st.session_state.current_topic, [])
                st.session_state.ai_mode = "old"
                st.session_state.page = "AI Assistant"
                st.rerun()
            st.selectbox("📚 Select a saved chat:", topics[::-1],
                         key="selected_old_topic", on_change=_set_topic)

# ------------------- Optional Agri News -------------------
st.sidebar.markdown("---")
st.sidebar.subheader("📰 Agri News")
import requests

query = st.sidebar.text_input("Keyword", value="agriculture")

@st.cache_data(ttl=600)
def get_agri_news(q):
    try:
        api_key = st.secrets.get("NEWS_API_KEY", "")
        if not api_key:
            return []
        url = f"https://newsapi.org/v2/everything?q={q}&language=en&pageSize=5&sortBy=publishedAt&apiKey={api_key}"
        res = requests.get(url).json()
        return res.get("articles", [])
    except:
        return []

for n in get_agri_news(query):
    st.sidebar.markdown(f"**[{n['title']}]({n['url']})**")
    st.sidebar.caption(n["source"]["name"])
    st.sidebar.markdown("---")

# ------------------- PAGE ROUTING -------------------
# Auto-redirect logged-in users from login to profile
if st.session_state.logged_in and st.session_state.page == "Login" and not st.session_state.redirect_done:
    st.session_state.page = "Profile"
    st.session_state.redirect_done = True
    st.rerun()

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