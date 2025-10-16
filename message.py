import streamlit as st
import uuid
from streamlit_autorefresh import st_autorefresh  # pip install streamlit-autorefresh

def app():
    st.title("💬 Messenger")

    # --- Auth check ---
    if "user" not in st.session_state or not st.session_state.get("logged_in", False):
        st.warning("⚠️ Please log in first.")
        st.stop()

    user = st.session_state.user.get("username")
    msg_sheet = get_sheet("Messages")
    comment_sheet = get_sheet("Comments")

    # --- Chat mode selection ---
    chat_type = st.session_state.get("chat_type", "Public")
    private_target = st.session_state.get("private_target", None)

    chat_type = st.radio(
        "Choose Chat Mode:", 
        ["Public", "Private"], 
        index=0 if chat_type == "Public" else 1,
        horizontal=True
    )

    receiver = None
    if chat_type == "Private":
        users = get_sheet("Sheet1").get_all_records()
        names = [u["username"] for u in users if u["username"] != user]
        receiver = private_target if private_target in names else st.selectbox("Chat with:", names)

    st.divider()

    # --- Auto refresh every 5 seconds ---
    st_autorefresh(interval=5000, key="chat_refresh")

    # --- Load messages ---
    msgs = load_messages(msg_sheet, chat_type, sender=user, receiver=receiver)
    st.subheader("🌍 Public Feed" if chat_type == "Public" else f"🔒 Chat with {receiver}")

    # --- Display messages ---
    for i, msg in enumerate(msgs[-50:]):
        msg_id = msg.get("id", f"msg_{i}")
        with st.container():
            role = "user" if msg["sender"] == user else "assistant"
            st.chat_message(role, key=f"msg_{msg_id}").markdown(
                f"**{'You' if msg['sender']==user else msg['sender']}:** {msg['message']}"
            )
            st.caption(msg["time"])

            # --- Only for public chats ---
            if chat_type == "Public":
                col1, col2, col3 = st.columns([1, 2, 2])

                with col1:
                    if st.button(f"❤️ {msg['likes']}", key=f"like_{msg_id}"):
                        handle_like(msg["id"])
                        st.rerun()

                with col2:
                    comment = st.text_input("💬 Comment", key=f"comment_{msg_id}")
                    if st.button("Post", key=f"post_{msg_id}"):
                        if comment.strip():
                            add_comment(comment_sheet, msg["id"], user, comment.strip())
                            st.success("✅ Comment added!")
                            st.rerun()

                with col3:
                    if st.button("🔒 Private Reply", key=f"reply_{msg_id}"):
                        st.session_state["page"] = "Messenger"
                        st.session_state["private_target"] = msg["sender"]
                        st.session_state["chat_type"] = "Private"
                        st.experimental_rerun()

                # --- Show comments ---
                comments = load_comments(comment_sheet, msg["id"])
                for c in comments:
                    st.markdown(f"  💭 *{c['commenter']}*: {c['comment']}  _({c['time']})_")

            st.markdown("---")

    # --- Chat input ---
    user_msg = st.chat_input("Type a message...")
    if user_msg:
        send_message(msg_sheet, chat_type, user, user_msg, receiver)
        st.rerun()