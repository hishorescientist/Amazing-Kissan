# ------------------- AI & CHAT HELPERS -------------------
import requests
from datetime import datetime
from langdetect import detect

GOOGLE_SHEET_ENABLED = False
sheet_ai = None

def init_ai_sheet(sheet_name="ai data"):
    """Initialize AI chat sheet connection"""
    global sheet_ai, GOOGLE_SHEET_ENABLED
    sheet_ai = connect_google_sheet(sheet_name)
    GOOGLE_SHEET_ENABLED = sheet_ai is not None
    return sheet_ai

def detect_language_text(text):
    try:
        return detect(text)
    except:
        return "en"

def load_user_chats(username):
    """Load all chats for a username from Google Sheet"""
    if not GOOGLE_SHEET_ENABLED or not sheet_ai:
        return {}
    try:
        rows = sheet_ai.get_all_records()
        user_chats = {}
        for row in rows:
            if str(row.get("username", "")).strip().lower() == username.strip().lower():
                topic = row.get("topic", "Untitled").strip()
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
    """Append a chat to Google Sheet"""
    if not GOOGLE_SHEET_ENABLED or not sheet_ai:
        return
    try:
        sheet_ai.append_row([
            username,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            topic,
            question,
            answer
        ])
    except Exception as e:
        st.warning(f"⚠️ Failed to save chat: {e}")

def generate_topic(question, answer, existing_topics):
    """Generate a short topic from question and answer using Groq API"""
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

def update_topic(messages, existing_topics):
    """Generate a dynamic topic based on last 5 messages"""
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
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=15)
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

    models = ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    for model in models:
        data = {"model": model, "messages": conversation}
        try:
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=30)
            if resp.status_code == 200:
                answer = resp.json()["choices"][0]["message"]["content"].strip()
                return answer, model
        except:
            continue
    return "❌ AI request failed", "None"