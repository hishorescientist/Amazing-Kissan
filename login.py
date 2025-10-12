# login.py
import streamlit as st
from utils import connect_google_sheet, hash_password, save_user, verify_user

# Connect to Google Sheet for users
sheet_users = connect_google_sheet("User")

def app():
    st.title("🔑 Login / Register")

    tab = st.radio("Choose an action:", ["Login", "Register"], horizontal=True)

    if tab == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if not username or not password:
                st.warning("❌ Please enter both username and password.")
            else:
                user = verify_user(sheet_users, username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.page = "Profile"
                    st.session_state.redirect_done = True
                    st.success(f"✅ Welcome back, {user.get('name', username)}!")
                    st.experimental_rerun()
                else:
                    st.error("❌ Invalid username or password.")

    elif tab == "Register":
        st.subheader("Register a new account")
        username = st.text_input("Username", key="reg_username")
        password = st.text_input("Password", type="password", key="reg_password")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        address = st.text_area("Address")
        dob = st.date_input("Date of Birth")

        if st.button("Register"):
            if not username or not password or not name:
                st.warning("❌ Username, password, and name are required.")
            else:
                hashed_password = hash_password(password)
                user_data = {
                    "username": username.strip(),
                    "password": hashed_password,
                    "name": name.strip(),
                    "email": email.strip(),
                    "phone": phone.strip(),
                    "address": address.strip(),
                    "dob": str(dob)
                }
                success = save_user(sheet_users, user_data)
                if success:
                    st.success("✅ Registration successful! Please login.")
                    st.session_state.page = "Login"
                    st.experimental_rerun()
                else:
                    st.error("❌ Registration failed. Try a different username.")