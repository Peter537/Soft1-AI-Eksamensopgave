import streamlit as st
from dotenv import load_dotenv
import os

def get_base_url() -> str:
    return "http://localhost:3000"

def get_api_key() -> str:
    load_dotenv()
    key = os.getenv("API_KEY")
    if not key:
        st.error("API Key not found in the environment file.")
    return key
