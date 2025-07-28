import random
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.scrapers.ideabrowser_scraper import IdeaBrowserScraper
from app.scrapers.hackernews_scraper import HackerNewsScraper
from app.scrapers.producthunt_scraper import ProductHuntScraper
from app.ai_processor import AIProcessor
from app.models import Idea, get_db

class IdeaDiscoveryAgent:
    def __init__(self):
        self.ideabrowser_scraper = IdeaBrowserScraper()
        self.hn_scraper = HackerNewsScraper()
        self.ph_scraper = ProductHuntScraper()
        self.ai_processor = AIProcessor()
        
        # Define idea categories similar to ideabrowser.com
        self.categories = [
            'saas', 'mobile-app', 'web-app', 'ecommerce', 'fintech',
            'healthtech', 'edtech', 'ai-ml', 'blockchain', 'social',
            'productivity', 'marketing', 'analytics', 'automation',
            'marketplace', 'subscription', 'freemium', 'b2b', 'b2c'
        ]
        
    def discover_daily_idea(self) -> Optional[Dict]:
        """Main method to discover and process one daily idea"""
        print("🔍 Starting daily idea discovery...")
        
        # Step 1: Collect ideas from multiple sources
        all_ideas = self._collect_ideas_from_sources()
        
        if not all_ideas:
            print("❌ No ideas collected from sources")
            return None
        
        # Step 2: Filter and rank ideas
        filtered_ideas = self._filter_and_rank_ideas(all_ideas)
        
        if not filtered_ideas:
            print("❌ No ideas passed filtering")
            return None
        
        # Step 3: Check for duplicates in database
        unique_ideas = self._check_duplicates(filtered_ideas)
        
        if not unique_ideas:
            print("❌ All ideas are duplicates")
            return None
        
        # Step 4: Select the best idea
        best_idea = self._select_best_idea(unique_ideas)
        
        if not best_idea:
            print("❌ Could not select best idea")
            return None
        
        # Step 5: Process with AI
        processed_idea = self.ai_processor.process_idea(best_idea)
        
        if processed_idea:
            print(f"✅ Successfully processed idea: {processed_idea['idea_title']}")
            return processed_idea
        else:
            print("❌ Failed to process idea with AI")
            return None
    
    def _collect_ideas_from_sources(self) -> List[Dict]:
        """Collect ideas from all available sources mimicking ideabrowser.com approach"""
        all_ideas = []
        
        # Collect from IdeaBrowser (primary source) - mimicking their framework
        try:
            print("🌐 Collecting from IdeaBrowser.com...")
            
            # Try different approaches like ideabrowser.com
            ideabrowser_ideas = []
            
            # Get general ideas
            general_ideas = self.ideabrowser_scraper.get_startup_ideas()
            ideabrowser_ideas.extend(general_ideas)
            
            # Get trending ideas
            trending_ideas = self.ideabrowser_scraper.get_trending_ideas()
            ideabrowser_ideas.extend(trending_ideas)
            
            # Get ideas by category (like ideabrowser.com categorization)
            for category in random.sample(self.categories, 3):  # Try 3 random categories
                category_ideas = self.ideabrowser_scraper.get_ideas_by_category(category)
                ideabrowser_ideas.extend(category_ideas)
            
            all_ideas.extend(ideabrowser_ideas)
            print(f"✅ Collected {len(ideabrowser_ideas)} ideas from IdeaBrowser")
            
        except Exception as e:
            print(f"❌ Error collecting from IdeaBrowser: {e}")
        
        # Collect from Hacker News
        try:
            print("📰 Collecting from Hacker News...")
            hn_ideas = self.hn_scraper.get_startup_ideas()
            all_ideas.extend(hn_ideas)
            print(f"✅ Collected {len(hn_ideas)} ideas from Hacker News")
            
            # Also get Show HN posts
            show_hn_ideas = self.hn_scraper.get_show_hn_posts()
            all_ideas.extend(show_hn_ideas)
            print(f"✅ Collected {len(show_hn_ideas)} Show HN ideas")
        except Exception as e:
            print(f"❌ Error collecting from Hacker News: {e}")
        
        # Collect from Product Hunt
        try:
            print("🚀 Collecting from Product Hunt...")
            ph_ideas = self.ph_scraper.get_today_products()
            all_ideas.extend(ph_ideas)
            print(f"✅ Collected {len(ph_ideas)} ideas from Product Hunt")
        except Exception as e:
            print(f"❌ Error collecting from Product Hunt: {e}")
        
        return all_ideas
    
    def _filter_and_rank_ideas(self, ideas: List[Dict]) -> List[Dict]:
        """Filter and rank ideas based on quality criteria (mimicking ideabrowser.com approach)"""
        filtered_ideas = []
        
        for idea in ideas:
            score = self._calculate_idea_score(idea)
            if score > 0:  # Only include ideas with positive scores
                idea['quality_score'] = score
                filtered_ideas.append(idea)
        
        # Sort by quality score (highest first)
        filtered_ideas.sort(key=lambda x: x['quality_score'], reverse=True)
        
        print(f"✅ Filtered to {len(filtered_ideas)} high-quality ideas")
        return filtered_ideas
    
    def _calculate_idea_score(self, idea: Dict) -> float:
        """Calculate a quality score for an idea (mimicking ideabrowser.com scoring)"""
        score = 0.0
        
        # Base score from source engagement
        if idea.get('score', 0) > 0:
            score += min(idea['score'] / 100, 5)  # Cap at 5 points
        
        if idea.get('comments_count', 0) > 0:
            score += min(idea['comments_count'] / 10, 3)  # Cap at 3 points
        
        # Bonus for specific source types (mimicking ideabrowser.com priorities)
        source_type = idea.get('source_type', '')
        if 'ideabrowser' in source_type:
            score += 4  # Primary source gets highest bonus
        elif 'showhn' in source_type:
            score += 3  # Show HN posts are often actual launches
        elif 'producthunt' in source_type:
            score += 2.5  # Product Hunt products are validated
        elif 'hackernews' in source_type:
            score += 2  # Hacker News stories
        
        # Bonus for category relevance (like ideabrowser.com categorization)
        category = idea.get('category', '').lower()
        if category and any(cat in category for cat in self.categories):
            score += 1.5  # Bonus for categorized ideas
        
        # Bonus for recent content (within last 24 hours)
        if idea.get('created_utc'):
            created_time = datetime.fromtimestamp(idea['created_utc'])
            if datetime.now() - created_time < timedelta(hours=24):
                score += 1
        
        # Content quality scoring (mimicking ideabrowser.com quality standards)
        content_length = len(idea.get('content', ''))
        if content_length < 50:
            score -= 2  # Penalty for very short content
        elif content_length > 200:
            score += 1.5  # Bonus for comprehensive content
        elif content_length > 500:
            score += 2  # Bonus for very detailed content
        
        # Bonus for specific keywords that indicate high-quality ideas
        title_content = f"{idea.get('title', '')} {idea.get('content', '')}".lower()
        quality_keywords = ['mvp', 'prototype', 'launch', 'beta', 'alpha', 'funding', 'revenue']
        if any(keyword in title_content for keyword in quality_keywords):
            score += 1
        
        return max(score, 0)  # Don't allow negative scores
    
    def _check_duplicates(self, ideas: List[Dict]) -> List[Dict]:
        """Check for duplicates in the database"""
        db = next(get_db())
        unique_ideas = []
        
        try:
            for idea in ideas:
                # Create a temporary title for checking
                temp_title = idea.get('title', '')[:100]
                
                # Check if this idea is already in the database
                if not self.ai_processor.check_duplicate(temp_title, db):
                    unique_ideas.append(idea)
                else:
                    print(f"⚠️ Skipping duplicate: {temp_title[:50]}...")
        finally:
            db.close()
        
        print(f"✅ Found {len(unique_ideas)} unique ideas")
        return unique_ideas
    
    def _select_best_idea(self, ideas: List[Dict]) -> Optional[Dict]:
        """Select the best idea from the filtered list (mimicking ideabrowser.com selection)"""
        if not ideas:
            return None
        
        # Prioritize ideabrowser.com ideas if available
        ideabrowser_ideas = [idea for idea in ideas if 'ideabrowser' in idea.get('source_type', '')]
        if ideabrowser_ideas:
            best_idea = ideabrowser_ideas[0]
            print(f"🎯 Selected ideabrowser idea: {best_idea.get('title', '')[:50]}...")
            return best_idea
        
        # Otherwise, select the highest scoring idea
        best_idea = ideas[0]
        print(f"🎯 Selected best idea: {best_idea.get('title', '')[:50]}...")
        return best_idea
    
    def get_ideas_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Get ideas from a specific category (mimicking ideabrowser.com category browsing)"""
        ideas = []
        
        try:
            # Get ideas from ideabrowser.com by category
            category_ideas = self.ideabrowser_scraper.get_ideas_by_category(category, limit)
            ideas.extend(category_ideas)
            
            # Also search for category-related ideas in other sources
            search_terms = [category, f"{category} startup", f"{category} app"]
            for term in search_terms:
                search_ideas = self.ideabrowser_scraper.search_ideas(term, limit//len(search_terms))
                ideas.extend(search_ideas)
                
        except Exception as e:
            print(f"❌ Error getting ideas by category {category}: {e}")
        
        return ideas
    
    def save_idea_to_database(self, processed_idea: Dict) -> bool:
        """Save the processed idea to the database"""
        try:
            db = next(get_db())
            
            # Create new idea record
            new_idea = Idea(
                idea_title=processed_idea['idea_title'],
                source_url=processed_idea['source_url'],
                summary_kr=processed_idea['summary_kr'],
                published_at=datetime.fromisoformat(processed_idea['published_at']),
                language=processed_idea['language'],
                source_type=processed_idea['source_type'],
                archived=False
            )
            
            db.add(new_idea)
            db.commit()
            
            print(f"💾 Saved idea to database: {new_idea.idea_title}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving idea to database: {e}")
            return False
        finally:
            db.close()
    
    def archive_old_ideas(self):
        """Archive ideas older than 24 hours"""
        try:
            db = next(get_db())
            
            # Find ideas older than 24 hours that aren't archived
            yesterday = datetime.now() - timedelta(hours=24)
            old_ideas = db.query(Idea).filter(
                Idea.archived == False,
                Idea.created_at < yesterday
            ).all()
            
            for idea in old_ideas:
                idea.archived = True
            
            db.commit()
            print(f"📦 Archived {len(old_ideas)} old ideas")
            
        except Exception as e:
            print(f"❌ Error archiving old ideas: {e}")
        finally:
            db.close() 