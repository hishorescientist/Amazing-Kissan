import streamlit as st
import json
import streamlit.components.v1 as components

LOCAL_KEY = "agri_app_state"

# --- JavaScript bridge ---
def inject_local_storage_bridge():
    components.html(f"""
        <script>
        const stateKey = '{LOCAL_KEY}';

        // Listen for messages from Streamlit (Python → JS)
        window.addEventListener("message", (event) => {{
            if (event.data.type === "SAVE_STATE") {{
                localStorage.setItem(stateKey, JSON.stringify(event.data.data));
            }}
            if (event.data.type === "CLEAR_STATE") {{
                localStorage.removeItem(stateKey);
            }}
        }});

        // On page load, send stored data (JS → Python)
        const saved = localStorage.getItem(stateKey);
        if (saved) {{
            const parsed = JSON.parse(saved);
            window.parent.postMessage({{ type: "RESTORE_STATE", data: parsed }}, "*");
        }}
        </script>
    """, height=0)


# --- Save Streamlit state to browser localStorage ---
def save_state(state_dict):
    data_json = json.dumps(state_dict)
    components.html(f"""
        <script>
        window.postMessage({{
            type: "SAVE_STATE",
            data: {data_json}
        }}, "*");
        </script>
    """, height=0)


# --- Clear localStorage (logout/reset) ---
def clear_state():
    components.html("""
        <script>
        window.postMessage({ type: "CLEAR_STATE" }, "*");
        </script>
    """, height=0)