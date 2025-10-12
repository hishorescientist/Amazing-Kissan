import streamlit as st
import os
import json
from login import connect_google_sheet, save_user

# --------------------------------------------------------
# 👤 PROFILE PAGE
# --------------------------------------------------------
LOG_FILE = "user_log.json"  # Same name used in main.py

def clear_log():
    """Delete saved login info for security"""
    if os.path.exists(LOG_FILE):
        try:
            os.remove(LOG_FILE)
        except Exception as e:
            st.warning(f"⚠️ Could not remove log file: {e}")

def app():
    """User Profile Page."""
    st.title("👤 User Profile")

    # Ensure session and login state
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
        dob = st.date_input("Date of Birth", user.get("dob") or None)

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
        # Clear session state
        for key in ["logged_in", "user", "current_topic", "ai_history", "user_chats", "guest_chats"]:
            if key in st.session_state:
                del st.session_state[key]

        # Delete auto-login log file
        clear_log()

        # Redirect to login page
        st.session_state.page = "Login"
        st.success("✅ Logged out successfully.")
        st.rerun()