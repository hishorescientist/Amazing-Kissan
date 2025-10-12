# ai_assistant.py
import streamlit as st
import requests
import json
from datetime import datetime
from langdetect import detect
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource(show_spinner=False)
def connect_google_sheet():
    try:
        creds_json = st.secrets["google"]["creds"]
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        client = gspread.authorize(creds)
        return client.open("User").worksheet("ai data")
    except Exception as e:
        st.warning(f"⚠️ Google Sheet connection failed: {e}")
        return None

sheet = connect_google_sheet()
GOOGLE_SHEET_ENABLED = sheet is not None

# ------------------- Helper Functions -------------------
def load_user_chats(username):
    if not GOOGLE_SHEET_ENABLED:
        return {}
    try:
        rows = sheet.get_all_records()
        user_chats = {}
        for row in rows:
            if str(row.get("username","")).strip().lower() == username.strip().lower():
                topic = row.get("topic","Untitled").strip()
                if topic not in user_chats:
                    user_chats[topic] = []
                user_chats[topic].append({
                    "timestamp": row.get("timestamp",""),
                    "question": row.get("question",""),
                    "answer": row.get("answer","")
                })
        return user_chats
    except:
        return {}

def save_chat(username, topic, question, answer):
    if not GOOGLE_SHEET_ENABLED:
        return
    try:
        sheet.append_row([
            username,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            topic,
            question,
            answer
        ])
    except:
        pass

# ------------------- Streamlit App -------------------
def app():
    st.title("🌾 AI Assistant for Farmers (All Languages → English)")

    # Session defaults
    for key in ["ai_mode", "current_topic", "ai_history", "user_chats"]:
        if key not in st.session_state:
            st.session_state[key] = None if key=="current_topic" else {} if key=="user_chats" else []

    username = st.session_state.user["username"] if st.session_state.get("logged_in") else "Guest"

    # Load old chats once
    if st.session_state.get("logged_in") and GOOGLE_SHEET_ENABLED and not st.session_state.user_chats:
        st.session_state.user_chats = load_user_chats(username)

    # ------------------- Display Current Topic -------------------
    topic = st.session_state.current_topic
    if topic:
        st.subheader(f"📘 Topic: {topic}")
        st.session_state.ai_history = st.session_state.user_chats.get(topic, [])

    # Display chat history
    if st.session_state.ai_history:
        for msg in st.session_state.ai_history:
            st.markdown(f"**🧑‍🌾 You:** {msg['question']}")
            st.markdown(f"**🤖 AI:** {msg['answer']}")
            st.markdown("---")
    else:
        st.info("💬 Start a new conversation below!")

    # ------------------- Chat Input -------------------
    user_input = st.chat_input("💬 Type your question here (any language)...")
    if user_input:
        topic = st.session_state.current_topic or "New Chat"

        # 1️⃣ Call your ask_ai() function to get AI response
        answer, model = ask_ai(user_input, st.session_state.ai_history)

        # 2️⃣ Append chat entry
        chat_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "question": user_input,
            "answer": answer
        }
        if topic not in st.session_state.user_chats:
            st.session_state.user_chats[topic] = []
        st.session_state.user_chats[topic].append(chat_entry)
        st.session_state.ai_history.append(chat_entry)

        # 3️⃣ Save to Google Sheet
        if st.session_state.get("logged_in") and GOOGLE_SHEET_ENABLED:
            save_chat(username, topic, user_input, answer)

        # 4️⃣ Display messages
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            st.markdown(answer)