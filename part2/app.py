import streamlit as st
from helpers.api import get_base_url, get_api_key, get_model
from components.chat import chat_stream

def render_thinking_dropdown(thinking_text: str) -> str:
    return f"""
<details open>
  <summary><strong>🤖 AI is thinking...</strong></summary>
  <pre>{thinking_text}</pre>
</details>
"""

def main():
    st.set_page_config(page_title="Open WebUI Streamlit Demo")
    st.title("Open WebUI Streamlit Demo")

    if "ui_history" not in st.session_state:
        st.session_state.ui_history = []

    base_url = get_base_url()
    token = get_api_key()
    model = get_model()

    tab1, tab2 = st.tabs(["Chatbot", "Admin"])

    # —— Admin Tab ——
    with tab2:
        st.subheader("Data Indexing Admin")
        st.info("\U0001F4C1 File and knowledge uploads are now handled directly within **OpenWebUI**.\n\n"
                "No additional setup is required here.")

    # —— Chatbot Tab ——
    with tab1:
        st.subheader("AI Shopping Assistant")

        chat_container = st.container()

        for msg in st.session_state.ui_history:
            role = msg.get("role")
            content = msg.get("content")

            if role == "user":
                st.markdown(f"**You:** {content}")
            else:
                # If there's a <Think> block, extract it
                if "<Think>" in content and "</Think>" in content:
                    think_text = content.split("<Think>")[1].split("</Think>")[0]
                    visible_response = content.replace(f"<Think>{think_text}</Think>", "").strip()

                    if visible_response:
                        # Final response: just show it normally
                        st.markdown(f"**Assistant:** {visible_response}")
                    else:
                        # Still thinking: show dropdown
                        st.markdown(render_thinking_dropdown(think_text), unsafe_allow_html=True)
                else:
                    # No <Think>: normal assistant response
                    st.markdown(f"**Assistant:** {content}")

        prompt = st.text_area("Your message", height=100)

        if st.button("Submit Streaming Chat") and prompt.strip():
            st.session_state.ui_history.append({"role": "user", "content": prompt})

            assistant_placeholder = chat_container.empty()

            # Stream full conversation history to the LLM
            response_content = chat_stream(
                model=model,
                messages=st.session_state.ui_history,
                base_url=base_url,
                token=token
            )

            # Save assistant's full response (may contain <Think>)
            st.session_state.ui_history.append({"role": "assistant", "content": response_content})

            st.rerun()

if __name__ == "__main__":
    main()
