#!/usr/bin/env python3
"""
IdeaOasis System Test

This script tests the main components of the IdeaOasis system:
1. Database connection and models
2. AI processor
3. Web scrapers (crawling-based)
4. Idea discovery agent

Usage:
    python test_system.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_database():
    """Test database connection and models"""
    print("🔍 Testing database connection...")
    try:
        from app.models import create_tables, get_db, Idea
        create_tables()
        
        # Test database connection
        db = next(get_db())
        idea_count = db.query(Idea).count()
        print(f"✅ Database connection successful. Found {idea_count} ideas in database.")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_ai_processor():
    """Test AI processor"""
    print("🤖 Testing AI processor...")
    try:
        from app.ai_processor import AIProcessor
        
        # Test with a sample idea
        sample_idea = {
            'title': 'AI-powered voice assistant for e-commerce',
            'content': 'A new startup is building an AI voice assistant specifically designed for e-commerce platforms. The assistant helps customers find products, compare prices, and complete purchases using natural language.',
            'url': 'https://example.com',
            'source_type': 'test'
        }
        
        processor = AIProcessor()
        result = processor.process_idea(sample_idea)
        
        if result and 'idea_title' in result and 'summary_kr' in result:
            print("✅ AI processor test successful")
            print(f"   Generated title: {result['idea_title']}")
            return True
        else:
            print("❌ AI processor test failed - invalid response format")
            return False
            
    except Exception as e:
        print(f"❌ AI processor test failed: {e}")
        return False

def test_scrapers():
    """Test web scrapers (crawling-based)"""
    print("🌐 Testing web scrapers...")
    
    scrapers_tested = 0
    scrapers_passed = 0
    
    # Test IdeaBrowser scraper
    try:
        from app.scrapers.ideabrowser_scraper import IdeaBrowserScraper
        ideabrowser_scraper = IdeaBrowserScraper()
        ideas = ideabrowser_scraper.get_startup_ideas(limit=5)
        if ideas:
            print(f"✅ IdeaBrowser scraper: {len(ideas)} ideas collected")
            scrapers_passed += 1
        else:
            print("⚠️ IdeaBrowser scraper: No ideas collected")
        scrapers_tested += 1
    except Exception as e:
        print(f"❌ IdeaBrowser scraper failed: {e}")
        scrapers_tested += 1
    
    # Test Hacker News scraper
    try:
        from app.scrapers.hackernews_scraper import HackerNewsScraper
        hn_scraper = HackerNewsScraper()
        ideas = hn_scraper.get_startup_ideas(limit=5)
        if ideas:
            print(f"✅ Hacker News scraper: {len(ideas)} ideas collected")
            scrapers_passed += 1
        else:
            print("⚠️ Hacker News scraper: No ideas collected")
        scrapers_tested += 1
    except Exception as e:
        print(f"❌ Hacker News scraper failed: {e}")
        scrapers_tested += 1
    
    # Test Product Hunt scraper
    try:
        from app.scrapers.producthunt_scraper import ProductHuntScraper
        ph_scraper = ProductHuntScraper()
        ideas = ph_scraper.get_today_products(limit=5)
        if ideas:
            print(f"✅ Product Hunt scraper: {len(ideas)} ideas collected")
            scrapers_passed += 1
        else:
            print("⚠️ Product Hunt scraper: No ideas collected")
        scrapers_tested += 1
    except Exception as e:
        print(f"❌ Product Hunt scraper failed: {e}")
        scrapers_tested += 1
    
    print(f"📊 Scraper test results: {scrapers_passed}/{scrapers_tested} passed")
    return scrapers_passed > 0

def test_idea_discovery():
    """Test idea discovery agent"""
    print("🔍 Testing idea discovery agent...")
    try:
        from app.idea_discovery_agent import IdeaDiscoveryAgent
        
        agent = IdeaDiscoveryAgent()
        
        # Test idea collection
        ideas = agent._collect_ideas_from_sources()
        if ideas:
            print(f"✅ Idea collection: {len(ideas)} ideas collected")
            
            # Test filtering
            filtered_ideas = agent._filter_and_rank_ideas(ideas)
            print(f"✅ Idea filtering: {len(filtered_ideas)} ideas passed filtering")
            
            return True
        else:
            print("⚠️ Idea discovery: No ideas collected")
            return False
            
    except Exception as e:
        print(f"❌ Idea discovery test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting IdeaOasis System Tests...")
    print("=" * 50)
    
    tests = [
        ("Database", test_database),
        ("AI Processor", test_ai_processor),
        ("Web Scrapers", test_scrapers),
        ("Idea Discovery", test_idea_discovery)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Set up your .env file with OpenAI API key")
        print("2. Run 'python run_web.py' to start the web application")
        print("3. Run 'python run_scheduler.py' to start the daily scheduler")
    else:
        print("⚠️ Some tests failed. Please check the configuration and try again.")
    
    return passed == total

if __name__ == "__main__":
    main() 