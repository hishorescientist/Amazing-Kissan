import streamlit as st
import json, uuid, gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
# Assuming 'comments' is a separate file you have
# from comments import add_comment_gsheet, load_comments_gsheet 

# If you don't have the comments file, mock them to run the code
def add_comment_gsheet(msg_id, user, text):
    st.info(f"Mock: Adding comment by {user} to {msg_id}: {text}")
def load_comments_gsheet(msg_id):
    return [{'user': 'TestUser', 'text': 'Great post!', 'time': '2025-10-17 10:00:00'}]

# ---------- GOOGLE CONFIG ----------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# ---------- CONNECT ----------
@st.cache_resource(show_spinner=False)
def connect_message_sheet():
    """Connect to Google Sheet for messages."""
    # NOTE: This function requires st.secrets to be configured
    try:
        creds_json = st.secrets["google"]["creds"]
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        client = gspread.authorize(creds)
        # Use a placeholder sheet name if the actual one isn't available for testing
        return client.open("User").worksheet("Sheet3") 
    except Exception as e:
        # st.warning(f"⚠️ Could not connect to Message Sheet: {e}")
        # MOCK RETURN FOR TESTING WITHOUT GOOGLE SHEETS
        class MockSheet:
            def get_all_records(self):
                # Mock data structure matching your app logic
                return [
                    {'id': '1', 'user': 'Alice', 'text': 'Hello world!', 'likes': 5, 'time': '2025-10-17 10:00:00'},
                    {'id': '2', 'user': 'Bob', 'text': 'Streamlit is fun.', 'likes': 1, 'time': '2025-10-17 10:05:00'},
                ]
            def append_row(self, row):
                st.info(f"Mock: Appending row: {row}")
            def update_cell(self, row, col, val):
                st.info(f"Mock: Updating cell ({row}, {col}) with value: {val}")
        
        if st.secrets.get("google"):
             st.warning(f"⚠️ Could not connect to Message Sheet: {e}")
             return None
        return MockSheet() # Return mock sheet if secrets not configured


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
        # gspread uses 1-based indexing for rows/cols
        # get_all_records skips header, so the first record is row 2
        for i, row in enumerate(data, start=2):  
            # Assuming 'id' is the first column and 'likes' is the fourth column (index 3)
            if str(row.get("id")) == str(msg_id):
                new_likes = int(row.get("likes", 0)) + 1
                # Column 4 for 'likes' (index 3 in a 0-based list)
                sheet.update_cell(i, 4, new_likes) 
                break
    except Exception as e:
        st.error(f"❌ Could not update likes: {e}")


# ---------- PAGE ----------
def app():
    st.title("💬 Messenger")

    # MOCK LOGIN for testing if not set
    if "logged_in" not in st.session_state:
         st.session_state.logged_in = True
         st.session_state.user = {"username": "DemoUser"}
         
    # ✅ Check login
    if not st.session_state.get("logged_in") or not st.session_state.get("user"):
        st.warning("⚠️ Please log in first.")
        st.stop()

    username = st.session_state.user.get("username", "Anonymous")

    # ---------- FLOATING BUTTON HACK ----------
    # 1. Inject CSS for the floating effect
    st.markdown("""
    <style>
    /* Target the container of the Streamlit button */
    .stButton > button {
        background-color: #FF5733; 
        color: white;
        border: none;
        padding: 14px 22px;
        border-radius: 50px;
        font-size: 16px;
        cursor: pointer;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #e64523;
    }
    
    /* Create a fixed-position container for the button */
    .floating-container {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 2. Place the Streamlit button inside a markdown div with the fixed class
    st.markdown('<div class="floating-container">', unsafe_allow_html=True)
    
    # 3. Native Streamlit button with a callback or logic
    # Set the state variable directly when the button is pressed
    if st.button("✏️ New Message", key="floating_post_btn"):
        st.session_state.show_post_box = True
        st.rerun() # Force a rerun to show the post box immediately
        
    st.markdown('</div>', unsafe_allow_html=True)
    # ---------- END FLOATING BUTTON HACK ----------

    # ---------- Toggle Post Box ----------
    if "show_post_box" not in st.session_state:
        st.session_state.show_post_box = False

    # Note: Removed the st.query_params logic as it's no longer needed

    # ---------- Post Box ----------
    if st.session_state.show_post_box:
        with st.form("post_form", clear_on_submit=True):
            text = st.text_area(f"💭 Message as **{username}**", key="msg_input", height=100)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submitted = st.form_submit_button("📨 Send")
            with col2:
                 # Add a button to hide the box
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.show_post_box = False
                    st.rerun()

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

    # Create a simple mapping to prevent redundant calls to update_likes_gsheet
    # This is a common pattern for handling button clicks inside loops
    if 'liked_message' not in st.session_state:
        st.session_state.liked_message = None

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

        # ❤️ Like button: Check if this button was clicked
        if st.button(f"❤️ {likes_msg}", key=f"like_{msg_id}"):
             # Store the ID of the message that was liked
             st.session_state.liked_message = msg_id
             st.rerun()
             
        # Process the like after the loop if a button was clicked
        if st.session_state.liked_message == msg_id:
            update_likes_gsheet(msg_id)
            st.session_state.liked_message = None # Clear the state
            # Note: This rerun is already handled by the button click above
            
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

# To run the code:
# if __name__ == "__main__":
#     app()