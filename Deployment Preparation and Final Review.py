import os
import streamlit as st

st.set_page_config(page_title="Demo", page_icon="🚀")

st.title("Deployment-Ready Demo App")

debug_mode = os.getenv("ENABLE_DEBUG_MODE", "false")
st.write(f"Debug mode: {debug_mode}")

name = st.text_input("Your name")
if name:
    st.success(f"Hello, {name}!")