# login.py
import streamlit as st
import hashlib
import json
import gspread
from datetime import date
from oauth2client.service_account import ServiceAccountCredentials
import re

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

def verify_user(sheet, username_or_email, password):
    """Validate login credentials (accepts username or email)."""
    hashed = hash_password(password)
    users = get_all_users(sheet)

    return next(
        (
            u for u in users
            if (
                (str(u.get("username","")).strip().lower() == username_or_email.strip().lower()
                 or str(u.get("email","")).strip().lower() == username_or_email.strip().lower())
                and u.get("password") == hashed
            )
        ),
        None
    )

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
        st.markdown("""
            <h1 style='text-align:center; color:#2E8B57;'>🔐 Log in / Register</h1>
            <p style='text-align:center; font-size:18px; color:#808080;'>
                You are required to log in every time you enter the app.
            </p>
        """, unsafe_allow_html=True)

        login_tab, register_tab = st.tabs(["Login", "Register"])

        # ---------------- LOGIN TAB ----------------
        with login_tab:
            username_or_email = st.text_input("Username or Email", placeholder="Enter your username or email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            if st.button("Login", use_container_width=True):
                if not username_or_email or not password:
                    st.warning("⚠️ Fill in both fields.")
                else:
                    user = verify_user(sheet, username_or_email, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.page = "Profile"
                        st.success(f"✅ Welcome {user['username']}! Redirecting to your profile...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username/email or password.")

            # ---------------- FORGOT PASSWORD SECTION ----------------
            with st.expander("🔑 Forgot Password?"):
                fp_username = st.text_input("Enter your username or email", key="fp_user")
                fp_phone = st.text_input("Enter your registered mobile number", key="fp_phone", placeholder="+919876543210")

                if st.button("Verify & Reset Password", use_container_width=True):
                    users = get_all_users(sheet)

                    if not fp_username or not fp_phone:
                        st.warning("⚠️ Please enter both username/email and phone number.")
                    else:
                        matched_user = next(
                            (
                                u for u in users
                                if (
                                    (str(u.get("username", "")).strip().lower() == fp_username.strip().lower()
                                     or str(u.get("email", "")).strip().lower() == fp_username.strip().lower())
                                    and str(u.get("phone", "")).strip() == fp_phone.strip()
                                )
                            ),
                            None
                        )

                        if not matched_user:
                            st.error("❌ No matching account found with this username/email and mobile number.")
                        else:
                            st.success(f"✅ Verified! Hello, {matched_user['username']}. You can now set a new password.")
                            new_pass1 = st.text_input("New Password", type="password", key="new_pass1")
                            new_pass2 = st.text_input("Confirm New Password", type="password", key="new_pass2")

                            if st.button("Update Password", use_container_width=True, key="update_pass_btn"):
                                if not new_pass1 or not new_pass2:
                                    st.warning("⚠️ Please fill both password fields.")
                                elif new_pass1 != new_pass2:
                                    st.error("❌ Passwords do not match.")
                                else:
                                    try:
                                        usernames = [u["username"] for u in users]
                                        if matched_user["username"] in usernames:
                                            idx = usernames.index(matched_user["username"]) + 2  # +2 to skip header row
                                            hashed_new = hash_password(new_pass1)
                                            sheet.update_cell(idx, 2, hashed_new)  # Column B = password
                                            st.success("✅ Password updated successfully! Please log in again.")
                                    except Exception as e:
                                        st.error(f"❌ Failed to update password: {e}")

        # ---------------- REGISTER TAB ----------------
        with register_tab:
            new_user = st.text_input("New Username")
            users = get_all_users(sheet)
            if new_user and any(u.get("username") == new_user.strip() for u in users):
                st.warning("⚠️ Username already exists.")

            new_pass = st.text_input("Password", type="password")
            new_re_pass = st.text_input("Confirm Password", type="password")

            if new_pass and new_re_pass and new_pass != new_re_pass:
                st.error("❌ Type same password in both fields.")

            new_email = st.text_input("Email", placeholder="your.email@gmail.com")
            if new_email:
                if "@" not in new_email or "." not in new_email.split("@")[-1]:
                    st.warning("⚠️ Please enter a valid email address")

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
                if not all([new_user, new_pass, new_re_pass, new_email, new_number, new_address, new_dob]):
                    st.error("❌ Fill all fields.")
                elif "@" not in new_email or "." not in new_email.split("@")[-1]:
                    st.error("❌ Invalid email address.")
                else:
                    phone_pattern = re.compile(r'^\+?\d{1,3}?\d{10}$')
                    if not phone_pattern.match(new_number.strip()):
                        st.error("📞 Invalid phone number. Must be 10 digits (optionally with country code, e.g. +911234567890).")
                    else:
                        user_dict = {
                            "username": new_user.strip(),
                            "password": hash_password(new_pass.strip()),
                            "name": new_user.strip(),
                            "email": new_email.strip(),
                            "phone": new_number.strip(),
                            "address": new_address.strip(),
                            "dob": str(new_dob)
                        }
                        if save_user(sheet, user_dict):
                            st.success("✅ Registration successful! You can now log in.")

    else:
        # If already logged in → move to profile
        st.session_state.page = "Profile"
        st.rerun()