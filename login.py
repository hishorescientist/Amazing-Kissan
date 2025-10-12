import streamlit as st
import hashlib
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit.components.v1 as components

# ------------------- GOOGLE SHEET -------------------
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

# ------------------- AUTH -------------------
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

# ------------------- LOGIN PAGE -------------------
def app():
    sheet = connect_google_sheet()
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("user", None)

    # -------- STEP 1: Get auto-login param safely --------
    auto_user = st.query_params.get("user")
    if isinstance(auto_user, list):
        auto_user = auto_user[0]

    # Inject JS to copy localStorage -> query param if not logged in
    if not st.session_state.logged_in and not auto_user:
        components.html("""
        <script>
        const user = localStorage.getItem("logged_in_user");
        if (user) {
            const url = new URL(window.location);
            url.searchParams.set("user", user);
            window.location.replace(url.toString());
        }
        </script>
        """, height=0)

    # -------- STEP 2: Auto-login if query param exists --------
    if auto_user and not st.session_state.logged_in:
        users = get_all_users(sheet)
        user = next((u for u in users if str(u.get("username")) == str(auto_user)), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.session_state.page = "Profile"
            st.success(f"✅ Welcome back {user.get('username')}! Restoring session...")
            # Remove query param to prevent loop
            components.html("""
            <script>
            const url = new URL(window.location);
            url.searchParams.delete('user');
            window.history.replaceState({}, document.title, url.toString());
            </script>
            """, height=0)
            st.rerun()

    # -------- STEP 3: Login / Register UI --------
    if not st.session_state.logged_in:
        st.title("🔐 Login / Register")
        login_tab, register_tab = st.tabs(["Login", "Register"])

        with login_tab:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True):
                if not username or not password:
                    st.warning("⚠️ Fill in both fields.")
                else:
                    user = verify_user(sheet, username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.page = "Profile"
                        # Save to localStorage
                        components.html(f"""
                        <script>
                        localStorage.setItem("logged_in_user", "{username}");
                        </script>
                        """, height=0)
                        st.success(f"✅ Welcome {username}! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")

        with register_tab:
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type="password")
            if st.button("Register", use_container_width=True):
                if not new_user or not new_pass:
                    st.error("❌ Fill all fields.")
                else:
                    users = get_all_users(sheet)
                    if any(u.get("username")==new_user.strip() for u in users):
                        st.warning("⚠️ Username already exists.")
                    else:
                        user_dict = {
                            "username": new_user.strip(),
                            "password": hash_password(new_pass.strip()),
                            "name":"",
                            "email":"",
                            "phone":"",
                            "address":"",
                            "dob":""
                        }
                        if save_user(sheet, user_dict):
                            st.success("✅ Registration successful! You can now log in.")

    # -------- STEP 4: Logout --------
    if st.session_state.logged_in and st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        components.html("""<script>localStorage.removeItem("logged_in_user");</script>""", height=0)
        st.success("👋 Logged out successfully.")
        st.rerun()