import openai
import os
from typing import Dict, Optional
from datetime import datetime
import json

class AIProcessor:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        else:
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def process_idea(self, idea_data: Dict) -> Optional[Dict]:
        """Process an idea through AI for translation and summarization"""
        try:
            # Create the prompt for the AI
            prompt = self._create_prompt(idea_data)
            
            # Get AI response
            response = self._get_ai_response(prompt)
            
            if response:
                return {
                    'idea_title': response.get('idea_title', idea_data.get('title', '')),
                    'source_url': idea_data.get('url', ''),
                    'summary_kr': response.get('summary_kr', ''),
                    'published_at': datetime.now().isoformat(),
                    'language': 'ko',
                    'source_type': idea_data.get('source_type', ''),
                    'archived': False
                }
                
        except Exception as e:
            print(f"Error processing idea with AI: {e}")
        
        return None
    
    def _create_prompt(self, idea_data: Dict) -> str:
        """Create the prompt for AI processing (mimicking ideabrowser.com format)"""
        title = idea_data.get('title', '')
        content = idea_data.get('content', '')
        source_type = idea_data.get('source_type', '')
        category = idea_data.get('category', '')
        
        prompt = f"""
당신은 한국의 창업자들을 위해 운영되는 아이디어 발굴 플랫폼 "IdeaOasis"의 전담 에이전트입니다.
ideabrowser.com의 프레임워크와 스타일을 참고하여 해외 아이디어를 한국어로 요약, 번역, 맥락화해주세요.

다음 해외 아이디어를 처리해주세요:

제목: {title}
내용: {content}
출처: {source_type}
카테고리: {category}

다음 포맷으로 JSON 형태로 응답해주세요:

{{
  "idea_title": "한국어 제목 (간결하고 임팩트 있게)",
  "summary_kr": "💡 오늘의 해외 아이디어

📋 아이디어 개요
• [간단한 소개 한 줄]

🎯 핵심 가치 제안
• [이 아이디어가 해결하는 문제와 제공하는 가치]

⚙️ 기술적 구현
• [기능, 기술 스택, 수익모델 등 구조 요약]

🌏 한국 시장 적용 방안
• [한국적 맥락에서의 응용 방안. 타겟/세분화 가능성/문화적 제약 등 포함]

💼 비즈니스 모델
• [수익화 전략, 고객 세그먼트, 경쟁 우위]

🚀 실행 로드맵
• [MVP 개발, 런칭 전략, 성장 계획]"
}}

요구사항:
1. ideabrowser.com의 전문적이고 구조화된 프레임워크를 따라 작성
2. 스타트업 창업자를 위한 실행 가능한 아이디어로 제시
3. 한국 시장에서의 적용 가능성과 문화적 맥락을 강조
4. 비즈니스 모델과 실행 계획을 포함
5. GPT 수준의 고품질 한국어 사용
6. 뉴스 기사가 아닌 실행 가능한 비즈니스 아이디어로 구성
"""
        
        return prompt
    
    def _get_ai_response(self, prompt: str) -> Optional[Dict]:
        """Get response from OpenAI API using the new v1.0+ format"""
        try:
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a startup idea analyst and translator for Korean entrepreneurs. Always respond in valid JSON format. Follow ideabrowser.com's professional framework for presenting business ideas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response
                return self._fallback_response(content)
                
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return None
    
    def _fallback_response(self, content: str) -> Dict:
        """Create a fallback response if JSON parsing fails (mimicking ideabrowser.com format)"""
        return {
            'idea_title': '해외 스타트업 아이디어',
            'summary_kr': f"""
💡 오늘의 해외 아이디어

📋 아이디어 개요
• {content[:100]}...

🎯 핵심 가치 제안
• 해외에서 주목받고 있는 혁신적인 아이디어입니다.

⚙️ 기술적 구현
• 자세한 내용은 원문을 참고하세요.

🌏 한국 시장 적용 방안
• 한국 시장에 맞게 로컬라이징하여 적용할 수 있습니다.

💼 비즈니스 모델
• 한국 시장 특성을 고려한 수익화 전략이 필요합니다.

🚀 실행 로드맵
• MVP 개발부터 단계적 런칭을 고려해보세요.
"""
        }
    
    def check_duplicate(self, idea_title: str, db_session) -> bool:
        """Check if an idea is already in the database (last 30 days)"""
        from datetime import datetime, timedelta
        from app.models import Idea
        
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # Check for exact title match
        existing_idea = db_session.query(Idea).filter(
            Idea.idea_title == idea_title,
            Idea.created_at >= thirty_days_ago
        ).first()
        
        if existing_idea:
            return True
        
        # Check for keyword matches (mimicking ideabrowser.com's duplicate detection)
        keywords = idea_title.lower().split()
        for keyword in keywords:
            if len(keyword) > 3:  # Only check meaningful keywords
                existing_ideas = db_session.query(Idea).filter(
                    Idea.idea_title.ilike(f"%{keyword}%"),
                    Idea.created_at >= thirty_days_ago
                ).all()
                
                if existing_ideas:
                    return True
        
        return False
    
    def categorize_idea(self, idea_data: Dict) -> str:
        """Categorize an idea based on its content (mimicking ideabrowser.com categorization)"""
        title = idea_data.get('title', '').lower()
        content = idea_data.get('content', '').lower()
        category = idea_data.get('category', '').lower()
        
        # Define categories similar to ideabrowser.com
        categories = {
            'saas': ['saas', 'software', 'subscription', 'platform'],
            'mobile-app': ['mobile', 'app', 'ios', 'android', 'smartphone'],
            'web-app': ['web', 'website', 'online', 'webapp'],
            'ecommerce': ['ecommerce', 'e-commerce', 'shopping', 'retail', 'marketplace'],
            'fintech': ['fintech', 'finance', 'payment', 'banking', 'crypto'],
            'healthtech': ['health', 'medical', 'fitness', 'wellness', 'healthcare'],
            'edtech': ['education', 'learning', 'edtech', 'course', 'training'],
            'ai-ml': ['ai', 'machine learning', 'artificial intelligence', 'ml'],
            'blockchain': ['blockchain', 'crypto', 'defi', 'nft', 'web3'],
            'social': ['social', 'community', 'network', 'sharing'],
            'productivity': ['productivity', 'efficiency', 'automation', 'workflow'],
            'marketing': ['marketing', 'advertising', 'promotion', 'growth'],
            'analytics': ['analytics', 'data', 'insights', 'metrics'],
            'automation': ['automation', 'bot', 'workflow', 'efficiency'],
            'marketplace': ['marketplace', 'platform', 'exchange', 'trading'],
            'subscription': ['subscription', 'recurring', 'membership'],
            'freemium': ['freemium', 'free', 'premium', 'upgrade'],
            'b2b': ['b2b', 'enterprise', 'business', 'corporate'],
            'b2c': ['b2c', 'consumer', 'personal', 'individual']
        }
        
        # Check which category matches best
        text_to_check = f"{title} {content} {category}"
        best_category = 'general'
        max_matches = 0
        
        for cat, keywords in categories.items():
            matches = sum(1 for keyword in keywords if keyword in text_to_check)
            if matches > max_matches:
                max_matches = matches
                best_category = cat
        
        return best_category 