# profile.py
import streamlit as st
from utils import connect_google_sheet, save_user

def app():
    """User Profile Page"""
    st.title("👤 User Profile")

    # Ensure user is logged in
    if not st.session_state.get("logged_in") or not st.session_state.get("user"):
        st.warning("⚠️ Please log in first.")
        st.session_state.page = "Login"
        st.experimental_rerun()

    user = st.session_state.user
    sheet = connect_google_sheet()
    
    # ---------------- Profile Form ----------------
    with st.form("profile_form", clear_on_submit=False):
        name = st.text_input("Full Name", user.get("name", ""))
        email = st.text_input("Email", user.get("email", ""))
        phone = st.text_input("Phone", user.get("phone", ""))
        address = st.text_area("Address", user.get("address", ""))
        dob = st.date_input("Date of Birth", user.get("dob") or None)

        save_btn = st.form_submit_button("💾 Save Changes")

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

    # ---------------- Logout ----------------
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.page = "Login"
        # Remove token from localStorage
        import streamlit.components.v1 as components
        components.html("""<script>localStorage.removeItem("login_user");</script>""", height=0)
        st.success("👋 Logged out successfully.")
        st.experimental_rerun()