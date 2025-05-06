import requests
import json
import streamlit as st

def chat_stream(model: str, prompt: str, base_url: str, token: str, file_obj=None) -> str:
    url = f"{base_url.rstrip('/')}/api/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    file_text = ""
    if file_obj:
        try:
            file_text = file_obj.get("data", {}).get("content", "")
            if not isinstance(file_text, str):
                raise ValueError("File content is not a valid string.")
        except Exception as e:
            st.error(f"Error processing file: {e}")
            return ""

    full_prompt = f"<FILE CONTENT>\n{file_text}\n</FILE CONTENT>\nUser Query: {prompt}"
    payload = {"model": model, "messages": [{"role": "user", "content": full_prompt}], "stream": True}
    response = requests.post(url, headers=headers, json=payload, stream=True)
    response.raise_for_status()

    placeholder = st.empty()
    full_text = ""
    for line in response.iter_lines(decode_unicode=True):
        if not line or line.strip() == b"":
            continue
        chunk = line.removeprefix("data: ").strip()
        if chunk == "[DONE]":
            break
        delta = json.loads(chunk)["choices"][0]["delta"].get("content", "")
        full_text += delta
        placeholder.text(full_text)
    return full_text
