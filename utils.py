# utils.py
import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import hashlib

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# ------------------- GOOGLE SHEET -------------------
def connect_google_sheet(sheet_name="Sheet1"):
    """Connect to a Google Sheet."""
    try:
        creds_json = st.secrets["google"]["creds"]
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        client = gspread.authorize(creds)
        return client.open("User").worksheet(sheet_name)
    except Exception as e:
        st.warning(f"⚠️ Could not connect to Google Sheet: {e}")
        return None

# ------------------- PASSWORD -------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_all_users(sheet):
    try:
        return sheet.get_all_records()
    except:
        return []

def save_user(sheet, user):
    if not sheet:
        return False
    users = get_all_users(sheet)
    usernames = [u["username"] for u in users]
    row = [
        user.get("username",""),
        user.get("password",""),
        user.get("name",""),
        user.get("email",""),
        user.get("phone",""),
        user.get("address",""),
        user.get("dob","")
    ]
    try:
        if user["username"] in usernames:
            idx = usernames.index(user["username"]) + 2
            sheet.update(f"A{idx}:G{idx}", [row])
        else:
            sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"❌ Error saving user: {e}")
        return False

def verify_user(sheet, username, password):
    hashed = hash_password(password)
    users = get_all_users(sheet)
    return next((u for u in users if u.get("username")==username and u.get("password")==hashed), None)