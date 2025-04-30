import streamlit as st
import requests
import json

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_base_url() -> str:
    """Get the base URL of your Open WebUI instance."""
    return st.text_input("Base URL", value="http://localhost:3000")

def get_api_key() -> str:
    """Get your Bearer API key."""
    return st.text_input("API Key", type="password")

# Streaming chat using Open WebUI's chat-completions endpoint
def chat_stream(model: str, prompt: str, base_url: str, token: str) -> str:
    """
    Streams a chat completion, updating the UI chunk-by-chunk.
    """
    url = f"{base_url.rstrip('/')}/api/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
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

# Non-streaming chat

def chat_non_stream(model: str, prompt: str, base_url: str, token: str) -> str:
    """
    Sends a complete chat completion request and returns the full reply.
    """
    url = f"{base_url.rstrip('/')}/api/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

# Raw file upload (no RAG) to /api/v1/files/

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

# Chat with file: read file client-side and send its text in a chat message

def chat_with_file(model: str, file_obj, query: str, base_url: str, token: str) -> str:
    """
    Reads file content locally and sends it as part of the chat prompt.
    """
    # Read file bytes and decode to text
    raw = file_obj.read()
    try:
        file_text = raw.decode("utf-8")
    except UnicodeDecodeError:
        file_text = raw.decode("latin-1")
    # Construct combined prompt
    prompt = f"<FILE CONTENT>\n{file_text}\n</FILE CONTENT>\nUser Query: {query}"
    # Use non-streaming chat for simplicity
    return chat_non_stream(model, prompt, base_url, token)

# ── Streamlit App ─────────────────────────────────────────────────────────────
st.title("Open WebUI Streamlit Demo")
base_url = get_base_url()
token    = get_api_key()
model    = st.text_input("Model", value="llama3.2:latest")

mode = st.sidebar.radio("Mode", [
    "Streaming Chat",
    "Non-Streaming Chat",
    "Send File",
    "Chat with File"
])

if mode == "Streaming Chat":
    prompt = st.text_area("Prompt for streaming chat")
    if st.button("Submit Streaming Chat"):
        if not token:
            st.error("API Key is required for streaming chat.")
        else:
            chat_stream(model, prompt, base_url, token)

elif mode == "Non-Streaming Chat":
    prompt = st.text_area("Prompt for non-streaming chat")
    if st.button("Submit Chat"):
        if not token:
            st.error("API Key is required for chat.")
        else:
            reply = chat_non_stream(model, prompt, base_url, token)
            st.write(reply)

elif mode == "Send File":
    uploaded = st.file_uploader("Select a file to send", type=["txt", "pdf", "md"] )
    if st.button("Upload File"):
        if not token:
            st.error("API Key is required for file upload.")
        elif not uploaded:
            st.error("Please select a file first.")
        else:
            res = send_file(token, base_url, uploaded)
            st.success("File uploaded successfully!")
            st.json(res)

elif mode == "Chat with File":
    uploaded = st.file_uploader("Select a file to include in chat", type=["txt", "md"] )
    query    = st.text_input("Enter your query regarding the file")
    if st.button("Submit Chat with File"):
        if not token:
            st.error("API Key is required for chat.")
        elif not uploaded or not query:
            st.error("Please provide both a file and query.")
        else:
            answer = chat_with_file(model, uploaded, query, base_url, token)
            st.write(answer)
