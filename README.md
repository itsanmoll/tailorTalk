# TailorTalk 🧵 — AI Calendar Booking Assistant

This is an AI-powered assistant that helps users book appointments on your Google Calendar through natural conversation.

## 🔧 Stack
- FastAPI (Backend)
- LangChain + Gemini (LLM)
- Google Calendar API (via Service Account)
- Streamlit (Frontend Chat)

## 🛠 Setup Instructions

1. Create a service account on Google Cloud
2. Enable Calendar API and share your test calendar with the service account
3. Place `service_account.json` in the root directory
4. Add your Gemini API key in `.env`:

```env
GOOGLE_API_KEY=your-key-here
