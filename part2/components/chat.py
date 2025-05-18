import requests
import json
import streamlit as st

def chat_stream(model: str, prompt: str, base_url: str, token: str) -> str:
    url = f"{base_url.rstrip('/')}/api/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    full_prompt = f"User Query: {prompt}"
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
        try:
            data = json.loads(chunk)
            # Defensive: check for choices, delta, and content
            choices = data.get("choices", [])
            if choices:
                delta = choices[0].get("delta", {})
                if isinstance(delta, dict):
                    delta_content = delta.get("content", "")
                    if delta_content:
                        full_text += delta_content
                        placeholder.text(full_text)
        except Exception as e:
            # Optionally log or display the error for debugging
            st.error(f"Error processing response: {e}")
            continue
    return full_text
