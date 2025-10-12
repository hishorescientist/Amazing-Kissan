# login.py
import streamlit as st
import streamlit.components.v1 as components
from utils import connect_google_sheet, save_user, verify_user, hash_password, get_all_users

def app():
    """Login / Register Page with auto-login."""
    sheet = connect_google_sheet()
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("user", None)

    # --- STEP 1: Check localStorage for saved login ---
    stored_username = st.query_params.get("login_user", [None])[0] if hasattr(st, "query_params") else None
    if not stored_username:
        # inject JS to read localStorage and reload with query param
        components.html("""
        <script>
        const user = localStorage.getItem("login_user");
        if (user) {
            const url = new URL(window.location);
            url.searchParams.set("login_user", user);
            window.location.replace(url.toString());
        }
        </script>
        """, height=0)

    # --- STEP 2: Auto-login from query param ---
    if stored_username and not st.session_state.logged_in:
        users = get_all_users(sheet)
        user = next((u for u in users if u["username"] == stored_username), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.session_state.page = "Profile"
            st.success(f"✅ Welcome back {user['username']}!")
            # clear query param to avoid loop
            components.html("""
            <script>
            const url = new URL(window.location);
            url.searchParams.delete('login_user');
            window.history.replaceState({}, document.title, url.toString());
            </script>
            """, height=0)
            st.rerun()

    # --- STEP 3: Login / Register UI ---
    if not st.session_state.logged_in:
        st.title("🔐 Login / Register")
        login_tab, register_tab = st.tabs(["Login", "Register"])

        # ---------- LOGIN ----------
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
                        # store in localStorage for next visit
                        components.html(f"""
                        <script>
                        localStorage.setItem("login_user", "{username}");
                        </script>
                        """, height=0)
                        st.success(f"✅ Welcome {user['username']}! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")

        # ---------- REGISTER ----------
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

    # --- STEP 4: Logout Button ---
    if st.session_state.logged_in and st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        components.html("""<script>localStorage.removeItem("login_user");</script>""", height=0)
        st.success("👋 Logged out successfully.")
        st.rerun()