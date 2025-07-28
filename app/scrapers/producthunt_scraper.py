import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional
from datetime import datetime
import re

class ProductHuntScraper:
    def __init__(self):
        self.base_url = "https://www.producthunt.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def get_today_products(self, limit: int = 50) -> List[Dict]:
        """Get today's products from Product Hunt by crawling"""
        ideas = []
        
        try:
            # Get today's products page
            response = requests.get(f"{self.base_url}/today", headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for product containers
            product_containers = soup.find_all(['div', 'article'], class_=re.compile(r'product|item|card|post'))
            
            if not product_containers:
                # Fallback: look for any divs with product-related content
                product_containers = soup.find_all('div', string=re.compile(r'product|app|tool|saas', re.I))
            
            for container in product_containers[:limit]:
                try:
                    idea = self._extract_idea_from_container(container)
                    if idea and self._is_startup_related(idea):
                        ideas.append(idea)
                        
                    # Rate limiting
                    time.sleep(random.uniform(0.5, 1.0))
                    
                except Exception as e:
                    print(f"Error extracting idea from container: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Product Hunt: {e}")
        
        return ideas
    
    def _extract_idea_from_container(self, container) -> Optional[Dict]:
        """Extract idea information from a product container"""
        try:
            # Try to find title
            title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            title = title_elem.get_text().strip() if title_elem else ""
            
            # Try to find description/tagline
            description_elem = container.find(['p', 'div', 'span'], class_=re.compile(r'description|tagline|summary'))
            description = description_elem.get_text().strip() if description_elem else ""
            
            # Try to find link
            link_elem = container.find('a')
            url = link_elem.get('href', '') if link_elem else ""
            if url and not url.startswith('http'):
                url = self.base_url + url
            
            # Try to find vote count
            vote_elem = container.find(['span', 'div'], class_=re.compile(r'vote|score|count'))
            vote_count = 0
            if vote_elem:
                vote_text = vote_elem.get_text()
                vote_match = re.search(r'(\d+)', vote_text)
                if vote_match:
                    vote_count = int(vote_match.group(1))
            
            # Try to find comment count
            comment_elem = container.find(['span', 'div'], class_=re.compile(r'comment|reply'))
            comment_count = 0
            if comment_elem:
                comment_text = comment_elem.get_text()
                comment_match = re.search(r'(\d+)', comment_text)
                if comment_match:
                    comment_count = int(comment_match.group(1))
            
            if title and description:
                return {
                    'title': title,
                    'content': description,
                    'url': url or self.base_url,
                    'score': vote_count,
                    'comments_count': comment_count,
                    'created_utc': datetime.now().timestamp(),
                    'source_type': 'producthunt'
                }
                
        except Exception as e:
            print(f"Error extracting idea data: {e}")
        
        return None
    
    def get_trending_products(self, days: int = 7, limit: int = 30) -> List[Dict]:
        """Get trending products from Product Hunt"""
        ideas = []
        
        try:
            # Try different trending pages
            trending_urls = [
                f"{self.base_url}/trending",
                f"{self.base_url}/popular",
                f"{self.base_url}/top"
            ]
            
            for url in trending_urls:
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    containers = soup.find_all(['div', 'article'], class_=re.compile(r'product|item|card|post'))
                    
                    for container in containers[:limit//len(trending_urls)]:
                        idea = self._extract_idea_from_container(container)
                        if idea and self._is_startup_related(idea):
                            ideas.append(idea)
                    
                    time.sleep(random.uniform(1, 2))  # Be respectful
                    
                except Exception as e:
                    print(f"Error scraping trending URL {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping trending products: {e}")
        
        return ideas
    
    def _is_startup_related(self, idea: Dict) -> bool:
        """Check if product is startup-related"""
        title = idea.get('title', '').lower()
        content = idea.get('content', '').lower()
        
        startup_keywords = [
            'saas', 'app', 'tool', 'platform', 'service', 'software',
            'business', 'productivity', 'automation', 'api', 'integration',
            'analytics', 'marketing', 'sales', 'crm', 'project management',
            'collaboration', 'communication', 'workflow', 'dashboard',
            'startup', 'product', 'launch', 'beta', 'alpha'
        ]
        
        # Check if title or content contains startup keywords
        text_to_check = f"{title} {content}"
        return any(keyword in text_to_check for keyword in startup_keywords)
    
    def get_product_details(self, url: str) -> Optional[Dict]:
        """Get detailed information about a specific product"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find(['h1', 'h2', 'h3', 'title'])
            title = title_elem.get_text().strip() if title_elem else ""
            
            # Extract description
            description_elem = soup.find(['p', 'div'], class_=re.compile(r'description|summary|content'))
            description = description_elem.get_text().strip() if description_elem else ""
            
            # Extract additional content
            content_elem = soup.find(['article', 'main', 'div'], class_=re.compile(r'content|body|description'))
            content = content_elem.get_text().strip() if content_elem else ""
            
            # Combine description and content
            full_content = f"{description}\n\n{content}".strip()
            
            if title and full_content:
                return {
                    'title': title,
                    'content': full_content,
                    'url': url,
                    'score': 0,
                    'comments_count': 0,
                    'created_utc': datetime.now().timestamp(),
                    'source_type': 'producthunt'
                }
                
        except Exception as e:
            print(f"Error getting product details from {url}: {e}")
        
        return None
    
    def search_products(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for products with specific keywords"""
        ideas = []
        
        try:
            # Try to find search functionality
            search_url = f"{self.base_url}/search?q={query}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                containers = soup.find_all(['div', 'article'], class_=re.compile(r'product|item|card|post'))
                
                for container in containers[:limit]:
                    idea = self._extract_idea_from_container(container)
                    if idea and self._is_startup_related(idea):
                        ideas.append(idea)
                        
        except Exception as e:
            print(f"Error searching products: {e}")
        
        return ideas 