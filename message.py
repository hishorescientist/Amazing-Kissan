from datetime import datetime
import time
import uuid
import streamlit as st
from streamlit_autorefresh import st_autorefresh  # install via: pip install streamlit-autorefresh

def app():
    st.title("💬 Messenger")

    if "user" not in st.session_state or not st.session_state.get("logged_in", False):
        st.warning("⚠️ Please log in first.")
        st.stop()

    user = st.session_state.user.get("username")
    msg_sheet = get_sheet("Messages")
    comment_sheet = get_sheet("Comments")

    # Handle private reply navigation
    chat_type = st.session_state.get("chat_type", "Public")
    private_target = st.session_state.get("private_target", None)

    chat_type = st.radio(
        "Choose Chat Mode:", 
        ["Public", "Private"], 
        index=0 if chat_type=="Public" else 1, 
        horizontal=True
    )

    receiver = None
    if chat_type == "Private":
        users = get_sheet("Sheet1").get_all_records()
        names = [u["username"] for u in users if u["username"] != user]
        receiver = private_target if private_target in names else st.selectbox("Chat with:", names)

    st.divider()

    # ⏱️ Auto-refresh every 5 seconds
    st_autorefresh(interval=5000, key="chat_refresh")

    # Load messages
    msgs = load_messages(msg_sheet, chat_type, sender=user, receiver=receiver)
    st.subheader("🌍 Public Feed" if chat_type == "Public" else f"🔒 Chat with {receiver}")

    for i, msg in enumerate(msgs[-50:]):
        with st.container():
            msg_key = f"{msg.get('id', uuid.uuid4())}_{i}"
            if msg["sender"] == user:
                st.chat_message("user", key=f"{msg_key}_user").markdown(f"**You:** {msg['message']}")
            else:
                st.chat_message("assistant", key=f"{msg_key}_assistant").markdown(f"**{msg['sender']}:** {msg['message']}")
            st.caption(msg["time"])

            if chat_type == "Public":
                col1, col2, col3 = st.columns([1, 2, 2])

                with col1:
                    if st.button(f"❤️ {msg['likes']}", key=f"like_{msg['id']}"):
                        handle_like(msg["id"])
                        st.rerun()

                with col2:
                    comment_key = f"c_{msg['id']}"
                    comment = st.text_input("💬 Comment", key=comment_key)
                    if st.button("Post", key=f"post_{msg['id']}"):
                        if comment.strip():
                            add_comment(comment_sheet, msg["id"], user, comment.strip())
                            st.success("✅ Comment added!")
                            st.rerun()

                with col3:
                    if st.button("🔒 Private Reply", key=f"reply_{msg['id']}"):
                        st.session_state["page"] = "Messenger"
                        st.session_state["private_target"] = msg["sender"]
                        st.session_state["chat_type"] = "Private"
                        st.experimental_rerun()

                comments = load_comments(comment_sheet, msg["id"])
                for c in comments:
                    st.markdown(f"  💭 *{c['commenter']}*: {c['comment']}  _({c['time']})_")

            st.markdown("---")

    # Input box for new message
    user_msg = st.chat_input("Type a message...")
    if user_msg:
        send_message(msg_sheet, chat_type, user, user_msg, receiver)
        st.rerun()