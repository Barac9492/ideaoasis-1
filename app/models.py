from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Idea(Base):
    __tablename__ = "ideas"
    
    id = Column(Integer, primary_key=True, index=True)
    idea_title = Column(String(500), nullable=False, index=True)
    source_url = Column(String(1000), nullable=False)
    summary_kr = Column(Text, nullable=False)
    published_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    language = Column(String(10), default="ko")
    source_type = Column(String(50), nullable=False)  # reddit, hackernews, zhihu, etc.
    archived = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    votes = relationship("Vote", back_populates="idea")

class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=False)
    user_ip = Column(String(45), nullable=False)  # IPv4/IPv6 support
    vote_type = Column(String(10), nullable=False)  # "up" or "down"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    idea = relationship("Idea", back_populates="votes")

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ideaoasis.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 