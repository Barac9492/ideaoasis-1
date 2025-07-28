import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional
from datetime import datetime
import re

class IdeaBrowserScraper:
    def __init__(self):
        self.base_url = "https://www.ideabrowser.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    def get_startup_ideas(self, limit: int = 50) -> List[Dict]:
        """Get startup ideas from ideabrowser.com mimicking their framework"""
        ideas = []
        
        try:
            # Get the main page
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for idea containers based on ideabrowser.com structure
            # They typically use cards or grid layouts for ideas
            idea_containers = soup.find_all(['div', 'article'], class_=re.compile(r'idea|card|item|post|product'))
            
            if not idea_containers:
                # Fallback: look for any divs with startup-related content
                idea_containers = soup.find_all('div', string=re.compile(r'startup|idea|business|product', re.I))
            
            for container in idea_containers[:limit]:
                try:
                    idea = self._extract_idea_from_container(container)
                    if idea and self._is_startup_related(idea):
                        ideas.append(idea)
                        
                    # Rate limiting
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    print(f"Error extracting idea from container: {e}")
                    continue
            
            # If no ideas found from main page, try specific sections
            if not ideas:
                ideas.extend(self._get_ideas_from_sections())
                
        except Exception as e:
            print(f"Error scraping ideabrowser.com: {e}")
        
        return ideas
    
    def _extract_idea_from_container(self, container) -> Optional[Dict]:
        """Extract idea information from a container element mimicking ideabrowser.com structure"""
        try:
            # Try to find title (ideabrowser.com typically uses h2 or h3 for idea titles)
            title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            title = title_elem.get_text().strip() if title_elem else ""
            
            # Try to find description/content (ideabrowser.com uses p tags for descriptions)
            content_elem = container.find(['p', 'div', 'span'])
            content = content_elem.get_text().strip() if content_elem else ""
            
            # Try to find link (ideabrowser.com uses anchor tags for idea links)
            link_elem = container.find('a')
            url = link_elem.get('href', '') if link_elem else ""
            if url and not url.startswith('http'):
                url = self.base_url + url
            
            # Try to find date (ideabrowser.com might show when ideas were posted)
            date_elem = container.find(['time', 'span'], class_=re.compile(r'date|time'))
            date_text = date_elem.get_text().strip() if date_elem else ""
            
            # Try to find category/tags (ideabrowser.com categorizes ideas)
            category_elem = container.find(['span', 'div'], class_=re.compile(r'category|tag|label'))
            category = category_elem.get_text().strip() if category_elem else ""
            
            if title and content:
                return {
                    'title': title,
                    'content': content,
                    'url': url or self.base_url,
                    'score': 0,  # No score available from crawling
                    'comments_count': 0,
                    'created_utc': datetime.now().timestamp(),
                    'source_type': 'ideabrowser',
                    'category': category
                }
                
        except Exception as e:
            print(f"Error extracting idea data: {e}")
        
        return None
    
    def _get_ideas_from_sections(self) -> List[Dict]:
        """Get ideas from different sections of ideabrowser.com"""
        ideas = []
        sections = [
            '/ideas', 
            '/startups', 
            '/business-ideas', 
            '/trending',
            '/latest',
            '/popular',
            '/categories',
            '/tags'
        ]
        
        for section in sections:
            try:
                url = self.base_url + section
                response = requests.get(url, headers=self.headers, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for idea containers in this section
                containers = soup.find_all(['div', 'article'], class_=re.compile(r'idea|card|item|post|product'))
                
                for container in containers[:10]:  # Limit per section
                    idea = self._extract_idea_from_container(container)
                    if idea and self._is_startup_related(idea):
                        ideas.append(idea)
                
                time.sleep(random.uniform(1, 2))  # Be respectful
                
            except Exception as e:
                print(f"Error scraping section {section}: {e}")
                continue
        
        return ideas
    
    def get_ideas_by_category(self, category: str, limit: int = 20) -> List[Dict]:
        """Get ideas from a specific category (mimicking ideabrowser.com categorization)"""
        ideas = []
        
        try:
            # Try category-specific URLs
            category_urls = [
                f"{self.base_url}/category/{category}",
                f"{self.base_url}/tag/{category}",
                f"{self.base_url}/{category}",
                f"{self.base_url}/ideas/{category}"
            ]
            
            for url in category_urls:
                try:
                    response = requests.get(url, headers=self.headers, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        containers = soup.find_all(['div', 'article'], class_=re.compile(r'idea|card|item|post|product'))
                        
                        for container in containers[:limit//len(category_urls)]:
                            idea = self._extract_idea_from_container(container)
                            if idea and self._is_startup_related(idea):
                                ideas.append(idea)
                        
                        time.sleep(random.uniform(1, 2))
                        
                except Exception as e:
                    print(f"Error scraping category {category} from {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error getting ideas by category {category}: {e}")
        
        return ideas
    
    def _is_startup_related(self, idea: Dict) -> bool:
        """Check if idea is startup-related (mimicking ideabrowser.com filtering)"""
        title = idea.get('title', '').lower()
        content = idea.get('content', '').lower()
        category = idea.get('category', '').lower()
        
        startup_keywords = [
            'startup', 'saas', 'app', 'product', 'business', 'entrepreneur',
            'launch', 'idea', 'project', 'tool', 'service', 'platform',
            'marketplace', 'api', 'software', 'tech', 'innovation',
            'funding', 'venture', 'capital', 'accelerator', 'incubator',
            'side hustle', 'indie', 'bootstrapped', 'mvp', 'prototype'
        ]
        
        # Check if title, content, or category contains startup keywords
        text_to_check = f"{title} {content} {category}"
        return any(keyword in text_to_check for keyword in startup_keywords)
    
    def get_idea_details(self, url: str) -> Optional[Dict]:
        """Get detailed information about a specific idea (mimicking ideabrowser.com detail pages)"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract detailed information (ideabrowser.com detail page structure)
            title_elem = soup.find(['h1', 'h2', 'h3'])
            title = title_elem.get_text().strip() if title_elem else ""
            
            # Look for main content area
            content_selectors = [
                'article', 'main', '.content', '.post-content', '.entry-content',
                '.idea-content', '.description', '.summary', '.details'
            ]
            
            content = ""
            for selector in content_selectors:
                content_elem = soup.find(selector)
                if content_elem:
                    content = content_elem.get_text().strip()
                    if len(content) > 50:  # Only use if substantial content
                        break
            
            # Look for additional metadata
            category_elem = soup.find(['span', 'div'], class_=re.compile(r'category|tag|label'))
            category = category_elem.get_text().strip() if category_elem else ""
            
            if title and content:
                return {
                    'title': title,
                    'content': content,
                    'url': url,
                    'score': 0,
                    'comments_count': 0,
                    'created_utc': datetime.now().timestamp(),
                    'source_type': 'ideabrowser',
                    'category': category
                }
                
        except Exception as e:
            print(f"Error getting idea details from {url}: {e}")
        
        return None
    
    def search_ideas(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for ideas with specific keywords (mimicking ideabrowser.com search)"""
        ideas = []
        
        try:
            # Try to find search functionality
            search_urls = [
                f"{self.base_url}/search?q={query}",
                f"{self.base_url}/search/{query}",
                f"{self.base_url}/ideas/search?q={query}"
            ]
            
            for search_url in search_urls:
                try:
                    response = requests.get(search_url, headers=self.headers, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        containers = soup.find_all(['div', 'article'], class_=re.compile(r'idea|card|item|post|product'))
                        
                        for container in containers[:limit//len(search_urls)]:
                            idea = self._extract_idea_from_container(container)
                            if idea and self._is_startup_related(idea):
                                ideas.append(idea)
                        
                        time.sleep(random.uniform(1, 2))
                        
                except Exception as e:
                    print(f"Error searching ideas from {search_url}: {e}")
                    continue
                        
        except Exception as e:
            print(f"Error searching ideas: {e}")
        
        return ideas
    
    def get_trending_ideas(self, limit: int = 20) -> List[Dict]:
        """Get trending ideas (mimicking ideabrowser.com trending section)"""
        ideas = []
        
        try:
            trending_urls = [
                f"{self.base_url}/trending",
                f"{self.base_url}/popular",
                f"{self.base_url}/hot",
                f"{self.base_url}/featured"
            ]
            
            for url in trending_urls:
                try:
                    response = requests.get(url, headers=self.headers, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        containers = soup.find_all(['div', 'article'], class_=re.compile(r'idea|card|item|post|product'))
                        
                        for container in containers[:limit//len(trending_urls)]:
                            idea = self._extract_idea_from_container(container)
                            if idea and self._is_startup_related(idea):
                                ideas.append(idea)
                        
                        time.sleep(random.uniform(1, 2))
                        
                except Exception as e:
                    print(f"Error getting trending ideas from {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error getting trending ideas: {e}")
        
        return ideas 