from sqlalchemy import create_engine, Column, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./markets.db")

# Handle empty DATABASE_URL (common in Railway)
if not DATABASE_URL or DATABASE_URL.strip() == "":
    DATABASE_URL = "sqlite:///./markets.db"

# Handle Railway's DATABASE_URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

logger.info(f"Using database URL: {DATABASE_URL}")

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Market model
class Market(Base):
    __tablename__ = "markets"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    prompt = Column(Text, nullable=False)
    close_time_iso = Column(String, nullable=False)
    outcomes = Column(JSON, nullable=False)  # List of strings
    initial_prob = Column(Float, nullable=False)
    validation = Column(JSON, nullable=False)  # MarketValidation dict
    created_at = Column(String, nullable=False)
    status = Column(String, default="active")  # active, resolved, expired
    outcome = Column(String, nullable=True)  # YES, NO, or None
    resolved_at = Column(String, nullable=True)
    resolution_confidence = Column(Float, nullable=True)

# Resolution model
class Resolution(Base):
    __tablename__ = "resolutions"
    
    id = Column(String, primary_key=True, index=True)
    market_id = Column(String, nullable=False, index=True)
    outcome = Column(String, nullable=False)  # YES, NO, or EXPIRED
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=False)
    evidence_sources = Column(JSON, nullable=False)  # List of strings
    resolved_at = Column(String, nullable=False)
    auto_expired = Column(Boolean, default=False)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise 