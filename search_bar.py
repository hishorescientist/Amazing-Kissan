# search_bar.py
import streamlit as st

def show_search_bar(user_chats):
    """
    Automatically updates st.session_state.current_topic and ai_history
    based on st.session_state.search_query. No UI elements are shown.
    """
    search_query = st.session_state.get("search_query", "").lower().strip()
    if not search_query:
        return  # Do nothing if input is empty

    # Find the first matching topic
    for topic, chat_list in user_chats.items():
        if search_query in topic.lower() or any(search_query in chat["question"].lower() for chat in chat_list):
            st.session_state.current_topic = topic
            st.session_state.ai_history = chat_list
            break