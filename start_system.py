#!/usr/bin/env python3
"""
아이디어 오아시스 시스템 시작 스크립트
"""

import os
import sys
import subprocess
import logging
from idea_crawler import IdeaCrawler

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_system():
    """시스템 초기 설정"""
    logger.info("=== 아이디어 오아시스 시스템 초기화 ===")
    
    # 1. 데이터베이스 초기화
    logger.info("1. 데이터베이스 초기화 중...")
    crawler = IdeaCrawler()
    logger.info("✓ 데이터베이스 초기화 완료")
    
    # 2. 샘플 데이터 생성 (테스트)
    logger.info("2. 테스트 크롤링 실행 중...")
    result = crawler.run_crawler()
    logger.info(f"✓ 테스트 크롤링 완료: {result}")
    
    # 3. 웹 서버 시작 안내
    logger.info("3. 시스템 설정 완료")
    logger.info("\n=== 다음 단계 ===")
    logger.info("웹 서버 시작: python3 -m http.server 8000")
    logger.info("관리자 페이지: http://localhost:8000/admin.html")
    logger.info("메인 페이지: http://localhost:8000/")
    logger.info("\n스케줄러 시작: python3 scheduler.py")
    logger.info("수동 크롤링: python3 scheduler.py --manual")

def start_scheduler():
    """스케줄러 백그라운드 시작"""
    logger.info("스케줄러를 백그라운드에서 시작합니다...")
    try:
        subprocess.Popen([sys.executable, "scheduler.py"], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        logger.info("✓ 스케줄러가 백그라운드에서 시작되었습니다.")
    except Exception as e:
        logger.error(f"스케줄러 시작 실패: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--with-scheduler":
        setup_system()
        start_scheduler()
    else:
        setup_system()