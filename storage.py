# storage.py
import json
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

# Key used in browser localStorage
STORAGE_KEY = "agri_local_state"

def save_state(data: dict):
    """
    Save app state to the user's browser localStorage.
    """
    try:
        js_code = f"window.localStorage.setItem('{STORAGE_KEY}', '{json.dumps(data)}');"
        streamlit_js_eval(js_expressions=js_code, key="saveLocalStorage")
    except Exception as e:
        st.warning(f"Could not save local state: {e}")

def load_state() -> dict:
    """
    Load app state from the user's browser localStorage.
    """
    try:
        raw = streamlit_js_eval(
            js_expressions=f"window.localStorage.getItem('{STORAGE_KEY}')",
            key="loadLocalStorage",
            want_output=True
        )
        if raw:
            return json.loads(raw)
    except Exception as e:
        st.warning(f"Could not load local state: {e}")
    return {}

def clear_state():
    """
    Clear user's saved local state from browser localStorage.
    """
    try:
        streamlit_js_eval(
            js_expressions=f"window.localStorage.removeItem('{STORAGE_KEY}');",
            key="clearLocalStorage"
        )
        st.success("Local data cleared! Refresh the page to start fresh.")
    except Exception as e:
        st.warning(f"Could not clear local state: {e}")