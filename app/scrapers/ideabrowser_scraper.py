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
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

    def get_startup_ideas(self, limit: int = 50) -> List[Dict]:
        """Get startup ideas from ideabrowser.com"""
        ideas = []
        try:
            print(f"Scraping {self.base_url}...")
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for idea containers
            selectors = [
                'article',
                '.idea-card',
                '.card',
                '.post',
                '.item',
                '[class*="idea"]',
                '[class*="card"]',
                '[class*="post"]'
            ]
            
            idea_containers = []
            for selector in selectors:
                containers = soup.select(selector)
                if containers:
                    idea_containers = containers
                    print(f"Found {len(containers)} containers using selector: {selector}")
                    break
            
            if not idea_containers:
                # Fallback: look for any div with text content
                idea_containers = soup.find_all('div', string=re.compile(r'idea|startup|business|app|tool|saas', re.I))
                print(f"Fallback: Found {len(idea_containers)} containers with startup-related text")
            
            for container in idea_containers[:limit]:
                try:
                    idea = self._extract_idea_from_container(container)
                    if idea and self._is_startup_related(idea):
                        ideas.append(idea)
                        print(f"Extracted idea: {idea['title'][:50]}...")
                    time.sleep(random.uniform(0.5, 1.0))
                except Exception as e:
                    print(f"Error extracting idea from container: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping IdeaBrowser: {e}")
            
        print(f"Total ideas extracted: {len(ideas)}")
        return ideas

    def _extract_idea_from_container(self, container) -> Optional[Dict]:
        """Extract idea information from a container element"""
        try:
            # Try multiple selectors for title
            title_selectors = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', '.title', '.heading', '[class*="title"]']
            title = ""
            for selector in title_selectors:
                title_elem = container.select_one(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    break
            
            # Try multiple selectors for content
            content_selectors = ['p', '.content', '.description', '.summary', '[class*="content"]', '[class*="desc"]']
            content = ""
            for selector in content_selectors:
                content_elem = container.select_one(selector)
                if content_elem:
                    content = content_elem.get_text().strip()
                    if len(content) > 20:  # Ensure we have meaningful content
                        break
            
            # Extract link
            link_elem = container.find('a')
            url = link_elem.get('href', '') if link_elem else ""
            if url and not url.startswith('http'):
                url = self.base_url + url
            
            # Extract date
            date_selectors = ['time', '.date', '.published', '[class*="date"]']
            date_text = ""
            for selector in date_selectors:
                date_elem = container.select_one(selector)
                if date_elem:
                    date_text = date_elem.get_text().strip()
                    break
            
            # Extract category/tags
            category_selectors = ['.category', '.tag', '.label', '[class*="category"]', '[class*="tag"]']
            category = ""
            for selector in category_selectors:
                category_elem = container.select_one(selector)
                if category_elem:
                    category = category_elem.get_text().strip()
                    break
            
            if title and content:
                return {
                    'title': title,
                    'content': content,
                    'url': url or self.base_url,
                    'score': 0,
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
                print(f"Scraping section: {url}")
                response = requests.get(url, headers=self.headers, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try multiple selectors
                selectors = ['article', '.idea-card', '.card', '.post', '.item']
                containers = []
                for selector in selectors:
                    containers = soup.select(selector)
                    if containers:
                        break
                
                for container in containers[:10]:
                    idea = self._extract_idea_from_container(container)
                    if idea and self._is_startup_related(idea):
                        ideas.append(idea)
                    time.sleep(random.uniform(0.1, 0.3))
            except Exception as e:
                print(f"Error scraping section {section}: {e}")
                continue
        return ideas

    def get_ideas_by_category(self, category: str, limit: int = 20) -> List[Dict]:
        """Get ideas from a specific category"""
        ideas = []
        try:
            category_urls = [
                f"{self.base_url}/category/{category}",
                f"{self.base_url}/tag/{category}",
                f"{self.base_url}/{category}",
                f"{self.base_url}/ideas/{category}"
            ]
            
            for url in category_urls:
                try:
                    print(f"Scraping category: {url}")
                    response = requests.get(url, headers=self.headers, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        selectors = ['article', '.idea-card', '.card', '.post', '.item']
                        containers = []
                        for selector in selectors:
                            containers = soup.select(selector)
                            if containers:
                                break
                        
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
        """Check if idea is startup-related"""
        title = idea.get('title', '').lower()
        content = idea.get('content', '').lower()
        category = idea.get('category', '').lower()
        
        startup_keywords = [
            'startup', 'saas', 'app', 'product', 'business', 'entrepreneur',
            'launch', 'idea', 'project', 'tool', 'service', 'platform',
            'marketplace', 'api', 'software', 'tech', 'innovation',
            'funding', 'venture', 'capital', 'accelerator', 'incubator',
            'side hustle', 'indie', 'bootstrapped', 'mvp', 'prototype',
            'revenue', 'profit', 'customer', 'user', 'growth', 'scale'
        ]
        
        text_to_check = f"{title} {content} {category}"
        return any(keyword in text_to_check for keyword in startup_keywords)

    def get_idea_details(self, url: str) -> Optional[Dict]:
        """Get detailed information about a specific idea"""
        try:
            print(f"Getting details from: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_selectors = ['h1', 'h2', 'h3', '.title', '.heading']
            title = ""
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    break
            
            # Extract content
            content_selectors = [
                'article', 'main', '.content', '.post-content', '.entry-content',
                '.idea-content', '.description', '.summary', '.details'
            ]
            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text().strip()
                    if len(content) > 50:
                        break
            
            # Extract category
            category_selectors = ['.category', '.tag', '.label', '[class*="category"]']
            category = ""
            for selector in category_selectors:
                category_elem = soup.select_one(selector)
                if category_elem:
                    category = category_elem.get_text().strip()
                    break
            
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
        """Search for ideas with specific keywords"""
        ideas = []
        try:
            search_urls = [
                f"{self.base_url}/search?q={query}",
                f"{self.base_url}/search/{query}",
                f"{self.base_url}/ideas/search?q={query}"
            ]
            
            for search_url in search_urls:
                try:
                    print(f"Searching: {search_url}")
                    response = requests.get(search_url, headers=self.headers, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        selectors = ['article', '.idea-card', '.card', '.post', '.item']
                        containers = []
                        for selector in selectors:
                            containers = soup.select(selector)
                            if containers:
                                break
                        
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
        """Get trending ideas"""
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
                    print(f"Getting trending ideas from: {url}")
                    response = requests.get(url, headers=self.headers, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        selectors = ['article', '.idea-card', '.card', '.post', '.item']
                        containers = []
                        for selector in selectors:
                            containers = soup.select(selector)
                            if containers:
                                break
                        
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