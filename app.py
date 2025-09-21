import streamlit as st
import requests
import os

# --- CONFIG ---
API_KEY = "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"
CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
IMAGE_URL = "https://openrouter.ai/api/v1/images/generations"
MAX_HISTORY = 6  # number of recent messages to send/display

# --- PAGE SETUP ---
st.set_page_config(page_title="🤖 Chaatu ", page_icon="🤖", layout="wide")

# Pink theme + chat styles
st.markdown("""
<style>
body { background-color: #ffe6f0; }
.chat-container { max-height: 500px; overflow-y: auto; padding: 10px; }
.user-bubble {
    background-color: #ffb6c1; color: #000; padding: 10px 15px; border-radius: 15px;
    margin: 5px; display: inline-block; max-width: 70%; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
}
.bot-bubble {
    background-color: #ccffdd; color: #000; padding: 10px 15px; border-radius: 15px;
    margin: 5px; display: inline-block; max-width: 70%; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# --- TITLE & DESCRIPTION ---
st.title("🤖 Chaatu ")
st.markdown("**A mini study bot which helps u in your studies by saving notes, summarizes content as ur wish, and provides simple solutions!**")

# --- SESSION STATE ---
if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "notes" not in st.session_state:
    st.session_state.notes = []

# --- FUNCTIONS ---
def is_image_request(text):
    keywords = ["image", "picture", "photo", "draw", "illustrate", "show me"]
    return any(word in text.lower() for word in keywords)

def generate_image(prompt):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "size": "512x512", "n": 1}
    response = requests.post(IMAGE_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['data'][0]['url']
    return None

def get_bot_response(user_input, simple=True, summarize=False):
    st.session_state.conversation.append({"role": "user", "content": user_input})

    # Image request
    if is_image_request(user_input):
        img_url = generate_image(user_input)
        if img_url:
            st.session_state.conversation.append({"role": "assistant", "content": "[Image generated below]"})
            st.session_state.conversation.append({"role": "assistant", "image": img_url})
        else:
            st.session_state.conversation.append({"role": "assistant", "content": "Sorry, I couldn't generate the image."})
        return

    # Text response
    system_prompt = "You are a helpful study buddy. Provide simple solutions. Summarize if asked."
    if summarize:
        system_prompt += " Summarize the answer in bullet points."
    if simple:
        system_prompt += " Explain answers in simple words for easy understanding."

    recent_messages = [{"role": "system", "content": system_prompt}] + st.session_state.conversation[-MAX_HISTORY:]
    payload = {"model": "gpt-3.5-turbo", "messages": recent_messages}
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    response = requests.post(CHAT_URL, headers=headers, json=payload)
    if response.status_code == 200:
        bot_message = response.json()["choices"][0]["message"]["content"]
        st.session_state.conversation.append({"role": "assistant", "content": bot_message})
    else:
        st.session_state.conversation.append({"role": "assistant", "content": f"Error {response.status_code}: {response.text}"})

# --- CHAT DISPLAY ---
chat_container = st.container()
with chat_container:
    for chat in st.session_state.conversation[-MAX_HISTORY:]:
        if chat["role"] == "user":
            st.markdown(f"<div class='user-bubble'><b>You:</b> {chat['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-bubble'><b>Chaatu 🤖:</b> {chat.get('content','')}</div>", unsafe_allow_html=True)
            if 'image' in chat:
                st.image(chat['image'], width=400)

# --- USER INPUT ---
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your question or note...", key="input")
    summarize = st.checkbox("Summarize answer?", key="summarize")
    save_note = st.checkbox("Save this chat as note?", key="save_note")
    submitted = st.form_submit_button("Send")

    if submitted and user_input:
        with st.spinner("Chaatu is thinking..."):
            get_bot_response(user_input, summarize=summarize)
        if save_note:
            st.session_state.notes.append(user_input)
            st.success("Note saved!")

# --- SHOW SAVED NOTES ---
if st.session_state.notes:
    st.markdown("### 💾 Saved Notes")
    for i, note in enumerate(st.session_state.notes, 1):
        st.markdown(f"{i}. {note}")

# --- DOWNLOAD NOTES/Chat ---
if st.session_state.notes:
    notes_text = "\n".join(st.session_state.notes)
    st.download_button("Download Notes", notes_text, file_name="chaatu_notes.txt")
