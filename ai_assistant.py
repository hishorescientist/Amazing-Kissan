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
        rows = sheet.get_all_records()
        user_chats = {}
        for row in rows:
            if str(row.get("username", "")).strip().lower() == username.strip().lower():
                topic = row.get("topic", "Untitled").strip()
                if topic not in user_chats:
                    user_chats[topic] = []
                user_chats[topic].append({
                    "timestamp": row.get("timestamp", ""),
                    "question": row.get("question", ""),
                    "answer": row.get("answer", "")
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
        sheet.append_row([
            username,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            topic,
            question,
            answer
        ])
    except Exception as e:
        st.warning(f"⚠️ Failed to save chat: {e}")

def generate_topic(question, answer, existing_topics):
    """Generate a short topic from question and answer"""
    api_key = st.secrets.get("GROQ_API_KEY")
    prompt = f"Provide a short 3-5 word topic in English summarizing this chat:\nQ: {question}\nA: {answer}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"} if api_key else {}
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You output short English topics only."},
            {"role": "user", "content": prompt}
        ]
    }

    topic = "New Chat"
    if api_key:
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=15
            )
            if resp.status_code == 200:
                topic = resp.json()["choices"][0]["message"]["content"].strip()
        except:
            pass

    for existing in existing_topics:
        if topic.lower() in existing.lower() or existing.lower() in topic.lower():
            return existing
    return topic

def update_topic(messages, existing_topics):
    """Generate a dynamic topic based on recent messages"""
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key or not messages:
        return None

    chat_text = "\n".join([f"Q: {m['question']}\nA: {m['answer']}" for m in messages[-5:]])
    prompt = f"Provide a concise 3-5 word English topic summarizing this conversation:\n{chat_text}"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You output short English topics only."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
                             headers=headers, json=data, timeout=15)
        if resp.status_code == 200:
            topic = resp.json()["choices"][0]["message"]["content"].strip()
            for existing in existing_topics:
                if topic.lower() in existing.lower() or existing.lower() in topic.lower():
                    return existing
            return topic
    except:
        pass
    return None

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

    models = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant"]
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    for model in models:
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json={"model": model, "messages": conversation},
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip(), model
        except:
            continue
    return "❌ AI request failed", "None"


# ------------------- STREAMLIT APP -------------------
# ------------------- STREAMLIT APP -------------------
def app():
    st.title("🌾 AI Assistant for Farmers")

    # Ensure login
    if not st.session_state.get("logged_in"):
        st.session_state.page = "Login"
        st.warning("🔒 Please log in first.")
        st.stop()

    username = st.session_state.user["username"]

    # Load previous chats once
    if GOOGLE_SHEET_ENABLED and not st.session_state.get("user_chats"):
        st.session_state.user_chats = load_user_chats(username)

    # Initialize session variables
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = None
    if "ai_history" not in st.session_state:
        st.session_state.ai_history = []

    # If no current topic, default to "New Chat"
    if st.session_state.current_topic is None:
        st.session_state.current_topic = "New Chat"

    topic = st.session_state.current_topic

    # Load ai_history from existing topic if it's not a brand new chat
    if topic != "New Chat" and not st.session_state.ai_history:
        st.session_state.ai_history = st.session_state.user_chats.get(topic, [])

    st.subheader(f"📘 Topic: {topic}")

    # Show previous chat
    if st.session_state.ai_history:
        for msg in st.session_state.ai_history:
            st.markdown(f"**🧑‍🌾 You:** {msg['question']}")
            st.markdown(f"**🤖 AI:** {msg['answer']}")
            st.markdown("---")
    else:
        st.info("💬 Start chatting below!")

    # Get user input
    user_input = st.chat_input("💬 Type your question here...")

    if user_input:
        st.session_state["pending_input"] = user_input
        st.rerun()

    if "pending_input" in st.session_state:
        question = st.session_state["pending_input"]
        del st.session_state["pending_input"]

        history = st.session_state.ai_history.copy()
        answer, _ = ask_ai(question, history)

        chat_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "question": question,
            "answer": answer
        }

        # Append to current topic
        st.session_state.ai_history.append(chat_entry)
        st.session_state.user_chats.setdefault(topic, []).append(chat_entry)

        # Only generate a new topic if this is a brand new chat with no previous messages
        if topic == "New Chat" and len(st.session_state.ai_history) == 1:
            new_topic = generate_topic(question, answer, list(st.session_state.user_chats.keys()))
            st.session_state.user_chats[new_topic] = st.session_state.user_chats.pop("New Chat")
            st.session_state.current_topic = new_topic
            topic = new_topic

        # Save to Google Sheet
        save_chat(username, topic, question, answer)

        # Display immediately
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            st.markdown(answer)