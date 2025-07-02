import streamlit as st
import requests

st.set_page_config(page_title="TailorTalk Agent", page_icon="🧵")
st.title("🧵 TailorTalk - AI Calendar Assistant")

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000/chat"  # Update this when deploying

# Sidebar
with st.sidebar:
    st.markdown("### 🛠️ Controls")
    if st.button("🧹 Reset Chat"):
        st.session_state.messages = []
        st.rerun()
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=2)
        st.success("✅ Backend Connected")
    except:
        st.error("❌ Backend Not Reachable")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat input field
user_input = st.chat_input("Ask me something like: 'Book a meeting tomorrow at 3 PM'")

# Handle user message
if user_input:
    chat_history = [(msg["role"], msg["content"]) for msg in st.session_state.messages]
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Show typing spinner
    with st.spinner("💬 Thinking..."):
        try:
            response = requests.post(
                BACKEND_URL,
                json={
                    "user_input": user_input,
                    "chat_history": chat_history
                    },
                timeout=30
                )
            if response.status_code == 200:
                # agent_reply = response.json()["response"]
                response_json = response.json()
                agent_reply = response_json.get("response", response_json.get("error", "⚠️ No response received."))
            else:
                agent_reply = f"⚠️ Error {response.status_code} from backend"
        except Exception as e:
            agent_reply = f"❌ Failed to connect to backend: {e}"

    # Add response to history
    st.session_state.messages.append({"role": "assistant", "content": agent_reply})

# Render full conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
