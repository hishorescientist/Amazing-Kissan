import streamlit as st

# ------------------ SAVE STATE ------------------
def save_state(state_dict):
    """
    Save state into Streamlit session_state.
    """
    for k, v in state_dict.items():
        st.session_state[k] = v

# ------------------ LOAD STATE ------------------
def load_state(keys, default_state=None):
    """
    Load state from Streamlit session_state.
    Returns a dict with the requested keys.
    """
    state = {}
    for k in keys:
        if k in st.session_state:
            state[k] = st.session_state[k]
        elif default_state and k in default_state:
            state[k] = default_state[k]
        else:
            state[k] = None
    return state

# ------------------ CLEAR STATE ------------------
def clear_state(keys=None):
    """
    Clears specific keys or entire session_state if keys is None.
    """
    if keys:
        for k in keys:
            if k in st.session_state:
                del st.session_state[k]
    else:
        st.session_state.clear()