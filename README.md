# TailorTalk 🧵 — AI Calendar Booking Assistant

An intelligent AI-powered assistant that helps users book appointments and manage their Google Calendar through natural conversation.

## ✨ Features

### 🤖 **Smart AI Assistant**
- **Natural Language Processing**: Book meetings using plain English
- **Intelligent Parsing**: Understands various date/time formats (tomorrow, next monday, 3 PM, etc.)
- **Context Awareness**: Remembers conversation history and asks follow-up questions
- **Error Handling**: Graceful handling of missing information and conflicts

### 📅 **Calendar Management**
- **Google Calendar Integration**: Direct booking to your Google Calendar
- **Availability Checking**: Verify time slots before booking
- **Conflict Resolution**: Automatically detect and avoid scheduling conflicts
- **Meeting Details**: Support for titles, descriptions, attendees, and durations

### 🎨 **Beautiful UI**
- **Modern Streamlit Interface**: Clean, responsive design with custom styling
- **Real-time Status**: Backend connection monitoring
- **Chat History**: Persistent conversation memory
- **Quick Actions**: Example prompts and meeting history
- **Visual Feedback**: Color-coded messages and status indicators

### 🔧 **Enhanced Backend**
- **FastAPI REST API**: High-performance backend with automatic documentation
- **Comprehensive Validation**: Input validation and error handling
- **Health Monitoring**: System status and health checks
- **Logging**: Detailed logging for debugging and monitoring

## 🛠 Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain**: Framework for developing applications with LLMs
- **Groq**: High-performance LLM inference
- **Google Calendar API**: Calendar integration
- **Pydantic**: Data validation using Python type annotations

### Frontend
- **Streamlit**: Rapid web app development
- **Custom CSS**: Beautiful, responsive design
- **Real-time Updates**: Live status monitoring

### Infrastructure
- **Google Cloud**: Service account for calendar access
- **Environment Variables**: Secure configuration management
- **Logging**: Comprehensive error tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud Project with Calendar API enabled
- Groq API key

### 1. Clone and Setup
```bash
git clone <repository-url>
cd tailorTalk
pip install -r requirements.txt
```

### 2. Google Calendar Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Calendar API
4. Create a Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Download the JSON key file
5. Share your calendar with the service account email
6. Place the JSON file in the project root as `assignments-464701-418734497e1c.json`

### 3. Environment Configuration
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your-groq-api-key-here
```

### 4. Run the Application

#### Start the Backend
```bash
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Start the Frontend
```bash
cd streamlitApp
streamlit run app.py
```

The application will be available at:
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📖 Usage Examples

### Booking Meetings
```
"Book a meeting tomorrow at 3 PM about project review"
"Schedule a 1-hour call next Monday at 10 AM with sarah@company.com"
"Set up a 30-minute meeting on 2025-01-15 at 14:30 with team@company.com"
```

### Checking Schedule
```
"Show me my upcoming meetings"
"What's on my calendar for tomorrow?"
"Check my availability for next week"
```

### Managing Meetings
```
"Cancel my meeting with John tomorrow"
"Reschedule my 3 PM meeting to 4 PM"
"What meetings do I have this week?"
```

## 🔧 API Endpoints

### Core Endpoints
- `POST /chat` - Main chat interface
- `POST /book_meeting` - Direct meeting booking
- `GET /health` - System health check
- `GET /` - API information

### Response Format
```json
{
  "response": "Meeting booked successfully!",
  "success": true,
  "details": {
    "date": "2025-01-15",
    "time": "14:30",
    "participants": ["user@example.com"],
    "agenda": "Project review",
    "duration": 60
  }
}
```

## 🎯 Key Features

### Natural Language Understanding
- **Flexible Date Parsing**: "tomorrow", "next monday", "2025-01-15"
- **Time Format Support**: "3 PM", "15:30", "3:30 PM"
- **Duration Recognition**: "1 hour", "30 minutes", "2-hour meeting"
- **Context Extraction**: Meeting titles, descriptions, attendees

### Smart Error Handling
- **Validation**: Comprehensive input validation
- **Conflict Detection**: Automatic availability checking
- **Graceful Degradation**: Fallback responses for errors
- **User Guidance**: Helpful error messages with suggestions

### Enhanced User Experience
- **Real-time Status**: Backend connection monitoring
- **Visual Feedback**: Color-coded messages and status indicators
- **Quick Actions**: Example prompts and meeting history
- **Responsive Design**: Works on desktop and mobile

## 🔒 Security & Best Practices

### Environment Variables
- API keys stored in `.env` file (not committed to version control)
- Service account credentials secured
- Environment-specific configurations

### Error Handling
- Comprehensive try-catch blocks
- Detailed logging for debugging
- User-friendly error messages
- Graceful fallbacks

### Data Validation
- Pydantic models for request/response validation
- Input sanitization and validation
- Type checking and conversion

## 🚧 Development

### Project Structure
```
tailorTalk/
├── app/
│   ├── main.py          # FastAPI backend
│   ├── agent.py         # LangChain agent
│   └── calendarUtils.py # Google Calendar integration
├── streamlitApp/
│   └── app.py          # Streamlit frontend
├── requirements.txt     # Python dependencies
└── README.md          # This file
```

### Adding New Features
1. **Backend**: Add new endpoints in `app/main.py`
2. **Calendar**: Extend `app/calendarUtils.py` with new functions
3. **Agent**: Add new tools in `app/agent.py`
4. **Frontend**: Enhance UI in `streamlitApp/app.py`

### Testing
```bash
# Test backend
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Book a meeting tomorrow at 3 PM"}'

# Test health endpoint
curl http://localhost:8000/health
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:
1. Check the logs for error messages
2. Verify your API keys and service account setup
3. Ensure all dependencies are installed
4. Check the API documentation at `/docs`

---

**Made with ❤️ using FastAPI, Streamlit, and LangChain**
