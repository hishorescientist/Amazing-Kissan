# main.py
import streamlit as st
import requests

from login import app as login_page
from profile import app as profile_page
from home import app as home_page
from about import app as about_page
from contact import app as contact_page
from ai_assistant import app as ai_page
from utils import connect_google_sheet

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🌾 Agriculture Assistant", layout="wide")

# Hide Streamlit menu and change sidebar icon
hide_menu = """
<style>
[data-testid="stSidebar"] button[aria-label="Toggle sidebar"]::before {
    content: "🛠️";
    font-size: 20px;
    color: #FF5733;
}
#MainMenu {visibility:hidden;}
[data-testid="stToolbarActions"] {visibility:hidden;}
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

# ------------------- SIDEBAR NAVIGATION -------------------
st.sidebar.title("🌿 Navigation")
main_menu = ["Home", "About", "AI Assistant", "Contact"]
if not st.session_state.logged_in:
    main_menu.append("Login")
else:
    main_menu.append("Profile")

for item in main_menu:
    if st.sidebar.button(item, use_container_width=True):
        st.session_state.page = item
        st.session_state.redirect_done = False
        st.experimental_rerun()

# ------------------- AI ASSISTANT OPTIONS -------------------
st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ AI Assistant Options", expanded=False):
    if st.button("🆕 New Chat", key="ai_new"):
        st.session_state.ai_mode = "new"
        st.session_state.current_topic = None
        st.session_state.ai_history = []
        st.session_state.page = "AI Assistant"
        st.experimental_rerun()

    if st.button("👤 Guest Chat", key="ai_guest"):
        st.session_state.ai_mode = "guest"
        st.session_state.current_topic = None
        st.session_state.ai_history = []
        st.session_state.page = "AI Assistant"
        st.experimental_rerun()

# ------------------- Agri News Sidebar -------------------
st.sidebar.markdown("---")
st.sidebar.subheader("📰 Agri News")
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