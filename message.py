import streamlit as st
import gspread
import json
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import time
import uuid # Still useful for temporary unique keys if needed

# ---------- GOOGLE SHEET CONFIG (KEEPING AS-IS) ----------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource(show_spinner=False)
def get_client():
    # Assuming st.secrets["google"]["creds"] is correctly defined
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

# ---------- MESSAGE FUNCTIONS (KEEPING AS-IS, but check for case insensitivity) ----------
def load_messages(sheet, chat_type, sender, receiver=None):
    try:
        data = sheet.get_all_records()
        # Note: Converting chat_type to lower() for robustness
        if chat_type.lower() == "public":
            return [m for m in data if m["type"].lower() == "public"]
        else:
            return [
                m for m in data
                if m["type"].lower() == "private" and (
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
    # Public messages now get a simple timestamp ID
    msg_id = f"{sender}_{int(datetime.now().timestamp() * 1000)}" if chat_type.lower() == "public" else "-"
    try:
        # Ensure 'chat_type' is passed as lowercase for consistency with loading
        sheet.append_row([chat_type.lower(), sender, receiver or "-", message, now, "0", msg_id])
    except Exception as e:
        st.error(f"❌ Could not send message: {e}")

def handle_like(msg_id):
    msg_sheet = get_sheet("Messages")
    if msg_sheet:
        try:
            # Note: We must fetch all data to find the row index for gspread
            data = msg_sheet.get_all_records()
            # Start enumeration from 2 because Sheets is 1-indexed and header row is 1
            for i, row in enumerate(data, start=2):
                if str(row.get("id")) == str(msg_id) and row.get("type").lower() == "public":
                    current_likes = int(row.get("likes") or 0)
                    # Column 6 is the 'likes' column
                    msg_sheet.update_cell(i, 6, str(current_likes + 1))
                    return
        except Exception as e:
            st.error(f"⚠️ Could not update likes: {e}")

# ---------- COMMENTS (KEEPING AS-IS) ----------
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

# ---------- MAIN APP (REFACTORED) ----------
def app():
    st.title("💬 Messenger")

    if "user" not in st.session_state or not st.session_state.get("logged_in", False):
        st.warning("⚠️ Please log in first.")
        st.stop()

    user = st.session_state.user.get("username")
    msg_sheet = get_sheet("Messages")
    comment_sheet = get_sheet("Comments")

    if not msg_sheet or not comment_sheet:
        st.error("Cannot connect to required Google Sheets.")
        st.stop()

    # Initialize chat mode states
    if "chat_type" not in st.session_state:
         st.session_state.chat_type = "Public"
    if "private_target" not in st.session_state:
         st.session_state.private_target = None
    
    # --- UI: Chat Mode Selection ---
    current_chat_type = st.radio(
        "Choose Chat Mode:", 
        ["Public", "Private"], 
        index=0 if st.session_state.chat_type == "Public" else 1, 
        horizontal=True
    )

    # Update session state if radio button changed
    if current_chat_type != st.session_state.chat_type:
        st.session_state.chat_type = current_chat_type
        # Clear private target if switching to public
        if current_chat_type == "Public":
            st.session_state.private_target = None

    receiver = None
    if st.session_state.chat_type == "Private":
        users_sheet = get_sheet("Sheet1")
        if users_sheet:
            users = users_sheet.get_all_records()
            names = [u["username"] for u in users if u["username"] != user]
            
            # Handle private target navigation from a public reply button
            if st.session_state.private_target and st.session_state.private_target in names:
                default_index = names.index(st.session_state.private_target)
            else:
                default_index = 0
            
            if names:
                receiver = st.selectbox("Chat with:", names, index=default_index)
                st.session_state.private_target = receiver # Keep target updated
            else:
                st.warning("No other users found to chat with.")
                st.session_state.chat_type = "Public"
                st.stop()
        else:
            st.warning("Could not load user list for private chat.")
            st.session_state.chat_type = "Public"
            st.stop()

    st.divider()

    # --- Display Messages ---
    # Data loading now runs once per script execution (i.e., on every rerun)
    msgs = load_messages(msg_sheet, st.session_state.chat_type, sender=user, receiver=receiver)
    
    st.subheader("🌍 Public Feed" if st.session_state.chat_type == "Public" else f"🔒 Chat with {receiver}")

    # Display the last 50 messages, reversed to show the newest at the bottom
    for i, msg in enumerate(reversed(msgs[-50:])):
        # Use the message ID as the key for stable elements
        msg_id = str(msg.get("id", f"temp-{i}")) 
        
        with st.container(border=True):
            # Display chat message
            if msg["sender"] == user:
                st.chat_message("user").markdown(f"**You:** {msg['message']}")
            else:
                st.chat_message("assistant").markdown(f"**{msg['sender']}:** {msg['message']}")
            st.caption(msg["time"])

            if st.session_state.chat_type == "Public":
                col1, col2, col3 = st.columns([1,2,2])

                # ❤️ Like Button
                with col1:
                    # Key must be stable across runs, use msg_id
                    like_key = f"like-{msg_id}" 
                    if st.button(f"❤️ {msg.get('likes', 0)}", key=like_key):
                        handle_like(msg_id)
                        # We must explicitly rerun after updating the sheet to show the new count
                        st.rerun() 

                # 💬 Comment Input + Post Button
                with col2:
                    comment_input_key = f"cbox-{msg_id}"
                    comment_post_key = f"post-{msg_id}"

                    # Use session state to store the temporary comment input value
                    if comment_input_key not in st.session_state:
                         st.session_state[comment_input_key] = ""

                    st.session_state[comment_input_key] = st.text_input(
                        "💬 Comment", 
                        value=st.session_state[comment_input_key], 
                        key=comment_input_key, 
                        label_visibility="collapsed"
                    )
                    
                    if st.button("Post", key=comment_post_key):
                        comment = st.session_state[comment_input_key].strip()
                        if comment:
                            add_comment(comment_sheet, msg_id, user, comment)
                            st.session_state[comment_input_key] = "" # Clear input
                            st.success("✅ Comment added! Refreshing...")
                            st.rerun()

                # 🔒 Private Reply
                with col3:
                    reply_key = f"reply-{msg_id}"
                    if msg["sender"] != user: # Don't allow replying privately to yourself
                        if st.button("🔒 Private Reply", key=reply_key):
                            st.session_state.chat_type = "Private"
                            st.session_state.private_target = msg["sender"]
                            st.rerun()

                # Display comments
                comments = load_comments(comment_sheet, msg_id)
                if comments:
                    with st.expander("Show Comments"):
                        for c in comments:
                            st.markdown(f"**{c['commenter']}**: {c['comment']} _({c['time']})_")

                st.markdown("---")

    # --- Chat Input for New Messages ---
    # The input should use a stable key, not one that changes on every run
    chat_input_key = "global_chat_input" 
    
    # This function allows us to handle the send action in a callback
    def on_send():
        user_msg = st.session_state[chat_input_key]
        if user_msg:
            send_message(msg_sheet, st.session_state.chat_type, user, user_msg, receiver)
            st.session_state[chat_input_key] = "" # Clear the input after sending
            # Rerun is automatically handled by the input change/form submission

    # Using st.form ensures the inputs are bundled and cleared correctly
    with st.form("chat_form", clear_on_submit=True):
        new_message = st.text_input(
            "Send a message:",
            key=chat_input_key,
            placeholder=f"Send a message to {'Public' if st.session_state.chat_type == 'Public' else receiver}..."
        )
        submitted = st.form_submit_button("Send", on_click=on_send)
        
    # --- Automatic Rerun Polling (Optional but sometimes necessary for chat) ---
    # If you still want to poll for *other* users' new messages without interaction,
    # you can place a single st.rerun call at the end, but be aware of API quotas.
    # The current approach relies on user action (like/comment/send) to trigger the refresh.
    # For a simple chat, relying on user interaction is often enough.

    # If you MUST poll (e.g., to see other user's incoming private messages immediately):
    if st.session_state.chat_type == "Private":
        time.sleep(5)
        st.rerun()

# Run the app (assuming this file is executed as a main module)
if __name__ == '__main__':
    # This part is typically outside the function if running the Streamlit app
    # app()
    pass # Keep it clean for the file block
