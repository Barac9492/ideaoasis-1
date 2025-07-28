#!/usr/bin/env python3
"""
IdeaOasis Scheduler Runner

This script runs the daily idea discovery scheduler that:
1. Runs at 6 AM Korea time every day
2. Discovers new startup ideas from various sources
3. Processes them with AI for Korean translation
4. Saves them to the database
5. Archives old ideas after 24 hours

Usage:
    python run_scheduler.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.scheduler import main

if __name__ == "__main__":
    print("🚀 Starting IdeaOasis Scheduler...")
    print("📅 Daily discovery scheduled for 6:00 AM Korea time")
    print("💡 Press Ctrl+C to stop the scheduler")
    print("-" * 50)
    
    main() 