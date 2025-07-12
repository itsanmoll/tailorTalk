#!/usr/bin/env python3
"""
TailorTalk Startup Script
Launches both backend and frontend services
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import streamlit
        import langchain
        import requests
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("⚠️  .env file not found")
        print("Please create a .env file with your GROQ_API_KEY")
        return False
    return True

def check_service_account():
    """Check if service account file exists"""
    service_account_file = "assignments-464701-418734497e1c.json"
    if not os.path.exists(service_account_file):
        print(f"⚠️  {service_account_file} not found")
        print("Please ensure your Google service account JSON file is in the root directory")
        return False
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting TailorTalk Backend...")
    backend_cmd = [
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--reload", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ]
    
    try:
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Backend started successfully")
        return backend_process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the Streamlit frontend"""
    print("🎨 Starting TailorTalk Frontend...")
    frontend_cmd = [
        sys.executable, "-m", "streamlit", 
        "run", "streamlitApp/app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ]
    
    try:
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Frontend started successfully")
        return frontend_process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def wait_for_backend():
    """Wait for backend to be ready"""
    import requests
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return True
        except:
            pass
        time.sleep(1)
        if i % 5 == 0:
            print(f"⏳ Waiting for backend... ({i+1}/{max_attempts})")
    
    print("❌ Backend failed to start")
    return False

def print_startup_info():
    """Print startup information"""
    print("\n" + "="*60)
    print("🧵 TailorTalk - AI Calendar Assistant")
    print("="*60)
    print("📱 Frontend: http://localhost:8501")
    print("🔧 Backend:  http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("="*60)
    print("💡 Try these example commands:")
    print("   • Book a meeting tomorrow at 3 PM")
    print("   • Schedule a 1-hour call next Monday")
    print("   • Show me my upcoming meetings")
    print("="*60)
    print("Press Ctrl+C to stop all services")
    print("="*60 + "\n")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down TailorTalk...")
    sys.exit(0)

def main():
    """Main startup function"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🔍 Checking prerequisites...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_env_file():
        print("Continuing anyway...")
    
    # Check service account
    if not check_service_account():
        print("Continuing anyway...")
    
    print("\n🚀 Starting TailorTalk services...")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    # Wait for backend to be ready
    if not wait_for_backend():
        backend_process.terminate()
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        sys.exit(1)
    
    # Print startup information
    print_startup_info()
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
                
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        # Cleanup
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
        print("✅ All services stopped")

if __name__ == "__main__":
    main() 