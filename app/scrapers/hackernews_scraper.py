import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional
from datetime import datetime
import re

class HackerNewsScraper:
    def __init__(self):
        self.base_url = "https://news.ycombinator.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def get_startup_ideas(self, limit: int = 30) -> List[Dict]:
        """Get startup-related stories from Hacker News by crawling"""
        ideas = []
        
        try:
            # Get the main page
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find story rows (Hacker News uses specific structure)
            story_rows = soup.find_all('tr', class_='athing')
            
            for row in story_rows[:limit]:
                try:
                    idea = self._extract_idea_from_row(row)
                    if idea and self._is_startup_related(idea):
                        ideas.append(idea)
                        
                    # Rate limiting
                    time.sleep(random.uniform(0.1, 0.3))
                    
                except Exception as e:
                    print(f"Error extracting idea from row: {e}")
                    continue
            
            # Also get Show HN posts
            show_hn_ideas = self.get_show_hn_posts(limit // 2)
            ideas.extend(show_hn_ideas)
            
        except Exception as e:
            print(f"Error scraping Hacker News: {e}")
        
        return ideas
    
    def _extract_idea_from_row(self, row) -> Optional[Dict]:
        """Extract idea information from a Hacker News story row"""
        try:
            # Find the title link
            title_elem = row.find('a', class_='storylink')
            if not title_elem:
                return None
                
            title = title_elem.get_text().strip()
            url = title_elem.get('href', '')
            
            # Get the next row for metadata (score, comments, etc.)
            metadata_row = row.find_next_sibling('tr')
            if not metadata_row:
                return None
                
            # Extract score
            score_elem = metadata_row.find('span', class_='score')
            score = 0
            if score_elem:
                score_text = score_elem.get_text()
                score_match = re.search(r'(\d+)', score_text)
                if score_match:
                    score = int(score_match.group(1))
            
            # Extract comments count
            comments_elem = metadata_row.find('a', string=re.compile(r'comment'))
            comments_count = 0
            if comments_elem:
                comments_text = comments_elem.get_text()
                comments_match = re.search(r'(\d+)', comments_text)
                if comments_match:
                    comments_count = int(comments_match.group(1))
            
            # Get story ID for detailed view
            story_id = row.get('id', '')
            
            return {
                'title': title,
                'content': '',  # Will be filled by get_idea_details if needed
                'url': url,
                'score': score,
                'comments_count': comments_count,
                'created_utc': datetime.now().timestamp(),
                'story_id': story_id,
                'source_type': 'hackernews'
            }
            
        except Exception as e:
            print(f"Error extracting idea from row: {e}")
        
        return None
    
    def get_show_hn_posts(self, limit: int = 15) -> List[Dict]:
        """Get 'Show HN' posts which are often startup launches"""
        ideas = []
        
        try:
            # Get Show HN page
            show_hn_url = f"{self.base_url}/show"
            response = requests.get(show_hn_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            story_rows = soup.find_all('tr', class_='athing')
            
            for row in story_rows[:limit]:
                try:
                    idea = self._extract_idea_from_row(row)
                    if idea:
                        idea['source_type'] = 'hackernews_showhn'
                        ideas.append(idea)
                        
                    time.sleep(random.uniform(0.1, 0.3))
                    
                except Exception as e:
                    print(f"Error extracting Show HN idea: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Show HN: {e}")
        
        return ideas
    
    def _is_startup_related(self, idea: Dict) -> bool:
        """Check if story is startup-related"""
        title = idea.get('title', '').lower()
        content = idea.get('content', '').lower()
        
        startup_keywords = [
            'startup', 'saas', 'app', 'product', 'business', 'entrepreneur',
            'launch', 'idea', 'project', 'tool', 'service', 'platform',
            'marketplace', 'api', 'software', 'tech', 'innovation',
            'funding', 'venture', 'capital', 'ycombinator', 'accelerator',
            'show hn', 'indie', 'bootstrapped', 'side project'
        ]
        
        # Check if title or content contains startup keywords
        text_to_check = f"{title} {content}"
        return any(keyword in text_to_check for keyword in startup_keywords)
    
    def get_idea_details(self, url: str) -> Optional[Dict]:
        """Get detailed information about a specific idea"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find(['h1', 'h2', 'h3', 'title'])
            title = title_elem.get_text().strip() if title_elem else ""
            
            # Extract content (try different selectors)
            content_selectors = [
                'article', 'main', '.content', '.post-content', '.entry-content',
                'p', '.description', '.summary'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.find(selector)
                if content_elem:
                    content = content_elem.get_text().strip()
                    if len(content) > 50:  # Only use if substantial content
                        break
            
            if title and content:
                return {
                    'title': title,
                    'content': content,
                    'url': url,
                    'score': 0,
                    'comments_count': 0,
                    'created_utc': datetime.now().timestamp(),
                    'source_type': 'hackernews'
                }
                
        except Exception as e:
            print(f"Error getting idea details from {url}: {e}")
        
        return None
    
    def get_trending_stories(self, limit: int = 20) -> List[Dict]:
        """Get trending stories from Hacker News"""
        ideas = []
        
        try:
            # Get the main page (already sorted by popularity)
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            story_rows = soup.find_all('tr', class_='athing')
            
            for row in story_rows[:limit]:
                try:
                    idea = self._extract_idea_from_row(row)
                    if idea and self._is_startup_related(idea):
                        ideas.append(idea)
                        
                    time.sleep(random.uniform(0.1, 0.3))
                    
                except Exception as e:
                    print(f"Error extracting trending story: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping trending stories: {e}")
        
        return ideas 