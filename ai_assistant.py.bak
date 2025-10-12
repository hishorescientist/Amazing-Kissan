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
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key or not messages:
        return None

    chat_text = ""
    for msg in messages[-5:]:
        chat_text += f"Q: {msg['question']}\nA: {msg['answer']}\n"

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
    st.session_state.setdefault("current_topic", None)
    st.session_state.setdefault("ai_history", [])
    st.session_state.setdefault("user_chats", {})
    st.session_state.setdefault("guest_chats", {})

    username = st.session_state.user["username"] if st.session_state.get("logged_in") else "Guest"

    # Load old chats once
    if st.session_state.get("logged_in") and GOOGLE_SHEET_ENABLED and not st.session_state.user_chats:
        st.session_state.user_chats = load_user_chats(username)

    # Determine what to show on top
    if st.session_state.current_topic:
        display_topic = st.session_state.current_topic
    else:
        display_topic = "New Chat"

    st.subheader(f"📘 Topic: {display_topic}")

    # Display chat history
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
        # Combine previous guest messages if needed
        if not st.session_state.get("logged_in"):
            guest_memory = []
            for msgs in st.session_state.get("guest_chats", {}).values():
                guest_memory.extend(msgs)
            full_history = guest_memory + st.session_state.ai_history
        else:
            full_history = st.session_state.ai_history

        with st.spinner("🤖 AI is thinking..."):
            answer, model = ask_ai(user_input, full_history)

        chat_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "question": user_input,
            "answer": answer
        }

        # First message in new chat
        if st.session_state.current_topic is None:
            st.session_state.current_topic = "New Chat"
            st.session_state.ai_history.append(chat_entry)

            # Display first user and AI message immediately
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                st.markdown(answer)
                st.markdown(f"*Model used: {model}*")

            # Now generate real topic from first Q&A
            real_topic = generate_topic(user_input, answer, list(st.session_state.user_chats.keys()))
            st.session_state.current_topic = real_topic

            # Move first message under the new topic
            if real_topic not in st.session_state.user_chats:
                st.session_state.user_chats[real_topic] = []
            st.session_state.user_chats[real_topic].append(chat_entry)
            st.session_state.ai_history = st.session_state.user_chats[real_topic]

            # Save if logged in
            if st.session_state.get("logged_in") and GOOGLE_SHEET_ENABLED:
                save_chat(username, real_topic, user_input, answer)
            else:
                st.session_state["guest_chats"].setdefault(real_topic, []).append(chat_entry)

            # Refresh display with real topic
            st.rerun()
            return

        # Subsequent messages
        topic = st.session_state.current_topic
        if topic not in st.session_state.user_chats:
            st.session_state.user_chats[topic] = []
        st.session_state.user_chats[topic].append(chat_entry)
        st.session_state.ai_history.append(chat_entry)

        # Optional: update topic dynamically after 3 messages
        if len(st.session_state.ai_history) >= 3:
            new_topic = update_topic(st.session_state.ai_history, list(st.session_state.user_chats.keys()))
            if new_topic and new_topic != st.session_state.current_topic:
                st.session_state.current_topic = new_topic

        # Display messages
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            st.markdown(answer)
            st.markdown(f"*Model used: {model}*")

        # Save chat
        if st.session_state.get("logged_in") and GOOGLE_SHEET_ENABLED:
            save_chat(username, st.session_state.current_topic, user_input, answer)
        else:
            st.session_state["guest_chats"].setdefault(topic, []).append(chat_entry)