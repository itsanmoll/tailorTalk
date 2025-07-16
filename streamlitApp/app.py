import streamlit as st
import requests
import json
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="TailorTalk Agent", 
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .error-message {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    .success-message {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
    }
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-online { background-color: #4caf50; }
    .status-offline { background-color: #f44336; }
</style>
""", unsafe_allow_html=True)

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"
CHAT_ENDPOINT = f"{BACKEND_URL}/chat"
HEALTH_ENDPOINT = f"{BACKEND_URL}/health"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "meeting_history" not in st.session_state:
    st.session_state.meeting_history = []
if "backend_status" not in st.session_state:
    st.session_state.backend_status = "unknown"

def check_backend_status():
    """Check if backend is reachable"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=3)
        if response.status_code == 200:
            return "online", response.json()
        else:
            return "offline", None
    except:
        return "offline", None

def send_message(user_input, chat_history):
    """Send message to backend with better error handling"""
    try:
        response = requests.post(
            CHAT_ENDPOINT,
            json={
                "user_input": user_input,
                "chat_history": chat_history
            },
            timeout=30
        )
        if response.status_code == 200:
            response_json = response.json()
            # If meeting booked, add emoji and success message
            if response_json.get("response", "").lower().startswith("meeting booked"):
                return f"✅ Meeting booked successfully!\n\n{response_json['response']}", True
            return response_json.get("response", "⚠️ No response received."), True
        else:
            return f"⚠️ Backend error: {response.status_code}", False
    except requests.exceptions.Timeout:
        return "⏰ Request timed out. Please try again.", False
    except requests.exceptions.ConnectionError:
        return "🔌 Cannot connect to backend. Please check if the server is running.", False
    except Exception as e:
        return f"❌ Error: {str(e)}", False

# Header
st.markdown("""
<div class="main-header">
    <h1>🧵 TailorTalk - AI Calendar Assistant</h1>
    <p>Your intelligent assistant for booking meetings and managing your calendar</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🛠️ Controls")
    
    # Backend status
    status, health_data = check_backend_status()
    st.session_state.backend_status = status
    
    status_color = "🟢" if status == "online" else "🔴"
    st.markdown(f"{status_color} **Backend Status**: {status.title()}")
    
    if health_data:
        st.markdown(f"**Last Check**: {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Reset Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("📋 Meeting History", use_container_width=True):
            st.session_state.show_history = not st.session_state.get('show_history', False)
            st.rerun()
    
    # Example prompts
    st.markdown("### 💡 Example Prompts")
    example_prompts = [
        "Book a meeting tomorrow at 3 PM with john@example.com",
        "Schedule a 1-hour call next Monday at 10 AM with sarah@company.com about project review",
        "Set up a 30-minute meeting on 2025-01-15 at 14:30 with team@company.com"
    ]
    
    for prompt in example_prompts:
        if st.button(prompt, key=f"prompt_{prompt[:20]}", use_container_width=True):
            st.session_state.example_input = prompt
            st.rerun()
    
    # Meeting history
    if st.session_state.get('show_history', False):
        st.markdown("### 📋 Recent Meetings")
        if st.session_state.meeting_history:
            for i, meeting in enumerate(st.session_state.meeting_history[-5:]):
                with st.expander(f"Meeting {i+1} - {meeting.get('date', 'Unknown')}"):
                    st.write(f"**Time**: {meeting.get('time', 'Unknown')}")
                    st.write(f"**Participants**: {', '.join(meeting.get('participants', []))}")
                    if meeting.get('agenda'):
                        st.write(f"**Agenda**: {meeting['agenda']}")
        else:
            st.info("No meetings booked yet.")

# Main chat interface
if st.session_state.get('example_input'):
    user_input = st.session_state.example_input
    del st.session_state.example_input
else:
    user_input = st.chat_input(
        "Try: Book a meeting tomorrow at 3 PM with john@example.com",
        key="chat_input"
    )

# Handle user message
if user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": datetime.now()})
    
    # Prepare chat history for backend
    chat_history = [(msg["role"], msg["content"]) for msg in st.session_state.messages[:-1]]
    
    # Show typing indicator
    with st.spinner("💬 Processing your request..."):
        # Send message to backend
        response_text, success = send_message(user_input, chat_history)
        
        # Add assistant response to chat
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_text, 
            "timestamp": datetime.now(),
            "success": success
        })
        
        # Extract meeting details if booking was successful
        if success and "✅ Meeting booked successfully" in response_text:
            # Try to extract meeting details for history
            try:
                # Simple extraction for demo - in real app, parse the response more carefully
                if "📅" in response_text and "🕐" in response_text:
                    meeting_info = {
                        "date": datetime.now().strftime("%Y-%m-%d"),  # Simplified
                        "time": "Unknown",
                        "participants": [],
                        "agenda": None
                    }
                    st.session_state.meeting_history.append(meeting_info)
            except:
                pass

# Display chat messages with better styling
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        # Determine message styling
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong><br>
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Check if it's an error message
            if "❌" in msg["content"] or "⚠️" in msg["content"]:
                css_class = "error-message"
            elif "✅" in msg["content"]:
                css_class = "success-message"
            else:
                css_class = "assistant-message"
            
            st.markdown(f"""
            <div class="chat-message {css_class}">
                <strong>Assistant:</strong><br>
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        
        # Show timestamp if available
        if "timestamp" in msg:
            st.caption(f"Sent at {msg['timestamp'].strftime('%H:%M:%S')}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    <p>🧵 TailorTalk v1.0 | Powered by AI & Google Calendar</p>
</div>
""", unsafe_allow_html=True)
