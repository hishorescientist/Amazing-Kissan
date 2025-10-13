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
            {"role": "system", "content": "You are a helpful assistant who outputs English topics only."},
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
            {"role": "system", "content": "You are a helpful assistant who outputs English topics only."},
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

    models = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    for model in models:
        data = {"model": model, "messages": conversation}
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            if resp.status_code == 200:
                answer = resp.json()["choices"][0]["message"]["content"].strip()
                return answer, model
        except:
            continue
    return "❌ AI request failed", "None"


# ------------------- STREAMLIT APP -------------------
def app():
    st.title("🌾 AI Assistant for Farmers (All Languages → English)")

    # Session defaults
    for key in ["ai_mode", "current_topic", "ai_history", "user_chats", "guest_chats"]:
        if key not in st.session_state:
            st.session_state[key] = None if key == "current_topic" else {} if key in ["user_chats", "guest_chats"] else []

    # If user logged out elsewhere
    if not st.session_state.get("logged_in"):
        st.session_state.ai_history = []
        st.session_state.current_topic = None
        st.session_state.user_chats = {}
        st.session_state.page = "Login"
        st.warning("🔒 Please log in to continue.")
        st.stop()

    username = st.session_state.user["username"]

    # Load old chats
    if GOOGLE_SHEET_ENABLED and not st.session_state.user_chats:
        st.session_state.user_chats = load_user_chats(username)

    # Topic selection
    topics = list(st.session_state.user_chats.keys()) or ["New Chat"]
    selected_topic = st.selectbox("📂 Select a topic:", topics, index=topics.index(st.session_state.current_topic) if st.session_state.current_topic in topics else 0)

    if selected_topic != st.session_state.current_topic:
        st.session_state.current_topic = selected_topic
        st.session_state.ai_history = st.session_state.user_chats.get(selected_topic, [])
        st.rerun()

    # Display topic
    st.subheader(f"📘 Topic: {st.session_state.current_topic}")

    # Display chat history
    for msg in st.session_state.ai_history:
        st.markdown(f"**🧑‍🌾 You:** {msg['question']}")
        st.markdown(f"**🤖 AI:** {msg['answer']}")
        st.markdown("---")

    # ------------------- CHAT INPUT -------------------
    user_input = st.chat_input("💬 Type your question here (any language)...")

    # Handle new input instantly
    if user_input:
        st.session_state["pending_input"] = user_input
        st.rerun()

    # Process pending input
    if "pending_input" in st.session_state:
        question = st.session_state["pending_input"]
        del st.session_state["pending_input"]

        topic = st.session_state.current_topic or "New Chat"
        full_history = st.session_state.ai_history.copy()

        # Ask AI
        answer, model = ask_ai(question, full_history)

        chat_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "question": question,
            "answer": answer
        }

        # Save locally
        if topic not in st.session_state.user_chats:
            st.session_state.user_chats[topic] = []
        st.session_state.user_chats[topic].append(chat_entry)
        st.session_state.ai_history.append(chat_entry)

        # Update topic if needed
        if len(st.session_state.ai_history) >= 3:
            new_topic = update_topic(st.session_state.ai_history, list(st.session_state.user_chats.keys()))
            if new_topic and new_topic != topic:
                st.session_state.user_chats[new_topic] = st.session_state.user_chats.pop(topic)
                st.session_state.current_topic = new_topic
                topic = new_topic

        # Save chat to Google Sheet
        save_chat(username, topic, question, answer)

        # Display immediately
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            st.markdown(answer)