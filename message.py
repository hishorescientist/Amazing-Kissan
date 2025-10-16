import streamlit as st
import gspread
import json
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# ---------- GOOGLE SHEET CONFIG ----------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource(show_spinner=False)
def connect_chat_sheet():
    """Connect to Google Sheet for chat messages."""
    if "google" not in st.secrets or "creds" not in st.secrets["google"]:
        st.warning("⚠️ Missing Google credentials.")
        return None
    try:
        creds_json = st.secrets["google"]["creds"]
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        client = gspread.authorize(creds)
        # Open or create 'Chat' sheet
        sheet = client.open("User").worksheet("Chat")  # Inside same Google Sheet
        return sheet
    except Exception as e:
        st.warning(f"⚠️ Could not connect to Google Sheets: {e}")
        return None


# ---------- CHAT FUNCTIONS ----------
def load_messages(sheet):
    if not sheet:
        return []
    try:
        data = sheet.get_all_records()
        return data[-50:]  # show last 50 messages
    except Exception:
        return []

def save_message(sheet, username, message):
    if not sheet:
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        sheet.append_row([username, message, now])
    except Exception as e:
        st.error(f"❌ Failed to send message: {e}")


# ---------- MAIN APP ----------
def app():
    st.title("💬 Messenger")
    st.caption("Chat with other logged-in users in real time.")

    sheet = connect_chat_sheet()

    if "user" not in st.session_state or not st.session_state.get("logged_in", False):
        st.warning("⚠️ Please log in first.")
        st.stop()

    username = st.session_state.user.get("username", "Anonymous")

    # Chat display area
    st.subheader("Messages")
    messages = load_messages(sheet)
    chat_container = st.container()

    with chat_container:
        for msg in messages:
            with st.chat_message("user" if msg["username"] == username else "assistant"):
                st.markdown(f"**{msg['username']}**: {msg['message']}")
                st.caption(msg["time"])

    # Message input
    user_msg = st.chat_input("Type a message...")

    if user_msg:
        save_message(sheet, username, user_msg)
        st.rerun()