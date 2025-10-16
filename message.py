import streamlit as st
import gspread
import json
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import time

# ---------- GOOGLE SHEET CONFIG ----------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource(show_spinner=False)
def get_client():
    """Initializes and authorizes the gspread client."""
    creds_json = st.secrets["google"]["creds"]
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    return gspread.authorize(creds)

def get_sheet(name):
    """Opens a specific worksheet."""
    try:
        client = get_client()
        # NOTE: Assumes the spreadsheet is named "User"
        return client.open("User").worksheet(name)
    except Exception as e:
        st.error(f"⚠️ Couldn't access sheet '{name}': {e}")
        return None

# ---------- MESSAGE FUNCTIONS ----------
def load_messages(sheet, chat_type, sender, receiver=None):
    """Loads public or private messages from the sheet."""
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
    """Appends a new message row to the sheet."""
    if not sheet or not message.strip():
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg_id = f"{sender}_{int(datetime.now().timestamp())}"
    try:
        # Note: Columns are: type, sender, receiver, message, time, likes, id
        sheet.append_row([chat_type.lower(), sender, receiver or "-", message, now, "0", msg_id])
    except Exception as e:
        st.error(f"❌ Could not send message: {e}")

def handle_like(msg_id):
    """Increments the like count for a specific message ID."""
    msg_sheet = get_sheet("Messages")
    if msg_sheet:
        try:
            data = msg_sheet.get_all_records()
            # Iterate through data to find the row index (gspread is 1-indexed, and rows start after header)
            for i, row in enumerate(data, start=2): 
                if str(row.get("id")) == str(msg_id):
                    # Column 6 is 'likes'
                    current_likes = int(row.get("likes") or 0)
                    msg_sheet.update_cell(i, 6, str(current_likes + 1))
                    return
        except Exception as e:
            st.error(f"⚠️ Could not update likes: {e}")

# ---------- COMMENTS ----------
def load_comments(sheet, msg_id):
    """Loads comments for a specific message."""
    try:
        # Note: Assumes Comments sheet columns are: message_id, commenter, comment, time
        return [c for c in sheet.get_all_records() if c["message_id"] == msg_id]
    except Exception:
        return []

def add_comment(sheet, msg_id, commenter, comment):
    """Adds a new comment row to the sheet."""
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

    # Initialize chat state
    if "chat_type" not in st.session_state:
        st.session_state["chat_type"] = "Public"
    if "private_target" not in st.session_state:
        st.session_state["private_target"] = None

    # Handle chat type selection
    chat_type = st.radio(
        "Choose Chat Mode:",
        ["Public", "Private"],
        index=0 if st.session_state.chat_type == "Public" else 1,
        horizontal=True
    )
    st.session_state["chat_type"] = chat_type # Update session state

    receiver = None
    if chat_type == "Private":
        # Note: Assumes user list is in "Sheet1" and has a "username" column
        users = get_sheet("Sheet1").get_all_records()
        names = [u["username"] for u in users if u["username"] != user]
        
        # Determine current selection index
        current_target = st.session_state.private_target if st.session_state.private_target in names else (names[0] if names else None)
        
        if names:
            receiver = st.selectbox("Chat with:", names, index=names.index(current_target))
            st.session_state["private_target"] = receiver
        else:
            st.warning("No other users found to chat with.")
            receiver = None

    st.divider()

    # Auto-refresh loop: Note: This is a blocking pattern in Streamlit and will cause a 5s delay on ALL interactions.
    # It is kept here as it was part of the original requirement for auto-refresh.
    placeholder = st.empty()
    while True:
        with placeholder.container():
            # Load and display messages
            msgs = load_messages(msg_sheet, chat_type, sender=user, receiver=receiver)
            
            # Show the most recent 50 messages
            st.subheader("🌍 Public Feed" if chat_type == "Public" and msg_sheet else f"🔒 Chat with {receiver}")

            if not msg_sheet:
                 st.error("Cannot display messages without a valid 'Messages' sheet connection.")
            elif chat_type == "Private" and not receiver:
                 st.info("Select a user to start a private chat.")
            else:
                for i, msg in enumerate(msgs[-50:]):
                    with st.container():
                        # --- CRITICAL FIX: Generate a stable, unique key using only the message ID ---
                        # The msg ID is unique and stable (sender_timestamp).
                        # The index 'i' (of the 50 displayed messages) is volatile and caused the key error.
                        msg_id = str(msg.get("id", f"fallback_{msg['sender']}_{i}")) 
                        # --------------------------------------------------------------------------
                        
                        sender_name = "You" if msg["sender"] == user else msg["sender"]

                        st.chat_message("user" if msg["sender"] == user else "assistant").markdown(
                            f"**{sender_name}:** {msg['message']}"
                        )
                        st.caption(msg["time"])

                        if chat_type == "Public":
                            col1, col2, col3 = st.columns([1, 2, 2])

                            with col1:
                                # Key uses only msg_id
                                if st.button(f"❤️ {msg.get('likes', 0)}", key=f"like_{msg_id}"):
                                    handle_like(msg["id"])
                                    st.rerun()

                            with col2:
                                # Key uses only msg_id
                                comment = st.text_input("💬 Comment", key=f"cbox_{msg_id}")
                                # Key uses only msg_id (added _btn suffix to avoid clash with text input)
                                if st.button("Post", key=f"post_{msg_id}_btn"): 
                                    if comment.strip():
                                        add_comment(comment_sheet, msg["id"], user, comment.strip())
                                        st.success("✅ Comment added!")
                                        st.rerun()

                            with col3:
                                # Key uses only msg_id
                                if st.button("🔒 Private Reply", key=f"reply_{msg_id}"):
                                    st.session_state["chat_type"] = "Private"
                                    st.session_state["private_target"] = msg["sender"]
                                    st.rerun() # Use st.rerun()

                            # Display comments
                            comments = load_comments(comment_sheet, msg["id"])
                            for c in comments:
                                st.markdown(f"  💭 *{c['commenter']}*: {c['comment']}  _({c['time']})_")

                        st.markdown("---")

            # Message Input
            user_msg = st.chat_input("Type a message...")
            if user_msg:
                send_message(msg_sheet, chat_type, user, user_msg, receiver)
                st.rerun()

        # The blocking refresh mechanism from the original code
        time.sleep(5)
