import streamlit as st
import gspread
import json
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import time
import uuid

# ---------- GOOGLE SHEET CONFIG ----------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource(show_spinner=False)
def get_client():
    creds_json = st.secrets["google"]["creds"]
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    return gspread.authorize(creds)

def get_sheet(name):
    try:
        client = get_client()
        return client.open("User").worksheet(name)
    except Exception as e:
        st.error(f"⚠️ Couldn't access sheet '{name}': {e}")
        return None

# ---------- MESSAGE FUNCTIONS ----------
def load_messages(sheet, chat_type, sender, receiver=None):
    try:
        data = sheet.get_all_records()
        if chat_type == "Public":
            return [m for m in data if m["type"] == "public"]
        else:
            return [
                m for m in data
                if m["type"] == "private" and (
                    (m["sender"] == sender and m["receiver"] == receiver)
                    or (m["sender"] == receiver and m["receiver"] == sender)
                )
            ]
    except Exception:
        return []

def send_message(sheet, chat_type, sender, message, receiver=None):
    if not sheet or not message.strip():
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg_id = f"{sender}_{int(datetime.now().timestamp())}" if chat_type == "Public" else "-"
    try:
        sheet.append_row([chat_type.lower(), sender, receiver or "-", message, now, "0", msg_id])
    except Exception as e:
        st.error(f"❌ Could not send message: {e}")

def update_likes(sheet, msg_id):
    try:
        data = sheet.get_all_records()
        for i, row in enumerate(data, start=2):
            if str(row.get("id")) == str(msg_id):
                current = row.get("likes")
                try:
                    current_likes = int(current or 0)
                except ValueError:
                    current_likes = 0
                new_likes = current_likes + 1
                sheet.update_cell(i, 6, str(new_likes))
                return
    except Exception as e:
        st.error(f"⚠️ Could not update likes: {e}")

# ---------- COMMENTS ----------
def load_comments(sheet, msg_id):
    try:
        return [c for c in sheet.get_all_records() if c["message_id"] == msg_id]
    except Exception:
        return []

def add_comment(sheet, msg_id, commenter, comment):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        sheet.append_row([msg_id, commenter, comment, now])
    except Exception as e:
        st.error(f"⚠️ Could not add comment: {e}")

# ---------- MAIN APP ----------
def app():
    st.title("💬 Messenger")

    if "user" not in st.session_state or not st.session_state.get("logged_in", False):
        st.warning("⚠️ Please log in first.")
        st.stop()

    user = st.session_state.user.get("username")
    msg_sheet = get_sheet("Messages")
    comment_sheet = get_sheet("Comments")

    # Handle private reply navigation
    chat_type = st.session_state.get("chat_type", "Public")
    private_target = st.session_state.get("private_target", None)

    chat_type = st.radio("Choose Chat Mode:", ["Public", "Private"], index=0 if chat_type=="Public" else 1, horizontal=True)

    receiver = None
    if chat_type == "Private":
        users = get_sheet("Sheet1").get_all_records()
        names = [u["username"] for u in users if u["username"] != user]
        if private_target and private_target in names:
            receiver = private_target
        else:
            receiver = st.selectbox("Chat with:", names)

    st.divider()

    # Auto-refresh every 5 seconds
    placeholder = st.empty()
    while True:
        with placeholder.container():
            # Load messages
            msgs = load_messages(msg_sheet, chat_type, sender=user, receiver=receiver)
            st.subheader("🌍 Public Feed" if chat_type == "Public" else f"🔒 Chat with {receiver}")

            for i, msg in enumerate(msgs[-50:]):  # use enumerate for unique index
                with st.container():
                    # Chat message display
                    if msg["sender"] == user:
                        st.chat_message("user").markdown(f"**You:** {msg['message']}")
                    else:
                        st.chat_message("assistant").markdown(f"**{msg['sender']}:** {msg['message']}")
                    st.caption(msg["time"])

                    # PUBLIC chat section
                    if chat_type == "Public":
                        col1, col2, col3 = st.columns([1, 2, 2])

                        # ❤️ Like Button
                        with col1:
                            like_key = f"like_{i}"  # unique per message
                            if st.button(f"❤️ {msg['likes']}", key=f"like_{msg['id']}_{uuid.uuid4()}"):
                                handle_like(msg['id'])
                                st.rerun()

                        # 💬 Comment Input + Post Button
                        with col2:
                            comment_input_key = f"cbox_{i}"
                            comment_post_key = f"post_{i}"

                            comment = st.text_input("💬 Comment", key=comment_input_key)
                            if st.button("Post", key=comment_post_key):
                                if comment.strip():
                                    add_comment(comment_sheet, msg["id"], user, comment.strip())
                                    st.success("✅ Comment added!")
                                    st.rerun()

                        # 🔒 Private Reply
                        with col3:
                            reply_key = f"reply_{i}"
                            if st.button("🔒 Private Reply", key=reply_key):
                                st.session_state["page"] = "Messenger"
                                st.session_state["private_target"] = msg["sender"]
                                st.session_state["chat_type"] = "Private"
                                st.experimental_rerun()

                        # Display comments
                        comments = load_comments(comment_sheet, msg["id"])
                        for c in comments:
                            st.markdown(f"  💭 *{c['commenter']}*: {c['comment']}  _({c['time']})_")

                    st.markdown("---")
            # Input box for new messages
            user_msg = st.chat_input("Type a message...")
            if user_msg:
                send_message(msg_sheet, chat_type, user, user_msg, receiver)
                st.rerun()

        time.sleep(5)  # refresh every 5 seconds