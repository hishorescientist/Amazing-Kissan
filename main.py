# main.py
import streamlit as st
import json
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

from login import app as login_page
from profile import app as profile_page
from ai_assistant import app as ai_page
from home import app as home_page
from about import app as about_page
from contact import app as contact_page

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🌾 Agriculture Assistant", layout="wide")

# Hide default Streamlit menu and toolbar, customize sidebar toggle
st.markdown("""
<style>
[data-testid="stSidebar"] button[aria-label="Toggle sidebar"]::before {
    content: "🛠️";
    font-size: 20px;
    color: #FF5733;
}
#MainMenu {visibility: hidden;}
[data-testid="stToolbarActions"] {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ------------------- SESSION STATE -------------------
default_state = {
    "page": "Home",
    "logged_in": False,
    "user": None,
    "ai_history": [],
    "ai_mode": "guest",
    "current_topic": None,
    "user_chats": {},
    "guest_chats": {},
    "redirect_done": False
}
for k, v in default_state.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------------------- GOOGLE SHEET SETUP -------------------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

def connect_google_sheet():
    if "google" not in st.secrets or "creds" not in st.secrets["google"]:
        return None
    try:
        creds_dict = json.loads(st.secrets["google"]["creds"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        client = gspread.authorize(creds)
        return client.open("User").worksheet("ai data")
    except Exception as e:
        st.warning(f"⚠️ Could not connect to Google Sheets: {e}")
        return None

sheet = connect_google_sheet()

# ------------------- SIDEBAR NAVIGATION -------------------
st.sidebar.title("🌿 Navigation")
main_menu = ["Home", "About", "AI Assistant", "Contact", "Login"]
for item in main_menu:
    if st.sidebar.button(item, use_container_width=True):
        st.session_state.page = item
        st.session_state.redirect_done = False
        st.rerun()

# ------------------- AI ASSISTANT OPTIONS -------------------
st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ AI Assistant Options", expanded=False):
    # New Chat
    if st.button("🆕 New Chat", key="ai_new", use_container_width=True):
        st.session_state.ai_mode = "new"
        st.session_state.current_topic = None
        st.session_state.ai_history = []
        st.session_state.page = "AI Assistant"
        st.rerun()

    # Guest Chat
    if st.button("👤 Guest Chat", key="ai_guest", use_container_width=True):
        st.session_state.ai_mode = "guest"
        st.session_state.current_topic = None
        st.session_state.ai_history = []
        st.session_state.page = "AI Assistant"
        st.rerun()

    # Load Old Chats (Logged-in Users)
    if st.session_state.logged_in and st.session_state.user and sheet:
        if not st.session_state.user_chats:
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
            except Exception as e:
                st.warning(f"⚠️ Failed to load chats: {e}")

        # Show current topic if any
        if st.session_state.user_chats and st.session_state.current_topic is None:
            st.session_state.current_topic = list(st.session_state.user_chats.keys())[0]
            st.session_state.ai_history = st.session_state.user_chats.get(st.session_state.current_topic, [])

# ------------------- AGRO NEWS -------------------
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
    except Exception:
        return []

for n in get_agri_news(query):
    st.sidebar.markdown(f"**[{n['title']}]({n['url']})**")
    st.sidebar.caption(n["source"]["name"])
    st.sidebar.markdown("---")

# ------------------- LOGIN REDIRECT -------------------
if st.session_state.logged_in and st.session_state.page == "Login" and not st.session_state.redirect_done:
    st.session_state.page = "Profile"
    st.session_state.redirect_done = True
    st.rerun()

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
    if st.session_state.logged_in:
        profile_page()
    else:
        st.warning("⚠️ Please log in to view your profile")