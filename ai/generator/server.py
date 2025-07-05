from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import requests
import json
import os
import re
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Market Generator Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:3000", "http://localhost:9000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ASI-1 Mini API Configuration
ASI_API_URL = "https://api.asi1.ai/v1/chat/completions"
ASI_API_KEY = os.getenv("ASI_API_KEY", "sk_a1d55fd6b1ba47ddadc98bd1e8048e56ff00c4736c844a9db4aab791d33f0989")
MODEL_NAME = "asi1-mini"

# Local storage for markets
MARKETS_FILE = "markets.json"
MARKETS_DIR = "markets"
ACTIVE_MARKETS_FILE = "active/markets.json"
ARCHIVED_MARKETS_FILE = "archived/markets.json"

class MarketRequest(BaseModel):
    prompt: str = Field(..., description="The market prompt to analyze")
    market_id: Optional[str] = Field(None, description="Optional custom market ID")
    tweet_url: Optional[str] = Field(None, description="Optional tweet URL for context")

class MarketValidation(BaseModel):
    is_valid: bool
    confidence: float
    reasoning: str
    yes_probability: float
    no_probability: float
    reliable_sources: List[str]
    resolution_date: str
    auto_expire: bool = False

class MarketData(BaseModel):
    id: str
    title: str
    description: str
    prompt: str
    close_time_iso: str
    outcomes: List[str] = ["YES", "NO"]
    initial_prob: float
    validation: MarketValidation
    created_at: str
    status: str = "active"  # active, resolved, expired

class MarketResponse(BaseModel):
    success: bool
    market: Optional[MarketData] = None
    error: Optional[str] = None

def get_asi_headers():
    """Get headers for ASI-1 API requests"""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'bearer {ASI_API_KEY}'
    }

def ensure_markets_directory():
    """Ensure the markets directory structure exists"""
    if not os.path.exists(MARKETS_DIR):
        os.makedirs(MARKETS_DIR)
    if not os.path.exists(os.path.join(MARKETS_DIR, "active")):
        os.makedirs(os.path.join(MARKETS_DIR, "active"))
    if not os.path.exists(os.path.join(MARKETS_DIR, "archived")):
        os.makedirs(os.path.join(MARKETS_DIR, "archived"))

def load_markets() -> Dict[str, MarketData]:
    """Load markets from local storage"""
    ensure_markets_directory()
    
    # Load active markets
    active_file = os.path.join(MARKETS_DIR, ACTIVE_MARKETS_FILE)
    archived_file = os.path.join(MARKETS_DIR, ARCHIVED_MARKETS_FILE)
    
    markets = {}
    
    # Load active markets
    if os.path.exists(active_file):
        try:
            with open(active_file, 'r') as f:
                data = json.load(f)
                for market_id, market_data in data.items():
                    markets[market_id] = MarketData(**market_data)
        except Exception as e:
            logger.error(f"Error loading active markets: {e}")
    
    # Load archived markets (for backward compatibility and reference)
    if os.path.exists(archived_file):
        try:
            with open(archived_file, 'r') as f:
                data = json.load(f)
                for market_id, market_data in data.items():
                    markets[market_id] = MarketData(**market_data)
        except Exception as e:
            logger.error(f"Error loading archived markets: {e}")
    
    # Backward compatibility: load from old single file if it exists
    old_file = os.path.join(MARKETS_DIR, MARKETS_FILE)
    if os.path.exists(old_file) and not markets:
        try:
            with open(old_file, 'r') as f:
                data = json.load(f)
                for market_id, market_data in data.items():
                    markets[market_id] = MarketData(**market_data)
        except Exception as e:
            logger.error(f"Error loading old markets file: {e}")
    
    return markets

def save_markets(markets: Dict[str, MarketData]):
    """Save markets to local storage, organizing by status"""
    ensure_markets_directory()
    
    active_markets = {}
    archived_markets = {}
    
    # Separate markets by status
    for market_id, market in markets.items():
        if market.status == "active":
            active_markets[market_id] = market.dict()
        else:
            archived_markets[market_id] = market.dict()
    
    # Save active markets
    active_file = os.path.join(MARKETS_DIR, ACTIVE_MARKETS_FILE)
    try:
        with open(active_file, 'w') as f:
            json.dump(active_markets, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving active markets: {e}")
    
    # Save archived markets
    archived_file = os.path.join(MARKETS_DIR, ARCHIVED_MARKETS_FILE)
    try:
        with open(archived_file, 'w') as f:
            json.dump(archived_markets, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving archived markets: {e}")

def archive_expired_markets():
    """Move expired markets to archived status"""
    markets = load_markets()
    current_time = datetime.now()
    updated = False
    
    for market_id, market in markets.items():
        if market.status == "active":
            try:
                close_time = datetime.fromisoformat(market.close_time_iso.replace('Z', '+00:00'))
                if close_time <= current_time:
                    market.status = "expired"
                    updated = True
                    logger.info(f"Archived expired market: {market.title}")
            except Exception as e:
                logger.error(f"Error checking market expiration: {e}")
    
    if updated:
        save_markets(markets)
    
    return updated

async def analyze_market_prompt(prompt: str) -> MarketValidation:
    """Use ASI-1 Mini to analyze market prompt and estimate probabilities"""
    
    # Get current date for validation
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    analysis_prompt = f"""
    You are a professional prediction market analyst. Analyze the following market prompt to determine if it's valid and estimate probabilities.

    CURRENT DATE: {current_date} (July 2025)
    MARKET PROMPT: {prompt}

    Return a JSON object with the following structure:
    {{
        "is_valid": true/false,
        "confidence": 0.0-1.0,
        "reasoning": "Detailed explanation of your analysis",
        "yes_probability": 0.0-1.0,
        "no_probability": 0.0-1.0,
        "reliable_sources": [
            "List of reliable sources that would report on this outcome (e.g., 'Reuters', 'Bloomberg', 'CNN', 'Associated Press')"
        ],
        "resolution_date": "YYYY-MM-DD",
        "auto_expire": true/false,
        "is_past_event": true/false
    }}

    VALIDATION CRITERIA:
    1. Is the outcome binary and clearly defined?
    2. Is there a clear resolution date?
    3. Are there reliable sources that would report on this outcome?
    4. Is the market not already resolved?
    5. Is the probability estimate reasonable?
    6. **CRITICAL: Is this about a FUTURE event? (not a past event)**
    7. **CRITICAL: Are there at least 3 reliable sources that would definitively report on this outcome?**
    8. **CRITICAL: Is the resolution date AFTER the current date ({current_date})?**

    REJECTION RULES:
    - If the event has already happened (is_past_event: true), mark as invalid
    - If the resolution date is today or in the past, mark as invalid
    - If there are fewer than 3 reliable sources, mark as invalid
    - If the outcome is not clearly binary, mark as invalid
    - If there's no clear resolution date, mark as invalid

    **IMPORTANT: Check if the event described has ALREADY HAPPENED. For example:**
    - "Will Bitcoin hit 100k before 2026?" - INVALID because Bitcoin already hit $100k in March 2024
    - "Will Bitcoin hit 200k before 2026?" - VALID because it hasn't happened yet
    - "Will the US have a recession in 2024?" - INVALID because 2024 is over
    - "Will the US have a recession in 2025?" - VALID because it's in the future

    **PAST EVENT DETECTION:**
    - Research if the specific event mentioned has already occurred
    - For price targets: Check if the asset has already reached that price
    - For time-based events: Check if the time period has already passed
    - For elections: Check if the election has already happened
    - For sports events: Check if the game/tournament has already occurre

    RELIABLE SOURCES: Include major news outlets, official government sources, financial data providers, or other credible sources that would definitively report on this outcome. You need at least 3 sources.

    RESOLUTION DATE: Set to a reasonable date when the outcome will be known. Must be AFTER {current_date}. If it's a "before X date" type market, set auto_expire to true.

    Be conservative in your probability estimates and only mark as valid if you have high confidence.
    """
    
    try:
        response = requests.post(
            ASI_API_URL,
            headers=get_asi_headers(),
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": analysis_prompt}],
                "temperature": 0.2,
                "stream": False,
                "max_tokens": 1500
            }
        )
        
        if response.status_code != 200:
            logger.error(f"ASI API error in analysis: {response.status_code}")
            return MarketValidation(
                is_valid=False,
                confidence=0.0,
                reasoning="Failed to analyze due to API error",
                yes_probability=0.5,
                no_probability=0.5,
                reliable_sources=[],
                resolution_date="",
                auto_expire=False
            )
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group())
            
            # Additional validation logic
            is_past_event = analysis.get("is_past_event", False)
            reliable_sources = analysis.get("reliable_sources", [])
            resolution_date = analysis.get("resolution_date", "")
            
            # Reject if it's a past event
            if is_past_event:
                return MarketValidation(
                    is_valid=False,
                    confidence=0.0,
                    reasoning="This market is about a past event. Prediction markets are for future events only.",
                    yes_probability=0.5,
                    no_probability=0.5,
                    reliable_sources=[],
                    resolution_date="",
                    auto_expire=False
                )
            
            # Reject if resolution date is in the past or today
            if resolution_date:
                try:
                    resolution_dt = datetime.strptime(resolution_date, "%Y-%m-%d")
                    current_dt = datetime.strptime(current_date, "%Y-%m-%d")
                    if resolution_dt <= current_dt:
                        return MarketValidation(
                            is_valid=False,
                            confidence=0.0,
                            reasoning=f"Resolution date {resolution_date} is not in the future. Current date is {current_date}.",
                            yes_probability=0.5,
                            no_probability=0.5,
                            reliable_sources=reliable_sources,
                            resolution_date=resolution_date,
                            auto_expire=analysis.get("auto_expire", False)
                        )
                except ValueError:
                    return MarketValidation(
                        is_valid=False,
                        confidence=0.0,
                        reasoning=f"Invalid resolution date format: {resolution_date}",
                        yes_probability=0.5,
                        no_probability=0.5,
                        reliable_sources=reliable_sources,
                        resolution_date=resolution_date,
                        auto_expire=analysis.get("auto_expire", False)
                    )
            
            # Reject if there aren't enough reliable sources
            if len(reliable_sources) < 3:
                return MarketValidation(
                    is_valid=False,
                    confidence=0.0,
                    reasoning=f"Insufficient reliable sources ({len(reliable_sources)} found, need at least 3). The resolver needs multiple credible sources to check for evidence.",
                    yes_probability=0.5,
                    no_probability=0.5,
                    reliable_sources=reliable_sources,
                    resolution_date=resolution_date,
                    auto_expire=analysis.get("auto_expire", False)
                )
            
            return MarketValidation(
                is_valid=analysis.get("is_valid", False),
                confidence=analysis.get("confidence", 0.0),
                reasoning=analysis.get("reasoning", "No reasoning provided"),
                yes_probability=analysis.get("yes_probability", 0.5),
                no_probability=analysis.get("no_probability", 0.5),
                reliable_sources=reliable_sources,
                resolution_date=resolution_date,
                auto_expire=analysis.get("auto_expire", False)
            )
        else:
            logger.warning("Could not parse analysis as JSON")
            return MarketValidation(
                is_valid=False,
                confidence=0.0,
                reasoning="Failed to parse analysis response",
                yes_probability=0.5,
                no_probability=0.5,
                reliable_sources=[],
                resolution_date="",
                auto_expire=False
            )
            
    except Exception as e:
        logger.error(f"Error in market analysis: {e}")
        return MarketValidation(
            is_valid=False,
            confidence=0.0,
            reasoning=f"Error during analysis: {str(e)}",
            yes_probability=0.5,
            no_probability=0.5,
            reliable_sources=[],
            resolution_date="",
            auto_expire=False
        )

def create_market_data(prompt: str, validation: MarketValidation, market_id: Optional[str] = None) -> MarketData:
    """Create market data based on validation results"""
    
    # Generate unique ID if market_id is not provided
    if not market_id:
        market_id = str(uuid.uuid4())
    
    # Set close time based on resolution date or default to 30 days
    if validation.resolution_date:
        try:
            close_time = datetime.strptime(validation.resolution_date, "%Y-%m-%d")
        except ValueError:
            close_time = datetime.now() + timedelta(days=30)
    else:
        close_time = datetime.now() + timedelta(days=30)
    
    # Use the validated probabilities
    initial_prob = validation.yes_probability
    
    return MarketData(
        id=market_id,
        title=f"Will {prompt}?",
        description=f"Prediction market: {prompt}. {validation.reasoning}",
        prompt=prompt,
        close_time_iso=close_time.isoformat(),
        outcomes=["YES", "NO"],
        initial_prob=initial_prob,
        validation=validation,
        created_at=datetime.now().isoformat(),
        status="active"
    )

@app.post("/generate", response_model=MarketResponse)
async def generate_market(request: MarketRequest):
    """Generate a prediction market based on the prompt"""
    
    if not ASI_API_KEY:
        raise HTTPException(status_code=500, detail="ASI API key not configured")
    
    try:
        logger.info(f"Processing market request: {request.prompt}")
        
        # Check if market with this ID already exists
        if request.market_id:
            markets = load_markets()
            if request.market_id in markets:
                logger.info(f"Market with ID {request.market_id} already exists, returning existing market")
                return MarketResponse(
                    success=True,
                    market=markets[request.market_id]
                )
        
        # Analyze market prompt using ASI-1 Mini
        validation = await analyze_market_prompt(request.prompt)
        logger.info(f"Market validation: valid={validation.is_valid}, confidence={validation.confidence}")
        
        if not validation.is_valid:
            return MarketResponse(
                success=False,
                error=f"Market validation failed: {validation.reasoning}"
            )
        
        # Create market data
        market_data = create_market_data(request.prompt, validation, request.market_id)
        
        # Store market locally
        markets = load_markets()
        markets[market_data.id] = market_data
        save_markets(markets)
        
        logger.info(f"Market created and stored: {market_data.id}")
        
        return MarketResponse(
            success=True,
            market=market_data
        )
        
    except Exception as e:
        logger.error(f"Error generating market: {e}")
        return MarketResponse(
            success=False,
            error=f"Internal error: {str(e)}"
        )

@app.post("/archive-expired")
async def archive_expired():
    """Manually trigger archiving of expired markets"""
    try:
        updated = archive_expired_markets()
        return {
            "success": True,
            "message": f"Archived {updated} expired markets" if updated else "No expired markets to archive",
            "archived_count": updated
        }
    except Exception as e:
        logger.error(f"Error archiving expired markets: {e}")
        raise HTTPException(status_code=500, detail=f"Error archiving markets: {str(e)}")

@app.get("/markets/active")
async def get_active_markets():
    """Get only active markets"""
    try:
        markets = load_markets()
        active_markets = {market_id: market for market_id, market in markets.items() if market.status == "active"}
        return {
            "total": len(active_markets),
            "markets": list(active_markets.values())
        }
    except Exception as e:
        logger.error(f"Error getting active markets: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading markets: {str(e)}")

@app.get("/markets/archived")
async def get_archived_markets():
    """Get only archived markets"""
    try:
        markets = load_markets()
        archived_markets = {market_id: market for market_id, market in markets.items() if market.status != "active"}
        return {
            "total": len(archived_markets),
            "markets": list(archived_markets.values())
        }
    except Exception as e:
        logger.error(f"Error getting archived markets: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading markets: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Clean up expired markets on startup"""
    try:
        updated = archive_expired_markets()
        if updated:
            logger.info(f"Archived {updated} expired markets on startup")
    except Exception as e:
        logger.error(f"Error during startup cleanup: {e}")

@app.get("/markets")
def list_markets():
    """List all stored markets"""
    markets = load_markets()
    return {
        "total": len(markets),
        "markets": [market.dict() for market in markets.values()]
    }

@app.get("/markets/{market_id}")
def get_market(market_id: str):
    """Get a specific market by ID"""
    markets = load_markets()
    if market_id in markets:
        return markets[market_id]
    raise HTTPException(status_code=404, detail="Market not found")

@app.get("/markets/{market_id}/outcome")
def get_market_outcome(market_id: str):
    """Get the outcome of a market (true, false, or undefined)"""
    markets = load_markets()
    if market_id not in markets:
        raise HTTPException(status_code=404, detail="Market not found")
    
    market = markets[market_id]
    
    # Check if market is resolved
    if market.status != "resolved":
        return {"outcome": "undefined", "status": market.status}
    
    # For now, return undefined since we don't have actual resolution logic
    # In a real implementation, this would check the actual outcome
    return {"outcome": "undefined", "status": market.status, "message": "Market not yet resolved"}

@app.delete("/markets/{market_id}")
def delete_market(market_id: str):
    """Delete a market by ID"""
    markets = load_markets()
    if market_id in markets:
        del markets[market_id]
        save_markets(markets)
        return {"message": "Market deleted successfully"}
    raise HTTPException(status_code=404, detail="Market not found")

@app.get("/health")
def health():
    """Health check endpoint"""
    markets = load_markets()
    return {
        "status": "healthy",
        "asi_api_configured": bool(ASI_API_KEY),
        "model": MODEL_NAME,
        "stored_markets": len(markets)
    }

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "service": "Market Generator Agent",
        "version": "1.0.0",
        "model": MODEL_NAME,
        "endpoints": {
            "POST /generate": "Generate a prediction market",
            "GET /markets": "List all markets",
            "GET /markets/{id}": "Get specific market",
            "DELETE /markets/{id}": "Delete market",
            "GET /health": "Health check"
        }
    }