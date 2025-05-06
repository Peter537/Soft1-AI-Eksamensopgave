import streamlit as st
from helpers.api import get_base_url, get_api_key
from helpers.file_utils import (
    check_if_file_exists,
    send_file,
    get_file,
    delete_file,
)
from components.chat import chat_stream

def main():
    st.title("Open WebUI Streamlit Demo")
    base_url = get_base_url()
    token = get_api_key()
    model = st.text_input("Model", value="llama3.2:latest")

    # file upload state
    if "file_uploaded" not in st.session_state:
        st.session_state["file_uploaded"] = False

    file_exists, files = check_if_file_exists(token, base_url)

    # Chat UI
    if file_exists:
        prompt = st.text_area("Prompt for streaming chat")
        file = get_file(token, base_url, files[0]["id"])
        if st.button("Submit Streaming Chat"):
            if not token:
                st.error("API Key is required for streaming chat.")
            else:
                chat_stream(model, prompt, base_url, token, file)

    # File upload/remove UI
    if not st.session_state["file_uploaded"]:
        if file_exists:
            st.info("A file is already uploaded.")
            st.write("Files:", files)
            if st.button("🧹 Remove Uploaded File"):
                success = delete_file(token, base_url, files[0]["id"])
                if success:
                    st.success("File removed successfully!")
                    st.session_state["file_uploaded"] = False
                    st.rerun()
                else:
                    st.error("Failed to remove the file.")
        else:
            uploaded = st.file_uploader("Select a file to send", type=["json", "pdf", "md"])
            if st.button("Upload File"):
                if not token:
                    st.error("API Key is required for file upload.")
                elif not uploaded:
                    st.error("Please select a file first.")
                else:
                    res = send_file(token, base_url, uploaded)
                    st.success("File uploaded successfully!")
                    st.json(res)
                    st.rerun()
