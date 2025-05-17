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

    # Initialize session state
    if "file_uploaded" not in st.session_state:
        st.session_state.file_uploaded = False
    if "history" not in st.session_state:
        # Prepend a system prompt to enforce shopping context and usage of the uploaded data
        system_prompt = (
            "You are a shopping assistant. You may only answer shopping-related queries using the uploaded datafile. "
            "If asked for code snippets, life advice, profanity, or any out-of-scope request, respond with: 'Sorry, but i cannot help with that'."
        )
        st.session_state.history = [{"role": "system", "content": system_prompt}]

    base_url = get_base_url()
    token = get_api_key()
    model = "llama3.2:latest"

    tab1, tab2 = st.tabs(["Chatbot", "Admin"])

    # Admin Tab for file upload/remove
    with tab2:
        file_exists, files = check_if_file_exists(token, base_url)

        if not st.session_state.file_uploaded and not file_exists:
            uploaded = st.file_uploader("Select a file to send", type=["json", "pdf", "md", "csv"])
            if st.button("Upload File"):
                if not token:
                    st.error("API Key is required for file upload.")
                elif not uploaded:
                    st.error("Please select a file first.")
                else:
                    res = send_file(token, base_url, uploaded)
                    st.success("File uploaded successfully!")
                    st.json(res)
                    st.session_state.file_uploaded = True
                    st.experimental_rerun()
        else:
            st.info("A file is already uploaded.")
            st.write("Files:", files)
            if st.button("🧹 Remove Uploaded File"):
                success = delete_file(token, base_url, files[0]["id"])
                if success:
                    st.success("File removed successfully!")
                    st.session_state.file_uploaded = False
                    st.experimental_rerun()
                else:
                    st.error("Failed to remove the file.")

    # Chatbot Tab for messaging
    with tab1:
        # Display chat history (skip system prompt)
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.history:
                if msg["role"] == "user":
                    st.markdown(f"**You:** {msg['content']}")
                elif msg["role"] == "assistant":
                    st.markdown(f"**Assistant:** {msg['content']}")

        # Input prompt
        prompt = st.text_area("Your message", height=100)
        if st.button("Submit Streaming Chat"):
            if not token:
                st.error("API Key is required for streaming chat.")
            else:
                # Append user message to history
                st.session_state.history.append({"role": "user", "content": prompt})

                # Placeholder for assistant
                assistant_placeholder = chat_container.empty()
                response_content = ""

                # Include file reference if exists
                file_id = files[0]["id"] if check_if_file_exists(token, base_url)[0] else None
                datafile = get_file(token, base_url, file_id) if file_id else None

                # Call streaming API with full message history
                for chunk in chat_stream(
                    model,
                    st.session_state.history,
                    base_url,
                    token,
                    datafile
                ):
                    response_content += chunk
                    assistant_placeholder.markdown(f"**Assistant:** {response_content}")

                # Save assistant response
                st.session_state.history.append({"role": "assistant", "content": response_content})
                st.rerun()


if __name__ == "__main__":
    main()
