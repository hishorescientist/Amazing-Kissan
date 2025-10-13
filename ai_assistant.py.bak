import streamlit as st
import requests
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from langdetect import detect

# ---------------- GOOGLE SHEET CONNECTION ----------------
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


# ---------------- HELPER FUNCTIONS ----------------
def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

def load_user_chats(username):
    if not GOOGLE_SHEET_ENABLED:
        return {}
    try:
        rows = sheet.get_all_records()
        user_chats = {}
        for row in rows:
            if str(row.get("username", "")).strip().lower() == username.strip().lower():
                topic = row.get("topic", "New Chat").strip()
                user_chats.setdefault(topic, []).append({
                    "timestamp": row.get("timestamp", ""),
                    "question": row.get("question", ""),
                    "answer": row.get("answer", "")
                })
        return user_chats
    except Exception as e:
        st.warning(f"⚠️ Failed to load chats: {e}")
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
    except Exception as e:
        st.warning(f"⚠️ Failed to save chat: {e}")

def generate_topic(question, answer, existing_topics):
    api_key = st.secrets.get("GROQ_API_KEY")
    prompt = f"Give a 3–5 word English topic summarizing this chat:\nQ: {question}\nA: {answer}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"} if api_key else {}
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You output short English topic names only."},
            {"role": "user", "content": prompt}
        ]
    }

    topic = "New Chat"
    if api_key:
        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=10)
            if r.status_code == 200:
                topic = r.json()["choices"][0]["message"]["content"].strip()
        except:
            pass

    for existing in existing_topics:
        if topic.lower() in existing.lower() or existing.lower() in topic.lower():
            return existing
    return topic

def ask_ai(question, history):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return "❌ Missing API Key", "None"

    conversation = [{"role": "system", "content": "You are an expert agricultural AI assistant."}]
    for msg in history:
        conversation.append({"role": "user", "content": msg["question"]})
        conversation.append({"role": "assistant", "content": msg["answer"]})
    conversation.append({"role": "user", "content": question})

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    models = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant"]

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


# ---------------- STREAMLIT APP ----------------
def app():
    st.title("🌾 AI Assistant for Farmers")

    # Redirect if not logged in
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("⚠️ Please log in first.")
        st.session_state.page = "Login"
        st.rerun()

    username = st.session_state.user["username"]

    # Initialize session variables
    if "user_chats" not in st.session_state:
        st.session_state.user_chats = load_user_chats(username) if GOOGLE_SHEET_ENABLED else {}
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = "New Chat"
    if "ai_history" not in st.session_state:
        st.session_state.ai_history = []

    topic = st.session_state.current_topic

    st.subheader(f"📘 Topic: {topic}")

    # Display chat history
    if st.session_state.ai_history:
        for msg in st.session_state.ai_history:
            st.markdown(f"**🧑‍🌾 You:** {msg['question']}")
            st.markdown(f"**🤖 AI:** {msg['answer']}")
            st.markdown("---")
    else:
        st.info("💬 Start by asking a question below!")

    # Chat input
    user_input = st.chat_input("💬 Type your question here...")

    # Handle input instantly
    if user_input:
        st.session_state["pending_input"] = user_input
        st.rerun()

    # Process input
    if "pending_input" in st.session_state:
        question = st.session_state["pending_input"]
        del st.session_state["pending_input"]

        history = st.session_state.ai_history
        answer, _ = ask_ai(question, history)

        chat_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "question": question,
            "answer": answer
        }

        # Add to chat history
        history.append(chat_entry)
        st.session_state.ai_history = history

        # Auto-generate topic (once first AI reply comes)
        if topic == "New Chat" and len(history) == 1:
            new_topic = generate_topic(question, answer, list(st.session_state.user_chats.keys()))
            st.session_state.current_topic = new_topic
            st.session_state.user_chats[new_topic] = history
            topic = new_topic
        else:
            st.session_state.user_chats[topic] = history

        # Save chat
        if GOOGLE_SHEET_ENABLED:
            save_chat(username, topic, question, answer)

        # Display latest message
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            st.markdown(answer)