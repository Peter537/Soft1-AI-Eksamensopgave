import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_base_url() -> str:
    """Get the base URL of your Open WebUI instance."""
    return st.text_input("Base URL", value="http://localhost:3000")

def get_api_key() -> str:
    """Get your Bearer API key."""
    load_dotenv()
    key = os.getenv("API_KEY")
    if not key:
        st.error("API Key not found in the environment file.")
    return key

def check_if_file_exists(token: str, base_url: str) -> bool:
    """Check if there is an existing uploaded file in the system."""
    url = f"{base_url.rstrip('/')}/api/v1/files/"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    files = resp.json()  # Assuming response is directly a list of files
    return len(files) > 0, files  # Return both whether file exists and the list of files

# Streaming chat using Open WebUI's chat-completions endpoint
def chat_stream(model: str, prompt: str, base_url: str, token: str, file_obj=None) -> str:
    """
    Streams a chat completion, updating the UI chunk-by-chunk.
    """
    url = f"{base_url.rstrip('/')}/api/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    if file_obj:
        print("File object is not None")
        try:
            file_text = file_obj.get("data", {}).get("content", "")
            if not isinstance(file_text, str):
                raise ValueError("File content is not a valid string.")
        except (UnicodeDecodeError, ValueError) as e:
            st.error(f"Error processing file: {e}")
            return


    full_prompt = f"""
    <FILE CONTENT>\n{file_text}\n</FILE CONTENT>\nUser Query: {prompt}
    """
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": full_prompt}],
        "stream": True
    }
    response = requests.post(url, headers=headers, json=payload, stream=True)
    response.raise_for_status()
    placeholder = st.empty()
    full_text = ""
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        chunk = line.removeprefix("data: ").strip()
        if chunk == "[DONE]":
            break
        delta = json.loads(chunk)["choices"][0]["delta"].get("content", "")
        full_text += delta
        placeholder.text(full_text)
    return full_text

def delete_file(token: str, base_url: str, file_id: str) -> bool:
    """Delete a file from the system."""
    url = f"{base_url.rstrip('/')}/api/v1/files/{file_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.delete(url, headers=headers)
    return resp.status_code == 200  # Return True if deletion was successful

def send_file(token: str, base_url: str, file_obj) -> dict:
    """
    Uploads a file directly to Open WebUI and returns the server's JSON response.
    """
    url = f"{base_url.rstrip('/')}/api/v1/files/"
    headers = {"Authorization": f"Bearer {token}"}
    content_type = getattr(file_obj, "type", "application/octet-stream")
    files = {"file": (file_obj.name, file_obj, content_type)}
    resp = requests.post(url, headers=headers, files=files)
    resp.raise_for_status()
    return resp.json()

def get_file(token: str, base_url: str, file_id: str) -> dict:
    """
    Fetches a file from the server using its ID.
    """
    url = f"{base_url.rstrip('/')}/api/v1/files/{file_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

# ── Streamlit App ─────────────────────────────────────────────────────────────
st.title("Open WebUI Streamlit Demo")
base_url = get_base_url()
token    = get_api_key()
model    = st.text_input("Model", value="llama3.2:latest")

if "file_uploaded" not in st.session_state:
    st.session_state["file_uploaded"] = False

file_exists, files = check_if_file_exists(token, base_url)

if file_exists:
    prompt = st.text_area("Prompt for streaming chat")
    file = get_file(token, base_url, files[0].get("id"))  # Assuming the response contains an 'id' field for the file
    if st.button("Submit Streaming Chat"):
        if not token:
            st.error("API Key is required for streaming chat.")
        else:
            chat_stream(model, prompt, base_url, token, file)

# File upload logic
if not st.session_state["file_uploaded"]:
    if file_exists:
        st.info("A file is already uploaded.")
        st.write("Files:", files)  # Show the files (this should ideally be a list of file names or IDs)
        file_id = files[0].get("id")  # Assuming the response contains an 'id' field for the file
        if st.button("🧹 Remove Uploaded File"):
            if file_id and delete_file(token, base_url, file_id):
                st.success("File removed successfully!")
                st.session_state["file_uploaded"] = False
            else:
                st.error("Failed to remove the file.")

    else:
        uploaded = st.file_uploader("Select a file to send", type=["json", "pdf", "md"] )
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
