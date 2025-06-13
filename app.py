import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
import requests
from dotenv import load_dotenv
import pathlib

# Load environment variables
load_dotenv()
API_KEY = st.secrets["OPENAI_API_KEY"]

# Load config.yaml for login credentials
config_path = pathlib.Path(__file__).parent / "config.yaml"
with open(config_path, "r") as file:
    config = yaml.safe_load(file)

if config is None or "credentials" not in config:
    st.error("Invalid or empty config.yaml. Please check the file.")
    st.stop()

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# Show login form
authenticator.login(fields={"Form name": "Login"}, location="main")

if st.session_state.get("authentication_status") == False:
    st.error("Incorrect username or password")
    st.stop()
elif st.session_state.get("authentication_status") is None:
    st.warning("Please enter your credentials.")
    st.stop()
else:
    name = st.session_state["name"]
    st.success(f"Welcome {name} 👋")
    authenticator.logout("Logout", "sidebar")

    st.title("Intern Onboarding Chatbot")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    user_input = st.chat_input("Ask me anything about the onboarding process:")

    if user_input:
        st.session_state.chat.append(("user", user_input))

        try:
            with open("InternGuideNote.txt", "r", encoding="utf-8") as f:
                file_content = f.read()
        except FileNotFoundError:
            st.error("Missing file: InternGuideNote.txt")
            st.stop()

        system_prompt = f"""
You are a helpful assistant for onboarding IT interns.
Use the following document as your source of truth:

{file_content}
"""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        body = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)

        if response.ok:
            result = response.json()
            bot_reply = result["choices"][0]["message"]["content"]
        else:
            bot_reply = f"Error: {response.text}"

        st.session_state.chat.append(("bot", bot_reply))

    for sender, message in st.session_state.chat:
        st.chat_message("user" if sender == "user" else "assistant").write(message)