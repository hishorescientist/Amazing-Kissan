# ai_assistant.py
import streamlit as st
import requests
from datetime import datetime
from langdetect import detect
from utils import connect_google_sheet  # shared Google Sheet connection

# ------------------- GOOGLE SHEET -------------------
ai_sheet = connect_google_sheet(sheet_name="ai data")
GOOGLE_SHEET_ENABLED = ai_sheet is not None

# ------------------- HELPER FUNCTIONS -------------------
def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

def load_user_chats(username):
    """Load all chats for a username from Google Sheet"""
    if not GOOGLE_SHEET_ENABLED:
        return {}
    try:
        rows = ai_sheet.get_all_records()
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
    except Exception as e:
        st.warning(f"⚠️ Failed to load chats: {e}")
        return {}

def save_chat(username, topic, question, answer):
    """Append a chat to Google Sheet"""
    if not GOOGLE_SHEET_ENABLED:
        return
    try:
        ai_sheet.append_row([
            username,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            topic,
            question,
            answer
        ])
    except Exception as e:
        st.warning(f"⚠️ Failed to save chat: {e}")

def ask_ai(question, history):
    """Ask AI using Groq API"""
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return "❌ Missing API Key", "None"

    conversation = [{"role": "system", "content": "You are an expert agricultural advisor. Respond in English."}]
    for msg in history:
        conversation.append({"role": "user", "content": msg["question"]})
        conversation.append({"role": "assistant", "content": msg["answer"]})
    conversation.append({"role": "user", "content": question})

    models = ["llama-3.1-70b-versatile","llama-3.1-8b-instant","mixtral-8x7b-32768"]
    headers = {"Authorization": f"Bearer {api_key}","Content-Type": "application/json"}

    for model in models:
        data = {"model": model,"messages": conversation}
        try:
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
                                 headers=headers, json=data, timeout=30)
            if resp.status_code == 200:
                answer = resp.json()["choices"][0]["message"]["content"].strip()
                return answer, model
        except:
            continue
    return "❌ AI request failed", "None"

# ------------------- STREAMLIT APP -------------------
def app():
    st.title("🌾 AI Assistant for Farmers (All Languages → English)")

    # Set defaults
    if "ai_history" not in st.session_state:
        st.session_state.ai_history = []
    if "ai_mode" not in st.session_state:
        st.session_state.ai_mode = "guest"
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = None
    if "user_chats" not in st.session_state:
        st.session_state.user_chats = {}

    username = st.session_state.user["username"] if st.session_state.get("logged_in") else "Guest"

    # Load user chats once
    if st.session_state.get("logged_in") and not st.session_state.user_chats:
        st.session_state.user_chats = load_user_chats(username)

    # Old chat selection
    if st.session_state.user_chats:
        topics = list(st.session_state.user_chats.keys())

        def _set_topic():
            st.session_state.current_topic = st.session_state.selected_old_topic
            st.session_state.ai_history = st.session_state.user_chats.get(st.session_state.current_topic, [])

        st.selectbox(
            "📚 Select a saved chat:",
            topics[::-1],
            key="selected_old_topic",
            on_change=_set_topic
        )

    # Show current topic
    if st.session_state.current_topic:
        st.subheader(f"📘 Topic: {st.session_state.current_topic}")

    # Show chat history
    if st.session_state.ai_history:
        for msg in st.session_state.ai_history:
            st.markdown(f"**🧑‍🌾 You:** {msg['question']}")
            st.markdown(f"**🤖 AI:** {msg['answer']}")
            st.markdown("---")
    else:
        st.info("💬 Start a new conversation below!")

    # Chat input
    user_input = st.chat_input("💬 Type your question here (any language)...")
    if user_input:
        topic = st.session_state.current_topic or "New Chat"

        answer, model = ask_ai(user_input, st.session_state.ai_history)

        chat_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "question": user_input,
            "answer": answer
        }

        if topic not in st.session_state.user_chats:
            st.session_state.user_chats[topic] = []
        st.session_state.user_chats[topic].append(chat_entry)
        st.session_state.ai_history.append(chat_entry)
        st.session_state.current_topic = topic

        # Display messages
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            st.markdown(answer)

        # Save chat if logged in
        if st.session_state.get("logged_in"):
            save_chat(username, topic, user_input, answer)