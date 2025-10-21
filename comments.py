import gspread
import json
import streamlit as st
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# ---------- GOOGLE CONFIG ----------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# ---------- CONNECT ----------
@st.cache_resource(show_spinner=False)
def connect_comment_sheet():
    """Connect to Google Sheet for comments."""
    try:
        creds_json = st.secrets["google"]["secrets_creds"]
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        client = gspread.authorize(creds)
        return client.open("User").worksheet("Sheet4")
    except Exception as e:
        st.warning(f"⚠️ Could not connect to Comment Sheet: {e}")
        return None


# ---------- ADD COMMENT ----------
def add_comment_gsheet(msg_id, username, text):
    """Add a new comment to the Google Sheet."""
    try:
        sheet = connect_comment_sheet()
        if not sheet:
            st.error("❌ Comment sheet not found.")
            return
        new_row = [
            msg_id,
            username,
            text,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        sheet.append_row(new_row)
    except Exception as e:
        st.error(f"❌ Could not add comment: {e}")


# ---------- LOAD COMMENTS ----------
def load_comments_gsheet(msg_id):
    """Load comments related to a specific message ID."""
    try:
        sheet = connect_comment_sheet()
        if not sheet:
            return []
        data = sheet.get_all_records()
        return [row for row in data if str(row.get("msg_id")) == str(msg_id)]
    except Exception as e:
        st.warning(f"⚠️ Could not load comments: {e}")
        return []