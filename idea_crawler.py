#!/usr/bin/env python3
"""
아이디어 오아시스 - 자동 아이디어 크롤러 시스템
매주 토요일 KST 9AM에 실행되어 새로운 비즈니스 아이디어를 수집하고 평가합니다.
"""

import sqlite3
import json
import time
import random
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import logging
import re

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('idea_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BusinessIdea:
    """비즈니스 아이디어 데이터 클래스"""
    def __init__(self, title, description, source, category, 
                 market_size_score, competition_score, execution_score, timing_score,
                 country="KR", created_at=None, status="pending"):
        self.title = title
        self.description = description
        self.source = source
        self.category = category
        self.market_size_score = market_size_score
        self.competition_score = competition_score
        self.execution_score = execution_score
        self.timing_score = timing_score
        self.country = country
        self.created_at = created_at
        self.status = status

class IdeaCrawler:
    """아이디어 크롤러 메인 클래스"""
    
    def __init__(self, db_path: str = "ideaoasis.db"):
        self.db_path = db_path
        self.init_database()
        
        # 크롤링 대상 사이트들
        self.sources = [
            {
                'name': 'TechCrunch',
                'url': 'https://techcrunch.com/category/startups/',
                'selector': '.post-block__title__link'
            },
            {
                'name': 'Y Combinator',
                'url': 'https://www.ycombinator.com/companies',
                'selector': '.company-name'
            },
            {
                'name': 'Product Hunt',
                'url': 'https://www.producthunt.com/',
                'selector': '[data-test="product-item-name"]'
            }
        ]
        
        # 카테고리별 키워드
        self.categories = {
            'AI/SaaS': ['AI', 'artificial intelligence', 'SaaS', 'automation', 'machine learning'],
            'FinTech': ['fintech', 'payment', 'cryptocurrency', 'banking', 'financial'],
            'EdTech': ['education', 'learning', 'online course', 'skill', 'training'],
            'HealthTech': ['health', 'medical', 'fitness', 'wellness', 'healthcare'],
            'E-commerce': ['marketplace', 'retail', 'shopping', 'commerce', 'store'],
            'Mobility': ['transportation', 'logistics', 'delivery', 'mobility', 'travel']
        }

    def init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ideas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    source TEXT NOT NULL,
                    category TEXT NOT NULL,
                    market_size_score INTEGER NOT NULL,
                    competition_score INTEGER NOT NULL,
                    execution_score INTEGER NOT NULL,
                    timing_score INTEGER NOT NULL,
                    country TEXT DEFAULT 'KR',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    UNIQUE(title, source)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crawler_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ideas_found INTEGER,
                    ideas_added INTEGER,
                    status TEXT,
                    notes TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")

    def generate_sample_ideas(self) -> List[BusinessIdea]:
        """샘플 아이디어 생성 (실제 크롤링 대신 사용)"""
        sample_ideas = [
            BusinessIdea(
                title="AI 기반 개인 영양 관리 앱",
                description="사용자의 건강 데이터와 식습관을 분석하여 개인 맞춤형 식단과 영양제를 추천하는 AI 기반 앱입니다. 혈액 검사 결과, 운동량, 스트레스 수준 등을 종합적으로 고려하여 최적의 영양 솔루션을 제공합니다.",
                source="TechCrunch",
                category="HealthTech",
                market_size_score=7,
                competition_score=5,
                execution_score=6,
                timing_score=8
            ),
            BusinessIdea(
                title="블록체인 기반 탄소 크레딧 거래소",
                description="기업들이 탄소 배출량을 상쇄하기 위해 탄소 크레딧을 투명하고 신뢰할 수 있게 거래할 수 있는 블록체인 플랫폼입니다. 스마트 컨트랙트를 통해 자동화된 검증과 거래를 제공합니다.",
                source="Y Combinator",
                category="FinTech",
                market_size_score=9,
                competition_score=4,
                execution_score=8,
                timing_score=9
            ),
            BusinessIdea(
                title="VR 기반 원격 팀 협업 도구",
                description="원격 근무 팀이 가상현실 환경에서 마치 같은 사무실에 있는 것처럼 협업할 수 있는 플랫폼입니다. 3D 화이트보드, 가상 회의실, 실시간 문서 편집 등의 기능을 제공합니다.",
                source="Product Hunt",
                category="AI/SaaS",
                market_size_score=6,
                competition_score=7,
                execution_score=7,
                timing_score=6
            ),
            BusinessIdea(
                title="농업용 IoT 모니터링 시스템",
                description="농부들이 작물의 상태를 실시간으로 모니터링하고 최적의 관리 방법을 제안받을 수 있는 IoT 기반 스마트 농업 솔루션입니다. 토양 습도, 온도, 영양분 수준을 자동으로 측정하고 분석합니다.",
                source="TechCrunch",
                category="AI/SaaS",
                market_size_score=5,
                competition_score=6,
                execution_score=5,
                timing_score=7
            ),
            BusinessIdea(
                title="마이크로 투자 게임화 플랫폼",
                description="20-30대가 소액으로 주식 투자를 배우고 경험할 수 있는 게임화된 투자 플랫폼입니다. 리워드 시스템, 투자 교육 컨텐츠, 소셜 투자 챌린지 등을 통해 재미있게 투자를 학습할 수 있습니다.",
                source="Y Combinator",
                category="FinTech",
                market_size_score=8,
                competition_score=8,
                execution_score=4,
                timing_score=7
            )
        ]
        
        # 무작위로 3개 선택
        return random.sample(sample_ideas, 3)

    def evaluate_idea(self, title: str, description: str, category: str) -> Dict[str, int]:
        """아이디어를 4가지 요소로 평가"""
        # 실제 구현에서는 더 정교한 평가 로직을 사용
        # 여기서는 키워드 기반의 간단한 평가를 시뮬레이션
        
        evaluation = {
            'market_size_score': random.randint(4, 9),
            'competition_score': random.randint(3, 8),
            'execution_score': random.randint(3, 8),
            'timing_score': random.randint(5, 9)
        }
        
        # 카테고리별 조정
        if category == "AI/SaaS":
            evaluation['timing_score'] = min(9, evaluation['timing_score'] + 1)
        elif category == "FinTech":
            evaluation['market_size_score'] = min(9, evaluation['market_size_score'] + 1)
        elif category == "HealthTech":
            evaluation['timing_score'] = min(9, evaluation['timing_score'] + 1)
            
        return evaluation

    def save_idea(self, idea: BusinessIdea) -> bool:
        """아이디어를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO ideas 
                (title, description, source, category, market_size_score, 
                 competition_score, execution_score, timing_score, country)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                idea.title, idea.description, idea.source, idea.category,
                idea.market_size_score, idea.competition_score, 
                idea.execution_score, idea.timing_score, idea.country
            ))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if success:
                logger.info(f"아이디어 저장 성공: {idea.title}")
            else:
                logger.info(f"아이디어 중복 (건너뜀): {idea.title}")
                
            return success
            
        except Exception as e:
            logger.error(f"아이디어 저장 오류: {e}")
            return False

    def log_crawler_run(self, ideas_found: int, ideas_added: int, status: str, notes: str = ""):
        """크롤러 실행 로그 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO crawler_logs (ideas_found, ideas_added, status, notes)
                VALUES (?, ?, ?, ?)
            ''', (ideas_found, ideas_added, status, notes))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"로그 저장 오류: {e}")

    def run_crawler(self) -> Dict[str, int]:
        """크롤러 메인 실행 함수"""
        logger.info("아이디어 크롤러 시작")
        
        start_time = datetime.now()
        ideas_found = 0
        ideas_added = 0
        
        try:
            # 실제 환경에서는 웹사이트를 크롤링하지만, 
            # 여기서는 샘플 데이터를 사용
            sample_ideas = self.generate_sample_ideas()
            ideas_found = len(sample_ideas)
            
            for idea in sample_ideas:
                if self.save_idea(idea):
                    ideas_added += 1
                time.sleep(1)  # API 제한 고려
            
            # 실행 로그 저장
            status = "SUCCESS"
            notes = f"실행 시간: {datetime.now() - start_time}"
            self.log_crawler_run(ideas_found, ideas_added, status, notes)
            
            logger.info(f"크롤러 완료: {ideas_found}개 발견, {ideas_added}개 추가")
            
            return {
                'ideas_found': ideas_found,
                'ideas_added': ideas_added,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"크롤러 실행 오류: {e}")
            self.log_crawler_run(ideas_found, ideas_added, "ERROR", str(e))
            return {
                'ideas_found': ideas_found,
                'ideas_added': ideas_added,
                'status': 'error',
                'error': str(e)
            }

    def get_pending_ideas(self) -> List[Dict]:
        """승인 대기 중인 아이디어 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM ideas WHERE status = 'pending' 
                ORDER BY created_at DESC
            ''')
            
            columns = [description[0] for description in cursor.description]
            ideas = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return ideas
            
        except Exception as e:
            logger.error(f"아이디어 조회 오류: {e}")
            return []

    def approve_idea(self, idea_id: int) -> bool:
        """아이디어 승인"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE ideas SET status = 'approved' WHERE id = ?
            ''', (idea_id,))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            logger.error(f"아이디어 승인 오류: {e}")
            return False

    def reject_idea(self, idea_id: int) -> bool:
        """아이디어 거부"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE ideas SET status = 'rejected' WHERE id = ?
            ''', (idea_id,))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
            
        except Exception as e:
            logger.error(f"아이디어 거부 오류: {e}")
            return False

def main():
    """메인 실행 함수"""
    crawler = IdeaCrawler()
    result = crawler.run_crawler()
    
    print(f"크롤링 결과: {result}")
    
    # 승인 대기 아이디어 확인
    pending = crawler.get_pending_ideas()
    print(f"승인 대기 중인 아이디어: {len(pending)}개")

if __name__ == "__main__":
    main()