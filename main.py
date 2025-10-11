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
import streamlit.components.v1 as components
# Add this function and call it at the beginning of your script


# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🌾 Agriculture Assistant", layout="wide")

# place this immediately after st.set_page_config(...)
# keep footer hidden (optional)
st.markdown('<style>footer{display:none !important;}</style>', unsafe_allow_html=True)

# client-side JS to remove only the top-right system buttons (but NOT anything inside the sidebar)
components.html(
    """
    <script>
    (function removeStreamlitTopButtons(){
      // selectors to catch common Streamlit toolbar/decoration/share widgets across versions
      const selectors = [
        'div[data-testid="stToolbar"]',
        'div[data-testid="stDecoration"]',
        'div[data-testid="stStatusWidget"]',
        'button[title*="Rerun"]',
        'button[title*="Settings"]',
        'button[title*="Share"]',
        'a[href*="github.com"]',
        'a[title*="Fork"]',
        'div[title="Share this app"]',
        'a[data-testid="share-button"]'
      ];

      function removeIfNotSidebar(el){
        // protect sidebar: don't remove elements that are inside the sidebar area
        if (!el) return false;
        if (el.closest && el.closest('[data-testid="stSidebar"]')) return false;
        el.remove();
        return true;
      }

      function attemptCleanup(){
        let removedCount = 0;
        selectors.forEach(sel => {
          document.querySelectorAll(sel).forEach(el => {
            if (removeIfNotSidebar(el)) removedCount++;
          });
        });
        return removedCount;
      }

      // Try several times while Streamlit finishes rendering
      let tries = 0;
      const maxTries = 12;
      const interval = setInterval(() => {
        tries++;
        const removed = attemptCleanup();
        // stop early if we removed something or after max tries
        if (removed > 0 || tries >= maxTries) {
          clearInterval(interval);
        }
      }, 250);
    })();
    </script>
    """,
    height=0,
)

# ------------------- SESSION STATE -------------------
default_state = {
    "page": "Home",
    "logged_in": False,
    "user": None,
    "ai_history": [],
    "ai_mode": "guest",
    "current_topic": None,
    "user_chats": {},
    "redirect_done": False  # prevents rerun loop after login
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
        creds_json = st.secrets["google"]["creds"]
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        client = gspread.authorize(creds)
        return client.open("User").worksheet("ai data")
    except Exception as e:
        st.warning(f"⚠️ Could not connect to Google Sheets: {e}")
        return None

sheet = connect_google_sheet()

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
with st.sidebar.expander("⚙️ AI Assistant Options", expanded=False):

    # 🆕 New Chat
    if st.button("🆕 New Chat", key="ai_new", use_container_width=True):
        st.session_state.ai_mode = "new"
        st.session_state.current_topic = None
        st.session_state.ai_history = []
        st.session_state.page = "AI Assistant"
        st.rerun()

    # 👤 Guest Chat
    if st.button("👤 Guest Chat", key="ai_guest", use_container_width=True):
        st.session_state.ai_mode = "guest"
        st.session_state.current_topic = None
        st.session_state.ai_history = []
        st.session_state.page = "AI Assistant"
        st.rerun()

    # 📂 Load Old Chats (Logged-in Users)
    if st.session_state.logged_in and st.session_state.user:
        # Load user chats if not already loaded
        if not st.session_state.user_chats and sheet:
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

        # Display selectbox only if chats exist
        if st.session_state.user_chats:
            topics = list(st.session_state.user_chats.keys())
            def _set_topic():
                st.session_state.current_topic = st.session_state.selected_old_topic
                st.session_state.ai_history = st.session_state.user_chats.get(
                    st.session_state.current_topic, []
                )
                st.session_state.ai_mode = "old"
                st.session_state.page = "AI Assistant"
                st.rerun()

            st.selectbox(
                "📚 Select a saved chat:",
                topics[::-1],
                key="selected_old_topic",
                on_change=_set_topic
            )

# ------------------- Optional: Agri News Sidebar -------------------
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


# ------------------- PAGE ROUTING -------------------
# Direct logged-in users from login to profile
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