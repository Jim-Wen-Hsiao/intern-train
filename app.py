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
    st.success(f"""Welcome IT Intern ??  
Feel free to ask me questions about the problem when you're helping users.

If the questions are about the IP or require domain accounts,  
please ask Tracy, Joseph, or Daniel.""")
    authenticator.logout("Logout", "sidebar")

    # Sidebar link buttons
    def styled_link(label, url):
        return f"""
        <a href="{url}" target="_blank" style="text-decoration:none;">
            <div style="
                background-color:#2b6cb0;
                color:white;
                padding:12px 18px;
                margin-bottom:10px;
                border-radius:6px;
                text-align:center;
                font-weight:bold;
            ">
                {label}
            </div>
        </a>
        """

    with st.sidebar:
        st.markdown(styled_link("Microsoft Intune", "https://admin.microsoft.com"), unsafe_allow_html=True)
        st.markdown(styled_link("Shared Drive", "https://fpcusa-my.sharepoint.com/:f:/g/personal/atsai_inteplast_com/EsBv6Ol66Q1CgXG_Rbc7KOUBdnHVfhm6PAGKoeChz60zbQ?e=LLFDSK"), unsafe_allow_html=True)
        st.markdown(styled_link("UPS", "https://www.ups.com/lasso/login?reasonCode=-1"), unsafe_allow_html=True)
        st.markdown(styled_link("Travel Request", "https://travel.inteplast.com"), unsafe_allow_html=True)
        st.markdown(styled_link("Asset Manager", "https://fpcusa.sharepoint.com/sites/Inteplast/preoffice/mid/it/ittest/Lists/Asset%20manager/AllItems.aspx?sortField=AssetType&isAscending=false&groupBy=Status&viewpath=%2Fsites%2FInteplast%2Fpreoffice%2Fmid%2Fit%2Fittest%2FLists%2FAsset%20manager%2FAllItems%2Easpx"), unsafe_allow_html=True)

    st.title("IT Intern Assist Chatbot")

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