# 💬 Messenger Page
# ----------------------------
# Features:
# - Public & Private chat modes
# - Google Sheet-based message storage
# - Like system with live updates
# - Session-safe key handling

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
def get_client():
    """Authenticate and return Google Sheets client."""
    creds_json = st.secrets["google"]["creds"]
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    return gspread.authorize(creds)

def get_message_sheet():
    """Return messages worksheet."""
    client = get_client()
    sheet = client.open("amazing_kissan_data").worksheet("messages")
    return sheet

# ---------- MESSAGE OPERATIONS ----------
def add_message(sheet, username, text, mode="Public"):
    """Add a new message to the sheet."""
    data = sheet.get_all_records()
    next_id = len(data) + 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([next_id, username, text, 0, timestamp, mode])

def update_likes(sheet, msg_id):
    """Increment likes in the Google Sheet."""
    data = sheet.get_all_records()
    for i, msg in enumerate(data, start=2):  # Start=2 to skip header row
        if str(msg.get("id")) == str(msg_id):
            current_likes = int(msg.get("likes", 0) or 0)
            sheet.update_cell(i, 4, current_likes + 1)
            break

# ---------- SAFE LIKE HANDLER ----------
def safe_like_update(sheet, msg_id, like_key):
    """Safely updates like count without duplicate keys."""
    if like_key not in st.session_state or not isinstance(st.session_state[like_key], int):
        st.session_state[like_key] = 0
    st.session_state[like_key] += 1
    update_likes(sheet, msg_id)
    st.rerun()

# ---------- MAIN PAGE ----------
def app():
    st.set_page_config(page_title="Messenger", page_icon="💬", layout="centered")
    st.title("💬 Messenger")
    st.caption("Chat publicly or privately — powered by Google Sheets")

    # ----- Select chat mode -----
    mode = st.radio("Choose Chat Mode:", ["🌍 Public", "🔒 Private"], horizontal=True)

    msg_sheet = get_message_sheet()
    all_messages = msg_sheet.get_all_records()

    # ----- Input box -----
    st.divider()
    st.subheader("📨 Send a Message")

    username = st.text_input("Your Name:", key="username_input")
    message_text = st.text_area("Type your message:", key="msg_input", height=100)

    if st.button("Send", use_container_width=True, key="send_btn"):
        if username.strip() and message_text.strip():
            add_message(msg_sheet, username.strip(), message_text.strip(), mode.replace("🌍 ", "").replace("🔒 ", ""))
            st.success("✅ Message sent!")
            st.rerun()
        else:
            st.warning("⚠️ Please enter both name and message.")

    st.divider()

    # ----- Message feed -----
    st.subheader("🗨️ Message Feed")

    # Filter messages by mode
    if "Public" in mode:
        messages = [m for m in all_messages if m.get("mode", "Public") == "Public"]
    else:
        messages = [m for m in all_messages if m.get("mode", "Public") == "Private"]

    if not messages:
        st.info("No messages yet. Start the conversation!")
        return

    for i, msg in enumerate(reversed(messages), start=1):
        user = msg.get("username", "Unknown")
        text = msg.get("message", "")
        likes = int(msg.get("likes", 0) or 0)
        timestamp = msg.get("timestamp", "—")
        msg_id = msg.get("id", i)

        with st.container():
            st.markdown(
                f"**{user}** says:  \n> {text}  \n"
                f"<small>🕒 {timestamp}</small>",
                unsafe_allow_html=True
            )

            col1, col2 = st.columns([1, 9])
            like_key = f"like_{msg_id}_{i}"

            # Initialize like count in session safely
            if like_key not in st.session_state or not isinstance(st.session_state[like_key], int):
                st.session_state[like_key] = likes

            with col1:
                if st.button(f"❤️ {st.session_state[like_key]}", key=f"btn_{like_key}"):
                    safe_like_update(msg_sheet, msg_id, like_key)

            st.markdown("---")

# ---------- RUN PAGE ----------
if __name__ == "__main__":
    app()