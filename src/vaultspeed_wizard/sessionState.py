import json
import streamlit as st
import os

def save_session_state(source_name):
    serializable_session_state = {}
    for key, value in st.session_state.items():
        try:
            json.dumps(value)
            serializable_session_state[key] = value
        except TypeError:
            serializable_session_state[key] = str(value)

    filename = f"{source_name}_session_state.txt"
    with open(filename, "w") as file:
        json.dump(serializable_session_state, file)

def load_session_state(source_name):
    filename = f"{source_name}_session_state.txt"
    with open(filename, "r") as file:
        session_state = json.load(file)
        for key, value in session_state.items():
            st.session_state[key] = value

def show_session_state_selector():
    
    session_files = [f for f in os.listdir() if f.endswith("_session_state.txt")]
    session_names = [f.replace("_session_state.txt", "") for f in session_files]

    if len(session_files) == 0:
        return
    else: 
        selected_session = st.selectbox("Select source to load", session_names)
        st.session_state.selected_session = selected_session
