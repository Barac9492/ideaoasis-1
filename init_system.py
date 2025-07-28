#!/usr/bin/env python3
"""
IdeaOasis System Initialization

This script helps first-time users set up the IdeaOasis system:
1. Creates necessary directories
2. Initializes database
3. Validates environment variables
4. Runs basic tests

Usage:
    python init_system.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("📦 Checking dependencies...")
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'python-dotenv',
        'requests', 'beautifulsoup4', 'openai', 'schedule',
        'pydantic', 'jinja2', 'pytz'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def setup_environment():
    """Set up environment variables"""
    print("🔧 Setting up environment...")
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        env_example = Path('env.example')
        if env_example.exists():
            print("📝 Creating .env file from template...")
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ .env file created. Please edit it with your API keys.")
        else:
            print("❌ env.example file not found")
            return False
    else:
        print("✅ .env file already exists")
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please add them to your .env file")
        return False
    
    print("✅ Environment variables are properly configured")
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        'app/templates',
        'app/scrapers',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")
    return True

def initialize_database():
    """Initialize database tables"""
    print("🗄️ Initializing database...")
    
    try:
        # Add app directory to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        
        from app.models import create_tables
        create_tables()
        print("✅ Database tables created")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def run_basic_tests():
    """Run basic system tests"""
    print("🧪 Running basic tests...")
    
    try:
        # Import and test basic components
        from app.models import get_db, Idea
        from app.ai_processor import AIProcessor
        
        # Test database connection
        db = next(get_db())
        idea_count = db.query(Idea).count()
        print(f"✅ Database connection: {idea_count} ideas found")
        db.close()
        
        # Test AI processor (without making API calls)
        processor = AIProcessor()
        print("✅ AI processor initialized")
        
        return True
    except Exception as e:
        print(f"❌ Basic tests failed: {e}")
        return False

def main():
    """Main initialization function"""
    print("🚀 Initializing IdeaOasis System...")
    print("=" * 50)
    
    steps = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment", setup_environment),
        ("Directories", create_directories),
        ("Database", initialize_database),
        ("Basic Tests", run_basic_tests)
    ]
    
    passed = 0
    total = len(steps)
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if step_func():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 Initialization Results: {passed}/{total} steps completed")
    
    if passed == total:
        print("\n🎉 System initialization completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Edit your .env file with API keys if needed")
        print("2. Run 'python test_system.py' to verify everything works")
        print("3. Run 'python run_web.py' to start the web application")
        print("4. Run 'python run_scheduler.py' to start the daily scheduler")
        print("\n📚 For more information, see README.md")
    else:
        print("\n⚠️ Some initialization steps failed. Please check the errors above.")
        print("Make sure all dependencies are installed and environment variables are set.")
    
    return passed == total

if __name__ == "__main__":
    main() 