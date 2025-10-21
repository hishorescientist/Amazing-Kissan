# ai_assistant.py
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
        creds_json = st.secrets["google"]["secrets_creds"]
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

    # Avoid duplicates
    for existing in existing_topics:
        if topic.lower() in existing.lower() or existing.lower() in topic.lower():
            return existing
    return topic

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
def app():
    st.title("🌾 AI Assistant for Farmers")

    # ---------------- Login Check ----------------
    if not st.session_state.get("logged_in"):
        st.warning("🔒 Please log in first.")
        st.stop()

    username = st.session_state.user["username"]

    # ---------------- Load User Chats ----------------
    if GOOGLE_SHEET_ENABLED and not st.session_state.get("user_chats"):
        st.session_state.user_chats = load_user_chats(username)

    # ---------------- Session Variables ----------------
    if "current_topic" not in st.session_state or st.session_state.current_topic is None:
        st.session_state.current_topic = "New Chat"

    topic = st.session_state.current_topic

    # Load existing chat history if not already loaded
    if topic != "New Chat" and not st.session_state.get("ai_history"):
        st.session_state.ai_history = st.session_state.user_chats.get(topic, []).copy()
    elif topic == "New Chat" and "ai_history" not in st.session_state:
        st.session_state.ai_history = []

    st.subheader(f"📘 Topic: {topic}")

    # ---------------- Display Chat History ----------------
    if st.session_state.ai_history:
        for msg in st.session_state.get('ai_history', []):
            st.markdown(
                f"""
                <div class="chat-container">
                    <div class="user-msg"><b>🧑‍🌾 You:</b> {msg['question']}</div>
                </div>
                <div class="chat-container">
                    <div class="ai-msg"><b>🤖 AI:</b> {msg['answer']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("💬 Start chatting below!")

    # ---------------- Chat Input ----------------
    user_input = st.chat_input("💬 Type your question here...")

    if user_input:
        st.session_state["pending_input"] = user_input

    if "pending_input" in st.session_state:
        question = st.session_state.pop("pending_input")

        # ---------------- Ask AI ----------------
        history = st.session_state.ai_history.copy()
        answer, _ = ask_ai(question, history)

        chat_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "question": question,
            "answer": answer
        }

        # ---------------- New Topic Handling ----------------
        if topic == "New Chat" or len(st.session_state.ai_history) == 0:
            new_topic = generate_topic(question, answer, list(st.session_state.user_chats.keys()))
            st.session_state.user_chats[new_topic] = []
            st.session_state.current_topic = new_topic
            st.session_state.ai_history = []  # start clean
            topic = new_topic

        # ---------------- Append to Current Topic ----------------
        st.session_state.ai_history.append(chat_entry)
        st.session_state.user_chats.setdefault(topic, []).append(chat_entry)

        # ---------------- Save to Google Sheet ----------------
        if GOOGLE_SHEET_ENABLED:
            save_chat(username, topic, question, answer)

        # ---------------- Display Instantly ----------------
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            st.markdown(answer)