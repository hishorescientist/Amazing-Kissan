# ai_assistant.py
import streamlit as st
import requests
from datetime import datetime
from utils import init_ai_sheet, save_chat

# Initialize AI sheet
ai_sheet = init_ai_sheet()
GOOGLE_SHEET_ENABLED = ai_sheet is not None

# ------------------- HELPER FUNCTIONS -------------------
def ask_ai(question, history):
    """Send question to AI via Groq API"""
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

    # Ensure session defaults
    st.session_state.setdefault("ai_mode", "guest")
    st.session_state.setdefault("current_topic", None)
    st.session_state.setdefault("ai_history", [])
    st.session_state.setdefault("user_chats", {})
    st.session_state.setdefault("guest_chats", {})

    username = st.session_state.user["username"] if st.session_state.get("logged_in") else "Guest"

    # Load old chats once
    if st.session_state.get("logged_in") and GOOGLE_SHEET_ENABLED and not st.session_state.user_chats:
        try:
            rows = ai_sheet.get_all_records()
            user_chats = {}
            for row in rows:
                if row.get("username") == username:
                    topic = row.get("topic", "Untitled")
                    if topic not in user_chats:
                        user_chats[topic] = []
                    user_chats[topic].append({
                        "timestamp": row.get("timestamp", ""),
                        "question": row.get("question", ""),
                        "answer": row.get("answer", "")
                    })
            st.session_state.user_chats = user_chats
        except:
            st.warning("⚠️ Failed to load user chats.")

    # Old chat selection
    if st.session_state.get("logged_in") and st.session_state.user_chats:
        topics = list(st.session_state.user_chats.keys())

        def _set_topic():
            st.session_state.current_topic = st.session_state.ai_selected_old_topic
            st.session_state.ai_history = st.session_state.user_chats.get(st.session_state.current_topic, [])

        st.selectbox(
            "📚 Select a saved chat:",
            topics[::-1],
            key="ai_selected_old_topic",
            on_change=_set_topic
        )

    # Display current topic
    display_topic = st.session_state.current_topic or "New Chat"
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
        # Determine topic
        if st.session_state.current_topic is None:
            st.session_state.current_topic = "New Chat"
        topic = st.session_state.current_topic

        # Get AI response
        answer, model = ask_ai(user_input, st.session_state.ai_history)

        chat_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "question": user_input,
            "answer": answer
        }

        # Append to session
        st.session_state.ai_history.append(chat_entry)
        if st.session_state.get("logged_in"):
            st.session_state.user_chats.setdefault(topic, []).append(chat_entry)
        else:
            st.session_state.guest_chats.setdefault(topic, []).append(chat_entry)

        # Display messages
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            st.markdown(answer)
            st.markdown(f"*Model used: {model}*")

        # Save to Google Sheet if logged in
        if st.session_state.get("logged_in") and GOOGLE_SHEET_ENABLED:
            save_chat(username, topic, user_input, answer)