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
  
    chat_text = ""  
    for msg in messages[-5:]:  # last 5 messages  
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
# --- Keep sidebar and assistant selectboxes in sync ---  
    if "selected_old_topic" in st.session_state:  
        st.session_state.setdefault("ai_selected_old_topic", st.session_state.selected_old_topic)  
    if "ai_selected_old_topic" in st.session_state:  
        st.session_state.setdefault("selected_old_topic", st.session_state.ai_selected_old_topic)  
    st.title("🌾 AI Assistant for Farmers (All Languages → English)")  
  
    # Session defaults  
    for key in ["ai_mode", "current_topic", "ai_history", "user_chats"]:  
        if key not in st.session_state:  
            st.session_state[key] = None if key=="current_topic" else {} if key=="user_chats" else []  
  
    username = st.session_state.user["username"] if st.session_state.get("logged_in") else "Guest"  
  
    # Load old chats once  
    if st.session_state.get("logged_in") and GOOGLE_SHEET_ENABLED and not st.session_state.user_chats:  
        st.session_state.user_chats = load_user_chats(username)  
  
    # Old chat selection  
    if st.session_state.get("logged_in") and st.session_state.user_chats:  
        topics = list(st.session_state.user_chats.keys())  
  
#        def _set_topic():  
#            st.session_state.selected_old_topic = st.session_state.ai_selected_old_topic  
        st.session_state.current_topic = st.session_state.selected_old_topic  
        st.session_state.ai_history = st.session_state.user_chats.get(st.session_state.current_topic, [])  
"""  
        st.selectbox(  
            "📚 Select a saved chat:",  
            topics[::-1],  
            key="ai_selected_old_topic",  
            on_change=_set_topic  
        )"""  
  
  
    # Display current topic  
    if st.session_state.current_topic:  
        st.subheader(f"📘 Topic: {st.session_state.current_topic}")  
  
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
        if st.session_state.current_topic is None:  
            topic = generate_topic(user_input, "First message", list(st.session_state.user_chats.keys()))  
            st.session_state.current_topic = topic  
        else:  
            topic = st.session_state.current_topic  
  
        # Include previous guest chats if user is guest  
        if not st.session_state.get("logged_in"):  
            guest_memory = []  
            for topic_msgs in st.session_state.get("guest_chats", {}).values():  
                guest_memory.extend(topic_msgs)  
            full_history = guest_memory + st.session_state.ai_history  
        else:  
            full_history = st.session_state.ai_history  
  
        answer, model = ask_ai(user_input, full_history)  
  
        chat_entry = {  
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),  
            "question": user_input,  
            "answer": answer  
        }  
  
        if topic not in st.session_state.user_chats:  
            st.session_state.user_chats[topic] = []  
        st.session_state.user_chats[topic].append(chat_entry)  
        st.session_state.ai_history.append(chat_entry)  
  
        # Optional: update topic dynamically after 3 messages  
        if len(st.session_state.ai_history) >= 3:  
            new_topic = update_topic(st.session_state.ai_history, list(st.session_state.user_chats.keys()))  
            if new_topic:  
                st.session_state.current_topic = new_topic  
  
        # Display messages  
        with st.chat_message("user"):  
            st.markdown(user_input)  
        with st.chat_message("assistant"):  
            st.markdown(answer)  
  
        # Save chat only if user is logged in  
        if st.session_state.get("logged_in") and GOOGLE_SHEET_ENABLED:  
            save_chat(username, st.session_state.current_topic, user_input, answer)  
        else:  
            # Guest chat: do not save permanently, only keep in session  
            st.session_state["guest_chats"] = st.session_state.get("guest_chats", {})  
            topic = st.session_state.current_topic  
            if topic not in st.session_state["guest_chats"]:  
                st.session_state["guest_chats"][topic] = []  
            st.session_state["guest_chats"][topic].append(chat_entry)  
        