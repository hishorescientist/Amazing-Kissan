import streamlit as st
import json
import gspread
from datetime import date
from oauth2client.service_account import ServiceAccountCredentials

# --------------------------------------------------------
# 🌐 GOOGLE SHEET CONNECTION
# --------------------------------------------------------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

def connect_google_sheet(sheet_name="Sheet1"):
    """Connect to Google Sheet."""
    try:
        creds_json = st.secrets["google"]["secrets_creds"]
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        client = gspread.authorize(creds)
        return client.open("User").worksheet(sheet_name)
    except Exception as e:
        st.warning(f"⚠️ Could not connect to Google Sheet: {e}")
        return None


def get_all_users(sheet):
    try:
        return sheet.get_all_records()
    except:
        return []


def save_user(sheet, user):
    """Save or update user details in Google Sheet."""
    if not sheet:
        return False
    users = get_all_users(sheet)
    usernames = [u["username"] for u in users]
    row = [
        user.get("username", ""),
        user.get("password", ""),
        user.get("name", ""),
        user.get("email", ""),
        user.get("phone", ""),
        user.get("address", ""),
        user.get("dob", "")
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


# --------------------------------------------------------
# 👤 PROFILE PAGE
# --------------------------------------------------------
def clear_url_params():
    """Clear URL query parameters in browser."""
    st.markdown(
        """
        <script>
        if(window.history.replaceState) {
            const clean_url = window.location.protocol + "//" + window.location.host + window.location.pathname;
            window.history.replaceState({}, document.title, clean_url);
        }
        </script>
        """,
        unsafe_allow_html=True
    )


def app():
    """User Profile Page."""
    st.title("👤 User Profile")

    # Ensure user is logged in
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("⚠️ Please log in first.")
        st.session_state.page = "Login"
        st.rerun()

    # Load current user info
    user = st.session_state.get("user", {})
    sheet = connect_google_sheet()

    # ----------------------------------------------------
    # ✏️ Editable Profile Fields
    # ----------------------------------------------------
    with st.form("profile_form", clear_on_submit=False):
        name = st.text_input("Full Name", user.get("name", ""))
        email = st.text_input("Email", user.get("email", ""))
        phone = st.text_input("Phone", user.get("phone", ""))
        address = st.text_area("Address", user.get("address", ""))
        dob = st.date_input(
            "Date of Birth",
            value=user.get("dob", date(2000, 1, 1)),
            min_value=date(1900, 1, 1),
            max_value=date.today()
        )

        save_btn = st.form_submit_button("💾 Save Changes")

    # ----------------------------------------------------
    # 💾 Save Button Handler
    # ----------------------------------------------------
    if save_btn:
        updated_user = {
            "username": user.get("username"),
            "password": user.get("password"),
            "name": name,
            "email": email,
            "phone": phone,
            "address": address,
            "dob": str(dob)
        }

        if save_user(sheet, updated_user):
            st.session_state.user = updated_user
            st.success("✅ Profile updated successfully!")

    # ----------------------------------------------------
    # 🚪 Logout Button
    # ----------------------------------------------------
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        # Clear all relevant session data
        keys_to_clear = [
            "logged_in", "user", "page",
            "ai_history", "ai_mode", "current_topic", "user_chats",
            "selected_old_topic", "ai_selected_old_topic"
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

        st.success("✅ Logged out successfully.")
        st.session_state.page = "Login"

        # Clear URL parameters safely
        clear_url_params()

        # Rerun to refresh page state
        st.rerun()