import requests
import json
import streamlit as st

def chat_stream(model: str, messages: list, base_url: str, token: str) -> str:
    url = f"{base_url.rstrip('/')}/api/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "stream": True
    }

    response = requests.post(url, headers=headers, json=payload, stream=True)
    response.raise_for_status()

    placeholder = st.empty()
    full_text = ""
    think_text = ""
    in_think = False

    for line in response.iter_lines(decode_unicode=True):
        if not line or line.strip() == "":
            continue

        chunk = line.removeprefix("data: ").strip()
        if chunk == "[DONE]":
            break

        try:
            data = json.loads(chunk)
            delta = data.get("choices", [{}])[0].get("delta", {})
            delta_content = delta.get("content", "")
            if not delta_content:
                continue

            full_text += delta_content

            # Detect <think> start and end
            if "<think>" in delta_content:
                in_think = True
                delta_content = delta_content.replace("<think>", "")

            if "</think>" in delta_content:
                in_think = False
                delta_content = delta_content.replace("</think>", "")

            if in_think:
                think_text += delta_content
                placeholder.markdown(
                    f"""
<details open>
  <summary><strong>🤖 Thinking...</strong></summary>
  <pre>{think_text.strip()}</pre>
</details>
                    """,
                    unsafe_allow_html=True
                )
            else:
                # If we previously collected a think block, strip it from final output
                visible = full_text
                if "<think>" in full_text and "</think>" in full_text:
                    think_block = full_text.split("<think>")[1].split("</think>")[0]
                    visible = full_text.replace(f"<think>{think_block}</think>", "").strip()

                placeholder.markdown(f"**Assistant:** {visible}")
        except Exception as e:
            st.error(f"Error during stream: {e}")
            continue

    return full_text
