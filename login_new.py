import streamlit as st
import hashlib
import json
import gspread
from datetime import date
from oauth2client.service_account import ServiceAccountCredentials
import re
import smtplib
from email.mime.text import MIMEText
import random

# --------------------------------------------------------
# 🔑 GOOGLE SHEET SETUP
# --------------------------------------------------------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource(show_spinner=False)
def connect_google_sheet():
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
    return hashlib.sha256(password.encode()).hexdigest()

def get_all_users(sheet):
    if not sheet:
        return []
    try:
        return sheet.get_all_records()
    except Exception:
        return []

def save_user(sheet, user):
    if not sheet:
        return False
    users = get_all_users(sheet)
    usernames = [u.get("username") for u in users]
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

def verify_user(sheet, username_or_email, password):
    hashed = hash_password(password)
    users = get_all_users(sheet)
    return next(
        (
            u for u in users
            if (
                (str(u.get("username") or "").strip().lower() == username_or_email.strip().lower()
                 or str(u.get("email") or "").strip().lower() == username_or_email.strip().lower())
                and u.get("password") == hashed
            )
        ),
        None
    )

# --------------------------------------------------------
# ✉️ EMAIL FUNCTIONS
# --------------------------------------------------------
def send_email(receiver_email, subject, message):
    sender_email = st.secrets["email"]["address"]
    sender_pass = st.secrets["email"]["password"]
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_pass)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")
        return False

# --------------------------------------------------------
# 🧑 LOGIN PAGE APP FUNCTION
# --------------------------------------------------------
def app():
    sheet = connect_google_sheet()
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("show_forgot", False)
    st.session_state.setdefault("fp_stage", "email")
    st.session_state.setdefault("fp_code", None)
    st.session_state.setdefault("fp_user", None)

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
            if not st.session_state.show_forgot:
                username_or_email = st.text_input("Username or Email", placeholder="Enter your username or email", key="login_user")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")

                if st.button("Login", use_container_width=True):
                    if not username_or_email or not password:
                        st.warning("⚠️ Fill in both fields.")
                    else:
                        user = verify_user(sheet, username_or_email, password)
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user = user
                            st.session_state.page = "Profile"
                            st.success(f"✅ Welcome {user['username']}! Redirecting...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username/email or password.")

                # clickable small forgot password text
                st.markdown(
                    "<p style='text-align:right; font-size:14px;'>"
                    "<a href='#' style='color:#1E90FF; text-decoration:none;' "
                    "onClick='window.location.reload()'>Forgot Password?</a></p>",
                    unsafe_allow_html=True
                )

                # Button to open forgot password section (Streamlit event)
                if st.button("Forgot Password", use_container_width=True):
                    st.session_state.show_forgot = True
                    st.rerun()

            else:
                # ---------------- FORGOT PASSWORD WORKFLOW ----------------
                st.markdown("### 🔑 Forgot Password")

                # Step 1: Email input
                if st.session_state.fp_stage == "email":
                    fp_email = st.text_input("Enter your registered email", key="fp_email")
                    if st.button("Send Verification Code", use_container_width=True, key="fp_send_code"):
                        users = get_all_users(sheet)
                        matched_user = next(
                            (u for u in users if str(u.get("email") or "").strip().lower() == fp_email.strip().lower()),
                            None
                        )
                        if not matched_user:
                            st.error("❌ No account found with this email.")
                        else:
                            code = random.randint(100000, 999999)
                            st.session_state.fp_code = str(code)
                            st.session_state.fp_user = matched_user
                            if send_email(fp_email, "Password Reset Code", f"Your verification code is: {code}"):
                                st.session_state.fp_stage = "code"
                                st.success("✅ Verification code sent! Check your email.")
                                st.rerun()

                # Step 2: Code entry
                elif st.session_state.fp_stage == "code":
                    entered_code = st.text_input("Enter Verification Code", key="fp_entered_code")
                    if st.button("Verify Code", use_container_width=True, key="fp_verify_code"):
                        if entered_code == st.session_state.fp_code:
                            st.session_state.fp_stage = "reset"
                            st.success("✅ Code verified! Now set a new password.")
                            st.rerun()
                        else:
                            st.error("❌ Invalid verification code.")

                # Step 3: Reset password
                elif st.session_state.fp_stage == "reset":
                    new_pass1 = st.text_input("New Password", type="password", key="fp_new_pass1")
                    new_pass2 = st.text_input("Confirm New Password", type="password", key="fp_new_pass2")
                    if st.button("Update Password", use_container_width=True, key="fp_update_btn"):
                        if not new_pass1 or not new_pass2:
                            st.warning("⚠️ Fill both password fields.")
                        elif new_pass1 != new_pass2:
                            st.error("❌ Passwords do not match.")
                        else:
                            try:
                                users = get_all_users(sheet)
                                usernames = [u.get("username") for u in users]
                                if st.session_state.fp_user["username"] in usernames:
                                    idx = usernames.index(st.session_state.fp_user["username"]) + 2
                                    hashed_new = hash_password(new_pass1)
                                    sheet.update_cell(idx, 2, hashed_new)
                                    st.success("✅ Password updated! Please log in again.")
                                    # Reset state
                                    st.session_state.fp_stage = "email"
                                    st.session_state.fp_code = None
                                    st.session_state.fp_user = None
                                    st.session_state.show_forgot = False
                                    st.rerun()
                            except Exception as e:
                                st.error(f"❌ Failed to update password: {e}")

                # Back button
                if st.button("⬅️ Back to Login", use_container_width=True):
                    st.session_state.show_forgot = False
                    st.session_state.fp_stage = "email"
                    st.rerun()

        # ---------------- REGISTER TAB ----------------
        with register_tab:
            new_user = st.text_input("New Username", key="reg_user")
            users = get_all_users(sheet)
            if any(u.get("username") == new_user.strip() for u in users):
                st.warning("⚠️ Username already exists.")

            new_pass = st.text_input("Password", type="password", key="reg_pass")
            new_re_pass = st.text_input("Confirm Password", type="password", key="reg_repass")

            if new_pass != new_re_pass and new_pass and new_re_pass:
                st.error("❌ Type same password in both fields.")

            new_email = st.text_input("Email", placeholder="your.email@gmail.com", key="reg_email")
            if new_email and ("@" not in new_email or "." not in new_email.split("@")[-1]):
                st.warning("⚠️ Please enter a valid email address")

            new_number = st.text_input("Phone Number", placeholder="+919876543210", key="reg_phone")
            new_address = st.text_input("Address", key="reg_address")
            new_dob = st.date_input("Date of Birth", value=date(2000, 1, 1),
                                    min_value=date(1900, 1, 1), max_value=date.today(), key="reg_dob")

            if st.button("Register", use_container_width=True, key="reg_btn"):
                if not all([new_user, new_pass, new_re_pass, new_email, new_number, new_address, new_dob]):
                    st.error("❌ Fill all fields.")
                else:
                    phone_pattern = re.compile(r'^\+?\d{1,3}?\d{10}$')
                    if not phone_pattern.match(new_number.strip()):
                        st.error("📞 Invalid phone number.")
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
        st.session_state.page = "Profile"
        st.rerun()