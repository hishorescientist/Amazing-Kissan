import streamlit as st
import streamlit.components.v1 as components
import json

# ------------------ SAVE STATE ------------------
def save_state(state_dict):
    """
    Save Streamlit session state to browser localStorage.
    """
    try:
        json_data = json.dumps(state_dict)
        components.html(f"""
        <script>
        localStorage.setItem("agri_app_state", JSON.stringify({json_data}));
        </script>
        """, height=0)
    except Exception as e:
        st.warning(f"Save error: {e}")


# ------------------ LOAD STATE ------------------
def load_state():
    """
    Load Streamlit state from browser localStorage.
    (Note: Streamlit cannot directly read JS values; this triggers sync.)
    """
    components.html("""
    <script>
    const saved = localStorage.getItem("agri_app_state");
    if (saved) {{
        const data = JSON.parse(saved);
        window.parent.postMessage({{ type: "RESTORE_STATE", data: data }}, "*");
    }}
    </script>
    """, height=0)

    # This can’t receive JS data directly, but allows prefill from previous sync
    if "local_state_cache" in st.session_state:
        return st.session_state.local_state_cache
    return None


# ------------------ CLEAR STATE ------------------
def clear_state():
    """
    Clears the localStorage data for this app only.
    """
    components.html("""
    <script>
    localStorage.removeItem("agri_app_state");
    alert("🧹 Local data cleared!");
    </script>
    """, height=0)