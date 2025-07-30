#!/usr/bin/env python3
"""
아이디어 오아시스 - 스케줄러
매주 토요일 오전 9시 (KST)에 아이디어 크롤러를 실행합니다.
"""

import time
import logging
from datetime import datetime
from idea_crawler import IdeaCrawler

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IdeaScheduler:
    """아이디어 크롤러 스케줄러"""
    
    def __init__(self):
        self.crawler = IdeaCrawler()
        
    def run_scheduled_crawler(self):
        """스케줄된 크롤러 실행"""
        try:
            now = datetime.now()
            logger.info(f"스케줄된 크롤러 시작 - {now.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 크롤러 실행
            result = self.crawler.run_crawler()
            
            if result['status'] == 'success':
                logger.info(f"크롤러 성공 완료: {result['ideas_found']}개 발견, {result['ideas_added']}개 추가")
            else:
                logger.error(f"크롤러 실행 실패: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"스케줄된 크롤러 실행 중 오류: {e}")
    
    def start_scheduler(self):
        """스케줄러 시작 (간단한 무한 루프)"""
        logger.info("아이디어 크롤러 스케줄러 시작")
        logger.info("매주 토요일 오전 9시에 크롤링 실행 예정 (시뮬레이션)")
        
        # 간단한 스케줄링 시뮬레이션
        while True:
            now = datetime.now()
            # 토요일(5)이고 9시인 경우 실행
            if now.weekday() == 5 and now.hour == 9 and now.minute == 0:
                self.run_scheduled_crawler()
                time.sleep(3600)  # 1시간 대기 (중복 실행 방지)
            else:
                time.sleep(300)  # 5분마다 체크

def manual_run():
    """수동 실행 (테스트용)"""
    logger.info("수동 크롤러 실행")
    crawler = IdeaCrawler()
    result = crawler.run_crawler()
    logger.info(f"수동 실행 결과: {result}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        # 수동 실행
        manual_run()
    else:
        # 스케줄러 시작
        scheduler = IdeaScheduler()
        scheduler.start_scheduler()