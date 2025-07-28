from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from app.models import get_db, Idea, Vote, create_tables
from app.idea_discovery_agent import IdeaDiscoveryAgent

load_dotenv()

app = FastAPI(title="IdeaOasis", description="Korean Startup Idea Discovery Platform")

# Create database tables
create_tables()

# Templates
templates = Jinja2Templates(directory="app/templates")

# Demo data for testing without API keys
DEMO_IDEA = {
    'id': 1,
    'idea_title': 'AI 기반 개인 스타일링 어시스턴트',
    'source_url': 'https://example.com/demo-idea',
    'summary_kr': '''
💡 오늘의 해외 아이디어

📋 아이디어 개요
• AI 기술을 활용한 개인 맞춤형 스타일링 추천 서비스

🎯 핵심 가치 제안
• 사용자의 체형, 취향, 상황에 맞는 최적의 패션 조합을 AI가 추천
• 쇼핑몰 연동으로 원클릭 구매까지 가능한 원스톱 서비스

⚙️ 기술적 구현
• 컴퓨터 비전 AI로 사용자 체형 분석
• 머신러닝 기반 개인 취향 학습
• 쇼핑몰 API 연동 및 결제 시스템

🌏 한국 시장 적용 방안
• 한국인의 패션 트렌드와 체형 특성 반영
• 네이버, 카카오 등 국내 플랫폼 연동
• 한국 쇼핑몰들과의 파트너십 구축

💼 비즈니스 모델
• 프리미엄 구독 서비스 (월 9,900원)
• 쇼핑몰 연계 수수료 수익
• 브랜드 협찬 및 광고 수익

🚀 실행 로드맵
• MVP: 기본 스타일링 추천 기능
• 1단계: 쇼핑몰 연동 및 결제 시스템
• 2단계: AI 개인화 기능 고도화
• 3단계: 브랜드 파트너십 확대
''',
    'published_at': datetime.now(),
    'language': 'ko',
    'source_type': 'demo',
    'archived': False,
    'created_at': datetime.now(),
    'updated_at': datetime.now()
}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    """Main page showing today's idea"""
    
    # Check if we're in demo mode (no OpenAI API key)
    demo_mode = not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here"
    
    if demo_mode:
        # Return demo data
        upvotes = 42
        downvotes = 8
        return templates.TemplateResponse("index.html", {
            "request": request,
            "idea": DEMO_IDEA,
            "upvotes": upvotes,
            "downvotes": downvotes,
            "demo_mode": True
        })
    
    # Get today's idea (not archived)
    today = datetime.now().date()
    idea = db.query(Idea).filter(
        Idea.archived == False,
        Idea.created_at >= today
    ).first()
    
    if idea:
        # Get vote counts
        upvotes = db.query(Vote).filter(Vote.idea_id == idea.id, Vote.vote_type == "up").count()
        downvotes = db.query(Vote).filter(Vote.idea_id == idea.id, Vote.vote_type == "down").count()
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "idea": idea,
            "upvotes": upvotes,
            "downvotes": downvotes,
            "demo_mode": False
        })
    else:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "idea": None,
            "upvotes": 0,
            "downvotes": 0,
            "demo_mode": False
        })

@app.get("/archive", response_class=HTMLResponse)
async def archive(request: Request, db: Session = Depends(get_db)):
    """Archive page showing all past ideas"""
    
    # Check if we're in demo mode
    demo_mode = not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here"
    
    if demo_mode:
        # Return demo archive data
        demo_ideas = [
            {**DEMO_IDEA, 'id': 1, 'idea_title': 'AI 기반 개인 스타일링 어시스턴트'},
            {**DEMO_IDEA, 'id': 2, 'idea_title': '원격 근무자를 위한 가상 오피스 플랫폼'},
            {**DEMO_IDEA, 'id': 3, 'idea_title': '지역 기반 푸드테크 마켓플레이스'},
        ]
        return templates.TemplateResponse("archive.html", {
            "request": request,
            "ideas": demo_ideas,
            "demo_mode": True
        })
    
    # Get all archived ideas
    ideas = db.query(Idea).filter(Idea.archived == True).order_by(Idea.created_at.desc()).all()
    
    return templates.TemplateResponse("archive.html", {
        "request": request,
        "ideas": ideas,
        "demo_mode": False
    })

@app.post("/vote/{idea_id}/{vote_type}")
async def vote(idea_id: int, vote_type: str, request: Request, db: Session = Depends(get_db)):
    """Vote on an idea"""
    
    # Check if we're in demo mode
    demo_mode = not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here"
    
    if demo_mode:
        return {"success": True, "message": "Demo mode - vote recorded"}
    
    if vote_type not in ["up", "down"]:
        raise HTTPException(status_code=400, detail="Invalid vote type")
    
    # Get client IP
    client_ip = request.client.host
    
    # Check if user already voted
    existing_vote = db.query(Vote).filter(
        Vote.idea_id == idea_id,
        Vote.user_ip == client_ip
    ).first()
    
    if existing_vote:
        # Update existing vote
        existing_vote.vote_type = vote_type
        existing_vote.created_at = datetime.now()
    else:
        # Create new vote
        vote = Vote(
            idea_id=idea_id,
            user_ip=client_ip,
            vote_type=vote_type
        )
        db.add(vote)
    
    db.commit()
    
    # Get updated vote counts
    upvotes = db.query(Vote).filter(Vote.idea_id == idea_id, Vote.vote_type == "up").count()
    downvotes = db.query(Vote).filter(Vote.idea_id == idea_id, Vote.vote_type == "down").count()
    
    return {
        "success": True,
        "upvotes": upvotes,
        "downvotes": downvotes
    }

@app.post("/discover")
async def discover_idea(db: Session = Depends(get_db)):
    """Manually trigger idea discovery (for testing)"""
    
    # Check if we're in demo mode
    demo_mode = not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here"
    
    if demo_mode:
        return {"success": True, "message": "Demo mode - discovery not available"}
    
    try:
        agent = IdeaDiscoveryAgent()
        result = agent.discover_daily_idea()
        
        if result:
            # Save to database
            success = agent.save_idea_to_database(result)
            if success:
                return {"success": True, "message": "Idea discovered and saved", "idea": result}
            else:
                return {"success": False, "message": "Failed to save idea"}
        else:
            return {"success": False, "message": "No suitable idea found"}
            
    except Exception as e:
        return {"success": False, "message": f"Error during discovery: {str(e)}"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 