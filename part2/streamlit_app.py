import streamlit as st
from helpers.api import get_base_url, get_api_key, get_model
from components.chat import chat_stream

def main():
    st.title("Open WebUI Streamlit Demo")

    # Session State
    if "ui_history" not in st.session_state:
        st.session_state.ui_history = []

    base_url = get_base_url()
    token = get_api_key()
    model = get_model()

    tab1, tab2 = st.tabs(["Chatbot", "Admin"])

    # —— Admin Tab ——
    with tab2:
        st.subheader("Data Indexing Admin")
        st.info("📁 File and knowledge uploads are now handled directly within **OpenWebUI**.\n\n"
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
                st.markdown(f"**Assistant:** {content}")

        prompt = st.text_area("Your message", height=100)

        if st.button("Submit Streaming Chat") and prompt.strip():
            st.session_state.ui_history.append({"role": "user", "content": prompt})

            assistant_placeholder = chat_container.empty()

            response_content = chat_stream(
                model=model,
                prompt=prompt,
                base_url=base_url,
                token=token
            )

            assistant_placeholder.markdown(f"**Assistant:** {response_content}")
            st.session_state.ui_history.append({"role": "assistant", "content": response_content})
            prompt = ""  # Clear the input field after submission
            st.rerun()

if __name__ == "__main__":
    main()
