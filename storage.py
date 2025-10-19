import streamlit as st
import json
import streamlit.components.v1 as components

# ✅ Save state to user's browser (localStorage)
def save_state(state_data):
    js_code = f"""
    <script>
    const data = {json.dumps(state_data)};
    localStorage.setItem("agri_app_state", JSON.stringify(data));
    </script>
    """
    components.html(js_code, height=0)

# ✅ Load state from browser
def load_state():
    load_js = """
    <script>
    const saved = localStorage.getItem("agri_app_state");
    if (saved) {{
        const data = JSON.parse(saved);
        window.parent.postMessage({{type: 'STATE_RESTORE', data: data}}, "*");
    }}
    </script>
    """
    components.html(load_js, height=0)
    return None  # Loaded asynchronously by JS

# ✅ Clear user’s local storage (on logout)
def clear_state():
    clear_js = """
    <script>
    localStorage.removeItem("agri_app_state");
    </script>
    """
    components.html(clear_js, height=0)