import gspread
import json
import streamlit as st
from datetime import datetime
import uuid
from oauth2client.service_account import ServiceAccountCredentials

# ---------- SCOPE ----------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# ---------- CONNECT ----------
@st.cache_resource(show_spinner=False)
def connect_gsheet():
    """Connect to Google Sheet using credentials from st.secrets."""
    if "google" not in st.secrets or "creds" not in st.secrets["google"]:
        st.warning("⚠️ Google credentials missing in secrets.")
        return None
    try:
        creds_json = st.secrets["google"]["creds"]
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        client = gspread.authorize(creds)
        # Change these names to your spreadsheet & worksheet
        return client.open("User").worksheet("Sheet3")
    except Exception as e:
        st.warning(f"⚠️ Could not connect to Google Sheets: {e}")
        return None

# ---------- LOAD MESSAGES ----------
def load_messages_gsheet():
    sheet = connect_gsheet()
    if sheet is None:
        return []  # return empty list if connection fails
    try:
        return sheet.get_all_records()  # returns list of dicts
    except Exception as e:
        st.error(f"❌ Error loading messages: {e}")
        return []

# ---------- ADD MESSAGE ----------
def add_message_gsheet(username, text):
    sheet = connect_gsheet()
    if sheet is None:
        return
    try:
        new_row = [
            str(uuid.uuid4()),        # unique message id
            username,                 # user
            text,                     # message text
            0,                        # likes
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # timestamp
        ]
        sheet.append_row(new_row)
    except Exception as e:
        st.error(f"❌ Could not send message: {e}")

# ---------- UPDATE LIKES ----------
def update_likes_gsheet(msg_id):
    sheet = connect_gsheet()
    if sheet is None:
        return
    try:
        data = sheet.get_all_records()
        for i, row in enumerate(data, start=2):  # start=2 because row 1 is header
            if str(row["id"]) == str(msg_id):
                new_likes = int(row["likes"]) + 1
                sheet.update_cell(i, 4, new_likes)  # 'likes' is 4th column
                break
    except Exception as e:
        st.error(f"❌ Could not update likes: {e}")

def load_comments_gsheet(parent_id):
    """Load comments for a specific message from the same sheet or a separate 'Comments' sheet."""
    try:
        sheet = connect_gsheet()
        comments_sheet = sheet  # Or use another worksheet for comments
        data = comments_sheet.get_all_records()
        return [c for c in data if c.get("parent_id") == parent_id]
    except Exception as e:
        st.error(f"❌ Error loading comments: {e}")
        return []

def add_comment_gsheet(parent_id, username, text):
    """Add a comment linked to a parent message."""
    try:
        sheet = connect_gsheet()
        comments_sheet = sheet  # Or a separate worksheet
        new_row = [
            str(uuid.uuid4()),   # unique comment id
            parent_id,           # parent message id
            username,
            text,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        comments_sheet.append_row(new_row)
    except Exception as e:
        st.error(f"❌ Could not add comment: {e}")