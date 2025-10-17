import streamlit as st
import json, uuid, gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from comments import add_comment_gsheet, load_comments_gsheet

# ---------- GOOGLE CONFIG ----------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]


# ---------- CONNECT ----------
@st.cache_resource(show_spinner=False)
def connect_message_sheet():
    """Connect to Google Sheet for messages."""
    try:
        creds_json = st.secrets["google"]["creds"]
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        client = gspread.authorize(creds)
        return client.open("User").worksheet("Sheet3")
    except Exception as e:
        st.warning(f"⚠️ Could not connect to Message Sheet: {e}")
        return None


# ---------- LOAD MESSAGES ----------
def load_messages_gsheet():
    try:
        sheet = connect_message_sheet()
        if not sheet:
            return []
        data = sheet.get_all_records()
        return data
    except Exception as e:
        st.error(f"❌ Error loading messages: {e}")
        return []


# ---------- ADD MESSAGE ----------
def add_message_gsheet(username, text):
    try:
        sheet = connect_message_sheet()
        if not sheet:
            st.error("❌ Message sheet not found.")
            return
        new_row = [
            str(uuid.uuid4()),
            username,
            text,
            0,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        sheet.append_row(new_row)
    except Exception as e:
        st.error(f"❌ Could not send message: {e}")


# ---------- UPDATE LIKES ----------
def update_likes_gsheet(msg_id):
    try:
        sheet = connect_message_sheet()
        if not sheet:
            return
        data = sheet.get_all_records()
        for i, row in enumerate(data, start=2):  # start=2 skips header
            if str(row["id"]) == str(msg_id):
                new_likes = int(row["likes"]) + 1
                sheet.update_cell(i, 4, new_likes)
                break
    except Exception as e:
        st.error(f"❌ Could not update likes: {e}")


# ---------- PAGE ----------
def app():
    st.title("💬 Messenger")

    # ✅ Check login
    if not st.session_state.get("logged_in") or not st.session_state.get("user"):
        st.warning("⚠️ Please log in first.")
        st.stop()

    username = st.session_state.user.get("username", "Anonymous")

    # ---------- Floating Button CSS ----------
    # --- Floating Button CSS ---
st.markdown("""
    <style>
    .floating-btn {
        position: fixed;
        bottom: 25px;
        right: 25px;
        z-index: 999999; /* very high to ensure visibility */
    }

    .floating-btn button {
        background-color: #ff5733;
        color: white;
        border: none;
        padding: 15px 20px;
        border-radius: 50px;
        font-size: 16px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        cursor: pointer;
        transition: all 0.2s ease-in-out;
    }

    .floating-btn button:hover {
        background-color: #ff784e;
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- Floating Button ---
st.markdown('<div class="floating-btn">', unsafe_allow_html=True)
if st.button("✏️ New Message", key="fab"):
    st.session_state.show_post_box = True
st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Toggle Post Box ----------
    if "show_post_box" not in st.session_state:
        st.session_state.show_post_box = False

    if st.query_params.get("show_post") == ["1"]:
        st.session_state.show_post_box = True
        st.experimental_set_query_params()  # clear param

    # ---------- Post Box ----------
    if st.session_state.show_post_box:
        with st.form("post_form", clear_on_submit=True):
            text = st.text_area(f"💭 Message as **{username}**", key="msg_input", height=100)
            submitted = st.form_submit_button("📨 Send")
            if submitted:
                if text.strip():
                    add_message_gsheet(username, text)
                    st.success("✅ Message sent!")
                    st.session_state.show_post_box = False
                    st.rerun()
                else:
                    st.warning("Please type something before sending.")

    st.divider()

    # ---------- Show Messages ----------
    messages = load_messages_gsheet()
    if not messages:
        st.info("No messages yet.")
        return

    for msg in reversed(messages):  # newest first
        msg_id = msg.get("id")
        user_msg = msg.get("user")
        text_msg = msg.get("text", "")
        likes_msg = msg.get("likes", 0)
        time_msg = msg.get("time", "")

        if not msg_id or not text_msg:
            continue  # skip invalid rows

        st.markdown(f"**👤 {user_msg}:** {text_msg}")
        st.caption(f"🕒 {time_msg}")

        # ❤️ Like button
        if st.button(f"❤️ {likes_msg}", key=f"like_{msg_id}"):
            update_likes_gsheet(msg_id)
            st.rerun()

        # 💬 Comments Expander
        with st.expander("💬 Comments", expanded=False):
            comments = load_comments_gsheet(msg_id)
            if comments:
                for c in comments:
                    st.markdown(f"**{c.get('user')}:** {c.get('text','')}")
                    st.caption(f"🕓 {c.get('time','')}")
            else:
                st.caption("No comments yet.")

        # Add Comment
            with st.form(f"comment_form_{msg_id}", clear_on_submit=True):
                comment_text = st.text_area("Reply...", key=f"comment_input_{msg_id}", height=50)
                comment_submitted = st.form_submit_button("Reply")
                if comment_submitted:
                    if comment_text.strip():
                        add_comment_gsheet(msg_id, username, comment_text.strip())
                        st.success("✅ Comment added!")
                        st.rerun()
                    else:
                        st.warning("Please type a comment before submitting.")

        st.divider()