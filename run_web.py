#!/usr/bin/env python3
"""
IdeaOasis Web Application Runner

This script runs the FastAPI web application that:
1. Displays today's idea on the homepage
2. Shows archived ideas
3. Handles voting functionality
4. Provides API endpoints

Usage:
    python run_web.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🌐 Starting IdeaOasis Web Application...")
    print("📱 Web interface will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("-" * 50)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True  # Enable auto-reload for development
    ) 