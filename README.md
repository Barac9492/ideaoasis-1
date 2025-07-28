# 🧠 IdeaOasis - 해외 아이디어 발굴 플랫폼

한국의 예비 창업자 및 스타트업 빌더들을 위해 해외에서 나온 신선하고 실행 가능한 아이디어를 매일 하나씩 제공하는 자동화 시스템입니다.

## ✨ 주요 기능

- **🌍 글로벌 아이디어 수집**: IdeaBrowser.com, Hacker News, Product Hunt 등 해외 커뮤니티에서 웹 크롤링으로 수집
- **🤖 AI 번역 및 요약**: GPT-4를 활용한 고품질 한국어 번역 및 한국 시장 적용 방안 제시
- **⏰ 자동 스케줄링**: 매일 오전 6시(한국시간) 자동 실행
- **📊 투표 시스템**: 사용자들이 아이디어에 대해 투표할 수 있는 기능
- **📚 아카이브**: 24시간 후 자동 아카이브, 30일간 보관

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd IdeaOasis-1

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# env.example을 복사하여 .env 파일 생성
cp env.example .env

# .env 파일을 편집하여 OpenAI API 키 설정
```

필요한 환경 변수:
- `OPENAI_API_KEY`: OpenAI API 키 (필수)
- `DATABASE_URL`: 데이터베이스 연결 문자열 (선택사항, 기본값: SQLite)

### 3. 데이터베이스 초기화

```bash
# 데이터베이스 테이블 생성
python -c "from app.models import create_tables; create_tables()"
```

### 4. 웹 애플리케이션 실행

```bash
# 웹 서버 시작
python run_web.py
```

웹 브라우저에서 `http://localhost:8000`으로 접속하여 플랫폼을 확인할 수 있습니다.

### 5. 스케줄러 실행 (선택사항)

```bash
# 백그라운드에서 스케줄러 실행
python run_scheduler.py
```

스케줄러는 매일 오전 6시(한국시간)에 자동으로 새로운 아이디어를 발굴합니다.

## 📁 프로젝트 구조

```
IdeaOasis-1/
├── app/
│   ├── models.py              # 데이터베이스 모델
│   ├── main.py                # FastAPI 웹 애플리케이션
│   ├── scheduler.py           # 스케줄링 시스템
│   ├── idea_discovery_agent.py # 메인 아이디어 발굴 에이전트
│   ├── ai_processor.py        # AI 번역 및 요약 처리
│   ├── scrapers/              # 웹 크롤링 모듈들
│   │   ├── ideabrowser_scraper.py
│   │   ├── hackernews_scraper.py
│   │   └── producthunt_scraper.py
│   └── templates/             # HTML 템플릿
│       ├── base.html
│       ├── index.html
│       └── archive.html
├── run_scheduler.py           # 스케줄러 실행 스크립트
├── run_web.py                 # 웹 애플리케이션 실행 스크립트
├── test_system.py             # 시스템 테스트
├── init_system.py             # 초기 설정
├── requirements.txt           # Python 의존성
├── env.example               # 환경 변수 템플릿
└── README.md                 # 프로젝트 문서
```

## 🔧 API 엔드포인트

### 웹 인터페이스
- `GET /`: 오늘의 아이디어 표시
- `GET /archive`: 아카이브된 아이디어 목록
- `POST /vote/{idea_id}/{vote_type}`: 아이디어 투표 (up/down)

### REST API
- `GET /api/ideas/current`: 현재 활성 아이디어 조회
- `GET /api/ideas/archive`: 아카이브된 아이디어 목록 조회
- `POST /discover`: 수동 아이디어 발굴 (관리자용)

## 🤖 아이디어 발굴 프로세스

1. **수집 단계**: IdeaBrowser.com, Hacker News, Product Hunt에서 웹 크롤링으로 아이디어 수집
2. **필터링 단계**: 품질 점수 기반 필터링 및 중복 제거
3. **선택 단계**: IdeaBrowser.com 우선, 최고 품질의 아이디어 선택
4. **AI 처리 단계**: GPT-4를 통한 한국어 번역 및 요약
5. **저장 단계**: 데이터베이스에 저장 및 웹에 표시

## 🎯 아이디어 선정 기준

- **신선성**: 한국에서 아직 소개되지 않은 아이디어
- **실행 가능성**: 특정 대상(직장인, 노인, 창작자 등)을 위한 문제 해결
- **다양성**: 기술 기반 SaaS, 툴, 커머스, 마이크로서비스 등
- **문화적 임팩트**: 한국인에게 문화적 충격을 줄 수 있는 엣지 있는 아이디어

## 🌐 데이터 소스

### 주요 소스 (우선순위 순)
1. **IdeaBrowser.com** - 전용 아이디어 발굴 사이트
2. **Hacker News** - Show HN 및 일반 스토리
3. **Product Hunt** - 신제품 및 서비스

### 크롤링 방식
- API 의존성 최소화로 안정성 향상
- 웹 크롤링을 통한 실시간 데이터 수집
- Rate limiting 및 respectful crawling 적용

## 🔒 보안 및 개인정보

- 사용자 투표는 IP 주소로 식별 (개인정보 수집 최소화)
- 30일 후 자동으로 아카이브된 아이디어 삭제
- API 키는 환경 변수로 안전하게 관리

## 🛠️ 개발 환경

- **Python**: 3.8+
- **데이터베이스**: PostgreSQL (권장) 또는 SQLite
- **웹 프레임워크**: FastAPI
- **템플릿 엔진**: Jinja2
- **스타일링**: Tailwind CSS
- **AI**: OpenAI GPT-4
- **크롤링**: BeautifulSoup, Requests

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 문의사항이나 버그 리포트는 GitHub Issues를 통해 제출해주세요.

---

**IdeaOasis** - 한국 창업자를 위한 해외 아이디어 발굴 플랫폼 🚀 