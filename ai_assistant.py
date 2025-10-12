import streamlit as st
import requests
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from langdetect import detect

# ------------------- GOOGLE SHEET SETUP -------------------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource(show_spinner=False)
def connect_google_sheet():
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["google"], SCOPE
        )
        client = gspread.authorize(creds)
        sheet = client.open("AI_Assistant_Chats").sheet1
        return sheet
    except Exception as e:
        st.error("⚠️ Could not connect to Google Sheet.")
        st.stop()

SHEET = connect_google_sheet()

# ------------------- FUNCTIONS -------------------
def save_chat_to_sheet(user, topic, role, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    SHEET.append_row([user, topic, role, message, timestamp])

def get_user_chats(username):
    try:
        data = SHEET.get_all_records()
        user_chats = {}
        for row in data:
            if row["User"] == username:
                topic = row["Topic"]
                if topic not in user_chats:
                    user_chats[topic] = []
                user_chats[topic].append({"role": row["Role"], "message": row["Message"]})
        return user_chats
    except Exception as e:
        st.warning("⚠️ Unable to load your chats.")
        return {}

def ai_reply(prompt):
    # Simulated AI response (you can replace this with an API)
    return f"🤖: This is a simulated AI response to: '{prompt}'"

# ------------------- MAIN APP FUNCTION -------------------
def app():
    st.title("🤖 AI Assistant")
    st.write("Chat with your personal AI assistant!")

    if "ai_history" not in st.session_state:
        st.session_state.ai_history = []
    if "ai_mode" not in st.session_state:
        st.session_state.ai_mode = "chat"
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = None
    if "user_chats" not in st.session_state:
        st.session_state.user_chats = {}

    # ------------------- LOGGED-IN MODE -------------------
    if st.session_state.get("logged_in"):
        username = st.session_state.username

        # Load saved chats
        if not st.session_state.user_chats:
            st.session_state.user_chats = get_user_chats(username)

        # 🆕 New Chat button
        if st.button("🆕 New Chat", key="ai_new", use_container_width=True):
            st.session_state.ai_mode = "new"
            st.session_state.current_topic = None
            st.session_state.ai_history = []
            st.session_state.page = "AI Assistant"
            st.rerun()

        # --- OLD CHATS DROPDOWN (only show when NOT in new chat mode) ---
        if (
            st.session_state.user_chats
            and st.session_state.get("ai_mode") != "new"
        ):
            topics = list(st.session_state.user_chats.keys())

            def _set_topic():
                st.session_state.selected_old_topic = st.session_state.ai_selected_old_topic
                st.session_state.current_topic = st.session_state.ai_selected_old_topic
                st.session_state.ai_history = st.session_state.user_chats.get(
                    st.session_state.current_topic, []
                )
                st.session_state.ai_mode = "chat"

            st.selectbox(
                "📚 Select a saved chat:",
                topics[::-1],
                key="ai_selected_old_topic",
                on_change=_set_topic
            )

        # --- CURRENT TOPIC TITLE ---
        if st.session_state.current_topic:
            st.subheader(f"💬 Topic: {st.session_state.current_topic}")
        else:
            st.subheader("🆕 New Chat")

        # --- DISPLAY CHAT HISTORY ---
        for chat in st.session_state.ai_history:
            role = "🧑 You" if chat["role"] == "user" else "🤖 AI"
            with st.chat_message(role):
                st.markdown(chat["message"])

        # --- USER INPUT BOX ---
        prompt = st.chat_input("Type your message...")

        if prompt:
            if not st.session_state.current_topic:
                st.session_state.current_topic = f"Chat - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # User message
            st.session_state.ai_history.append({"role": "user", "message": prompt})
            save_chat_to_sheet(username, st.session_state.current_topic, "user", prompt)

            # AI response
            response = ai_reply(prompt)
            st.session_state.ai_history.append({"role": "assistant", "message": response})
            save_chat_to_sheet(username, st.session_state.current_topic, "assistant", response)

            st.session_state.user_chats[st.session_state.current_topic] = st.session_state.ai_history
            st.session_state.ai_mode = "chat"
            st.rerun()

    # ------------------- GUEST MODE -------------------
    else:
        st.info("👋 Welcome Guest! Your chats are not saved.")
        if st.button("🆕 New Chat", key="guest_new", use_container_width=True):
            st.session_state.ai_history = []
            st.session_state.current_topic = None
            st.rerun()

        for chat in st.session_state.ai_history:
            role = "🧑 You" if chat["role"] == "user" else "🤖 AI"
            with st.chat_message(role):
                st.markdown(chat["message"])

        prompt = st.chat_input("Type your message...")

        if prompt:
            st.session_state.ai_history.append({"role": "user", "message": prompt})
            response = ai_reply(prompt)
            st.session_state.ai_history.append({"role": "assistant", "message": response})
            st.rerun()