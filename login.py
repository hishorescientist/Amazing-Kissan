#login page
import streamlit as st
import hashlib
import json
import gspread
from datetime import date
from oauth2client.service_account import ServiceAccountCredentials

# --------------------------------------------------------
# 🔑 GOOGLE SHEET SETUP
# --------------------------------------------------------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource(show_spinner=False)
def connect_google_sheet():
    """Connect to Google Sheet using credentials from st.secrets."""
    if "google" not in st.secrets or "creds" not in st.secrets["google"]:
        st.warning("⚠️ Google credentials missing in secrets.")
        return None
    try:
        creds_json = st.secrets["google"]["creds"]
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        client = gspread.authorize(creds)
        return client.open("User").worksheet("Sheet1")
    except Exception as e:
        st.warning(f"⚠️ Could not connect to Google Sheets: {e}")
        return None


# --------------------------------------------------------
# 🔐 AUTH FUNCTIONS
# --------------------------------------------------------
def hash_password(password):
    """Securely hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def get_all_users(sheet):
    """Get all users from the sheet."""
    if not sheet:
        return []
    try:
        return sheet.get_all_records()
    except Exception:
        return []

def save_user(sheet, user):
    """Add or update user details in Google Sheet."""
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
            idx = usernames.index(user["username"]) + 2  # Skip header row
            sheet.update(f"A{idx}:G{idx}", [row])
        else:
            sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"❌ Error saving user: {e}")
        return False

def verify_user(sheet, username, password):
    """Validate login credentials."""
    hashed = hash_password(password)
    users = get_all_users(sheet)
    return next((u for u in users if u.get("username")==username and u.get("password")==hashed), None)


# --------------------------------------------------------
# 🧑 LOGIN PAGE APP FUNCTION
# --------------------------------------------------------
def app():
    """Login and Registration UI."""
    sheet = connect_google_sheet()

    # Initialize session variables safely
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("user", None)

    if not st.session_state.logged_in:
        st.title("🔐 Log in / Register")
        st.markdown("You are required to log in every time you enter the app")
        login_tab, register_tab = st.tabs(["Login", "Register"])

        # ---------------- LOGIN TAB ----------------
        with login_tab:
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            if st.button("Login", use_container_width=True):
                if not username or not password:
                    st.warning("⚠️ Fill in both fields.")
                else:
                    user = verify_user(sheet, username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.page = "Profile"
                        st.success(f"✅ Welcome {user['username']}! Redirecting to your profile...")
                        st.session_state.page = "Profile"
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")

        # ---------------- REGISTER TAB ----------------
        with register_tab:
            new_user = st.text_input("New Username")
            users = get_all_users(sheet)
            if any(u.get("username")==new_user.strip() for u in users):
                st.warning("⚠️ Username already exists.")
            new_pass = st.text_input("Password", type="password")
            new_re_pass = st.text_input("Again type Password", type="password")
            if new_pass != new_re_pass:
                    st.error("type same password on both.")
            new_email = st.text_input("Email", placeholder="your.email@gmail.com")
            st.markdown("""
                <style>
                input[type=tel] {
                    width: 100%;
                    padding: 8px;
                    font-size: 16px;
                    border-radius: 5px;
                    border: 1px solid #ccc;
                }
                </style>
            """, unsafe_allow_html=True)
            new_number = st.text_input("Phone Number", placeholder="+919876543210", key="phone")
            new_address = st.text_input("Address")
            new_dob = st.date_input("Date of Birth", value=date(2000, 1, 1), min_value=date(1900, 1, 1), max_value=date.today())
            
            

            if st.button("Register", use_container_width=True):
                if not new_user or not new_pass or not new_re_pass or not new_email or not new_number or not new_address or not new_dob :
                    st.error("❌ Fill all fields.")
                else:
                    import re
                    phone_pattern = re.compile(r'^\+?\d{1,3}?\d{10}$')
                    if not phone_pattern.match(new_number.strip()):
                        st.error("📞 Invalid phone number. Must be 10 digits (optionally with country code, e.g. +911234567890).")
                    else:
                        user_dict = {
                            "username": new_user.strip(),
                            "password": hash_password(new_pass.strip()),
                            "name": new_user.strip(),
                            "email":new_email.strip(),
                            "phone":new_number.strip(),
                            "address":new_address.strip(),
                            "dob":new_dob.strip()
                        }
                        if save_user(sheet, user_dict):
                            st.success("✅ Registration successful! You can now log in.")

    else:
        # If already logged in → move to profile
        st.session_state.page = "Profile"
        st.rerun()