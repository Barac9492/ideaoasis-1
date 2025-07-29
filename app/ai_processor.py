import openai
import os
from typing import Dict, Optional
from datetime import datetime
import json
from app.models import Idea

class AIProcessor:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        else:
            raise ValueError("OPENAI_API_KEY environment variable is required")

    def process_idea(self, idea_data: Dict) -> Optional[Dict]:
        """Process an idea with AI to create Korean summary and context"""
        try:
            prompt = self._create_prompt(idea_data)
            result = self._get_ai_response(prompt)
            
            if result:
                # Add metadata
                result['source_url'] = idea_data.get('url', '')
                result['published_at'] = datetime.now()
                result['language'] = 'ko'
                result['source_type'] = idea_data.get('source_type', 'ideabrowser')
                result['archived'] = False
                
                return result
        except Exception as e:
            print(f"Error processing idea: {e}")
        return None

    def _create_prompt(self, idea_data: Dict) -> str:
        """Create the prompt for AI processing"""
        title = idea_data.get('title', '')
        content = idea_data.get('content', '')
        source_type = idea_data.get('source_type', '')
        category = idea_data.get('category', '')

        prompt = f"""
당신은 한국의 창업자들을 위해 운영되는 아이디어 발굴 플랫폼 "IdeaOasis"의 전담 에이전트입니다.
ideabrowser.com의 프레임워크를 참고하여 해외 아이디어를 한국어로 요약, 번역, 맥락화해주세요.

다음 해외 아이디어를 처리해주세요:

제목: {title}
내용: {content}
출처: {source_type}
카테고리: {category}

다음 포맷으로 JSON 형태로 응답해주세요:
{{
  "idea_title": "[매력적이고 실행 가능한 한국어 아이디어 제목]",
  "source_url": "{idea_data.get('url', '')}",
  "summary_kr": "🚀 오늘의 창업 아이디어

💡 아이디어 핵심
• [한 줄로 아이디어의 핵심을 설명]

🎯 시장 기회
• [이 아이디어가 해결하는 문제와 시장 기회]
• [왜 지금이 적기인지]

⚡ 실행 가능성
• [기술적 구현 방법과 필요한 리소스]
• [MVP 개발 계획과 타임라인]

💰 수익 모델
• [구체적인 수익화 전략]
• [목표 고객과 가격 정책]

🌏 한국 시장 적용
• [한국 시장에서의 차별화 포인트]
• [로컬라이징 전략과 문화적 고려사항]

📈 성장 전략
• [초기 런칭부터 확장까지의 로드맵]
• [마케팅과 고객 확보 전략]

💪 창업자에게 주는 메시지
• [이 아이디어로 창업할 때의 장점과 주의사항]
• [성공을 위한 핵심 팁]"
}}

요구사항:
1. ideabrowser.com의 전문적이고 구조화된 프레임워크를 따라 작성
2. 창업자가 실제로 실행하고 싶게 만드는 매력적인 내용으로 구성
3. 구체적이고 실행 가능한 정보를 포함
4. 한국 시장에서의 적용 가능성과 문화적 맥락을 강조
5. 수익 모델과 성장 전략을 명확히 제시
6. 창업자에게 실질적인 가치를 제공하는 내용으로 구성
7. GPT 수준의 고품질 한국어 사용
8. 뉴스 기사가 아닌 실행 가능한 비즈니스 아이디어로 구성
"""
        return prompt

    def _get_ai_response(self, prompt: str) -> Optional[Dict]:
        """Get response from OpenAI API using the new v1.0+ format"""
        try:
            client = openai.OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a startup idea analyst and translator for Korean entrepreneurs. Always respond in valid JSON format. Create compelling, actionable business ideas that make readers want to start a business. Focus on practical implementation and market opportunities."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            print(f"Raw AI response: {content}")
            return self._fallback_response(content)
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return None

    def _fallback_response(self, content: str) -> Dict:
        """Create a fallback response if JSON parsing fails"""
        return {
            'idea_title': '혁신적인 해외 스타트업 아이디어',
            'summary_kr': f"""
🚀 오늘의 창업 아이디어

💡 아이디어 핵심
• {content[:100]}...

🎯 시장 기회
• 해외에서 주목받고 있는 혁신적인 아이디어입니다.
• 한국 시장에서도 충분한 기회가 있습니다.

⚡ 실행 가능성
• 기술적으로 구현 가능한 아이디어입니다.
• MVP 개발부터 단계적 접근이 가능합니다.

💰 수익 모델
• 구독 모델, 마켓플레이스 수수료 등 다양한 수익화 방안이 있습니다.
• 한국 시장에 맞는 가격 정책이 필요합니다.

🌏 한국 시장 적용
• 한국인의 사용 패턴과 문화를 반영한 로컬라이징이 필요합니다.
• 네이버, 카카오 등 국내 플랫폼과의 연동을 고려해보세요.

📈 성장 전략
• 초기에는 특정 세그먼트에 집중하여 검증하세요.
• 검증 후 점진적으로 확장하는 전략을 추천합니다.

💪 창업자에게 주는 메시지
• 이 아이디어는 충분한 시장 기회를 가지고 있습니다.
• 철저한 시장 조사와 MVP 검증을 통해 리스크를 최소화하세요.
"""
        }

    def check_duplicate(self, idea_title: str, db_session) -> bool:
        """Check if an idea is already in the database (last 30 days)"""
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        existing_idea = db_session.query(Idea).filter(
            Idea.idea_title == idea_title,
            Idea.created_at >= thirty_days_ago
        ).first()
        if existing_idea:
            return True
        keywords = idea_title.lower().split()
        for keyword in keywords:
            if len(keyword) > 3:
                existing_ideas = db_session.query(Idea).filter(
                    Idea.idea_title.ilike(f"%{keyword}%"),
                    Idea.created_at >= thirty_days_ago
                ).all()
                if existing_ideas:
                    return True
        return False

    def categorize_idea(self, idea_data: Dict) -> str:
        """Categorize an idea based on its content"""
        title = idea_data.get('title', '').lower()
        content = idea_data.get('content', '').lower()
        category = idea_data.get('category', '').lower()

        categories = {
            'saas': ['saas', 'software', 'subscription', 'platform', 'tool'],
            'mobile-app': ['mobile', 'app', 'ios', 'android', 'smartphone'],
            'web-app': ['web', 'website', 'online', 'webapp', 'web-app'],
            'ecommerce': ['ecommerce', 'e-commerce', 'shopping', 'retail', 'marketplace'],
            'fintech': ['fintech', 'finance', 'payment', 'banking', 'crypto', 'money'],
            'healthtech': ['health', 'medical', 'fitness', 'wellness', 'healthcare'],
            'edtech': ['education', 'learning', 'edtech', 'course', 'training'],
            'ai-ml': ['ai', 'machine learning', 'artificial intelligence', 'ml', 'automation'],
            'blockchain': ['blockchain', 'crypto', 'defi', 'nft', 'web3'],
            'social': ['social', 'community', 'network', 'sharing', 'connection'],
            'productivity': ['productivity', 'efficiency', 'automation', 'workflow', 'tool'],
            'marketing': ['marketing', 'advertising', 'promotion', 'growth', 'sales'],
            'analytics': ['analytics', 'data', 'insights', 'metrics', 'dashboard'],
            'automation': ['automation', 'bot', 'workflow', 'efficiency', 'process'],
            'marketplace': ['marketplace', 'platform', 'exchange', 'trading', 'connect'],
            'subscription': ['subscription', 'recurring', 'membership', 'service'],
            'freemium': ['freemium', 'free', 'premium', 'upgrade', 'tier'],
            'b2b': ['b2b', 'enterprise', 'business', 'corporate', 'saas'],
            'b2c': ['b2c', 'consumer', 'personal', 'individual', 'user']
        }

        text_to_check = f"{title} {content} {category}"
        best_category = 'general'
        max_matches = 0

        for cat, keywords in categories.items():
            matches = sum(1 for keyword in keywords if keyword in text_to_check)
            if matches > max_matches:
                max_matches = matches
                best_category = cat
        return best_category 