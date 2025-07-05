from fastapi import FastAPI, HTTPException, Depends
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
from sqlalchemy.orm import Session
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db, init_db, Market, SessionLocal

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

# Localhost Configuration
LOCALHOST_URL = os.getenv("LOCALHOST_URL", None)

# ASI-1 Mini API Configuration
ASI_API_URL = "https://api.asi1.ai/v1/chat/completions"
ASI_API_KEY = os.getenv("ASI_API_KEY", "sk_a1d55fd6b1ba47ddadc98bd1e8048e56ff00c4736c844a9db4aab791d33f0989")
MODEL_NAME = "asi1-mini"

# Database storage for markets (replaces file storage)

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
    outcome: Optional[str] = None  # YES, NO, or None
    resolved_at: Optional[str] = None
    resolution_confidence: Optional[float] = None

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
def deploy_market(
    market_id: str,
    title: str,
    url: str,
    yes_probability: float,
    no_probability: float,
) -> bool:
    """Deploy market to the blockchain using admin wallet"""
    
    w3 = get_web3_instance()
    if not w3:
        logger.warning("Web3 not available, skipping blockchain deployment")
        return False
    
    if ADMIN_PRIVATE_KEY is None:
        logger.warning("ADMIN_PRIVATE_KEY not configured, skipping blockchain deployment")
        return False
    
    if PMW_ADDRESS is None:
        logger.warning("PMW_ADDRESS not configured, skipping blockchain deployment")
        return False

    if PMW_POOL_ADDRESS is None:
        logger.warning("PMW_POOL_ADDRESS not configured, skipping blockchain deployment")
        return False
    
    try:
        # Create account from private key
        account = Account.from_key(ADMIN_PRIVATE_KEY)
        
        # Create contract instance
        contract = w3.eth.contract(address=Web3.to_checksum_address(PMW_ADDRESS), abi=get_contract_abi())
        
        # Prepare market data for blockchain
        request_hash = Web3.keccak(text=
            url + 
            "GET" + 
            "{}" + 
            "{}" + 
            "{}" + 
            "{outcome: .outcome}" + 
            '{"components": [ {"internalType": "uint256", "name": "outcome", "type": "uint256"} ],"name": "task", "type": "tuple"}'
        )
        
        # Convert probabilities to price format (1e18 = 100%)
        yes_price = int(yes_probability * 1e18)
        no_price = int(no_probability * 1e18)
        
        # Ensure prices sum to 1e18 (100%)
        total_price = yes_price + no_price
        if total_price != 1e18:
            # Normalize prices
            yes_price = (yes_price * 1e18) // total_price
            no_price = 1e18 - yes_price
        
        # Build transaction
        transaction = contract.functions.createMarket(
            Web3.keccak(text=market_id),
            request_hash,
            title,
            f"PMW-{title.upper()}",  # Symbol
            yes_price,
            no_price,
            Web3.to_checksum_address(PMW_POOL_ADDRESS)
        ).build_transaction({
            'from': account.address,
            'gas': 2000000,  # Adjust gas limit as needed
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
            'chainId': CHAIN_ID
        })
        
        # Sign and send transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, ADMIN_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f"Market deployed to blockchain: {market_id}, tx: {tx_hash.hex()}")
        # Wait for transaction receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt["status"] == 1:
            logger.info(f"Market deployed to blockchain: {market_id}, tx: {tx_hash.hex()}")
            return True
        else:
            logger.error(f"Transaction failed: {tx_hash.hex()}")
            return False
            
    except Exception as e:
        logger.error(f"Error deploying market to blockchain: {e}")
        return False
      
def load_markets_from_db(db: Session) -> Dict[str, MarketData]:
    """Load markets from database"""
    markets = {}
    try:
        db_markets = db.query(Market).all()
        for db_market in db_markets:
            market_data = {
                "id": db_market.id,
                "title": db_market.title,
                "description": db_market.description,
                "prompt": db_market.prompt,
                "close_time_iso": db_market.close_time_iso,
                "outcomes": db_market.outcomes,
                "initial_prob": db_market.initial_prob,
                "validation": db_market.validation,
                "created_at": db_market.created_at,
                "status": db_market.status,
                "outcome": db_market.outcome,
                "resolved_at": db_market.resolved_at,
                "resolution_confidence": db_market.resolution_confidence
            }
            markets[db_market.id] = MarketData(**market_data)
    except Exception as e:
        logger.error(f"Error loading markets from database: {e}")
    
    return markets

def save_market_to_db(db: Session, market: MarketData):
    """Save market to database"""
    try:
        db_market = Market(
            id=market.id,
            title=market.title,
            description=market.description,
            prompt=market.prompt,
            close_time_iso=market.close_time_iso,
            outcomes=market.outcomes,
            initial_prob=market.initial_prob,
            validation=market.validation.dict(),
            created_at=market.created_at,
            status=market.status,
            outcome=market.outcome,
            resolved_at=market.resolved_at,
            resolution_confidence=market.resolution_confidence
        )
        
        # Check if market exists
        existing_market = db.query(Market).filter(Market.id == market.id).first()
        if existing_market:
            # Update existing market
            for key, value in market.dict().items():
                if key == "validation":
                    setattr(existing_market, key, market.validation.dict())
                else:
                    setattr(existing_market, key, value)
        else:
            # Add new market
            db.add(db_market)
        
        db.commit()
        logger.info(f"Saved market to database: {market.id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving market to database: {e}")
        raise


def archive_expired_markets(db: Session):
    """Move expired markets to archived status in database"""
    current_time = datetime.now()
    updated = False
    
    try:
        active_markets = db.query(Market).filter(Market.status == "active").all()
        for db_market in active_markets:
            try:
                close_time = datetime.fromisoformat(db_market.close_time_iso.replace('Z', '+00:00'))
                if close_time <= current_time:
                    db_market.status = "expired"
                    updated = True
                    logger.info(f"Archived expired market: {db_market.title}")
            except Exception as e:
                logger.error(f"Error checking market expiration: {e}")
        
        if updated:
            db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error archiving expired markets: {e}")
    
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
async def generate_market(request: MarketRequest, db: Session = Depends(get_db)):
    """Generate a prediction market based on the prompt"""
    
    if not ASI_API_KEY:
        raise HTTPException(status_code=500, detail="ASI API key not configured")
    
    try:
        logger.info(f"Processing market request: {request.prompt}")
        
        # Check if market with this ID already exists
        if request.market_id:
            existing_market = db.query(Market).filter(Market.id == request.market_id).first()
            if existing_market:
                logger.info(f"Market with ID {request.market_id} already exists, returning existing market")
                market_data = MarketData(
                    id=existing_market.id,
                    title=existing_market.title,
                    description=existing_market.description,
                    prompt=existing_market.prompt,
                    close_time_iso=existing_market.close_time_iso,
                    outcomes=existing_market.outcomes,
                    initial_prob=existing_market.initial_prob,
                    validation=MarketValidation(**existing_market.validation),
                    created_at=existing_market.created_at,
                    status=existing_market.status,
                    outcome=existing_market.outcome,
                    resolved_at=existing_market.resolved_at,
                    resolution_confidence=existing_market.resolution_confidence
                )
                return MarketResponse(success=True, market=market_data)
        
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
        
        # Store market in database
        save_market_to_db(db, market_data)
        
        logger.info(f"Market created and stored: {market_data.id}")

        url = f"{LOCALHOST_URL}/resolutions/{market_data.id}/outcome"

        # Deploy the market to the blockchain
        blockchain_deployed = False
        try:            
            blockchain_deployed = deploy_market(
                market_id=market_data.id,
                title=market_data.title,
                url=url,
                yes_probability=market_data.validation.yes_probability,
                no_probability=market_data.validation.no_probability,
            )
            if blockchain_deployed:
                logger.info(f"Market successfully deployed to blockchain: {market_data.id}")
            else:
                logger.warning(f"Failed to deploy market to blockchain: {market_data.id}")
        except Exception as e:
            logger.error(f"Error deploying to blockchain: {e}")
            # Continue with local storage even if blockchain deployment fails
        
        # Add blockchain deployment status to market data
        market_data.blockchain_deployed = blockchain_deployed
        
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
async def archive_expired(db: Session = Depends(get_db)):
    """Manually trigger archiving of expired markets"""
    try:
        updated = archive_expired_markets(db)
        return {
            "success": True,
            "message": f"Archived {updated} expired markets" if updated else "No expired markets to archive",
            "archived_count": updated
        }
    except Exception as e:
        logger.error(f"Error archiving expired markets: {e}")
        raise HTTPException(status_code=500, detail=f"Error archiving markets: {str(e)}")

@app.get("/markets/active")
async def get_active_markets(db: Session = Depends(get_db)):
    """Get only active markets"""
    try:
        db_markets = db.query(Market).filter(Market.status == "active").all()
        markets = []
        for db_market in db_markets:
            market_data = MarketData(
                id=db_market.id,
                title=db_market.title,
                description=db_market.description,
                prompt=db_market.prompt,
                close_time_iso=db_market.close_time_iso,
                outcomes=db_market.outcomes,
                initial_prob=db_market.initial_prob,
                validation=MarketValidation(**db_market.validation),
                created_at=db_market.created_at,
                status=db_market.status,
                outcome=db_market.outcome,
                resolved_at=db_market.resolved_at,
                resolution_confidence=db_market.resolution_confidence
            )
            markets.append(market_data)
        
        return {
            "total": len(markets),
            "markets": markets
        }
    except Exception as e:
        logger.error(f"Error getting active markets: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading markets: {str(e)}")

@app.get("/markets/archived")
async def get_archived_markets(db: Session = Depends(get_db)):
    """Get only archived markets"""
    try:
        db_markets = db.query(Market).filter(Market.status != "active").all()
        markets = []
        for db_market in db_markets:
            market_data = MarketData(
                id=db_market.id,
                title=db_market.title,
                description=db_market.description,
                prompt=db_market.prompt,
                close_time_iso=db_market.close_time_iso,
                outcomes=db_market.outcomes,
                initial_prob=db_market.initial_prob,
                validation=MarketValidation(**db_market.validation),
                created_at=db_market.created_at,
                status=db_market.status,
                outcome=db_market.outcome,
                resolved_at=db_market.resolved_at,
                resolution_confidence=db_market.resolution_confidence
            )
            markets.append(market_data)
        
        return {
            "total": len(markets),
            "markets": markets
        }
    except Exception as e:
        logger.error(f"Error getting archived markets: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading markets: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize database and clean up expired markets on startup"""
    try:
        init_db()
        logger.info("Database initialized successfully")
        
        # Archive expired markets
        db = SessionLocal()
        try:
            updated = archive_expired_markets(db)
            if updated:
                logger.info(f"Archived {updated} expired markets on startup")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error during startup: {e}")

@app.get("/markets")
def list_markets(db: Session = Depends(get_db)):
    """List all stored markets"""
    db_markets = db.query(Market).all()
    markets = []
    for db_market in db_markets:
        market_data = MarketData(
            id=db_market.id,
            title=db_market.title,
            description=db_market.description,
            prompt=db_market.prompt,
            close_time_iso=db_market.close_time_iso,
            outcomes=db_market.outcomes,
            initial_prob=db_market.initial_prob,
            validation=MarketValidation(**db_market.validation),
            created_at=db_market.created_at,
            status=db_market.status,
            outcome=db_market.outcome,
            resolved_at=db_market.resolved_at,
            resolution_confidence=db_market.resolution_confidence
        )
        markets.append(market_data)
    
    return {
        "total": len(markets),
        "markets": [market.dict() for market in markets]
    }

@app.get("/markets/{market_id}")
def get_market(market_id: str, db: Session = Depends(get_db)):
    """Get a specific market by ID"""
    db_market = db.query(Market).filter(Market.id == market_id).first()
    if db_market:
        market_data = MarketData(
            id=db_market.id,
            title=db_market.title,
            description=db_market.description,
            prompt=db_market.prompt,
            close_time_iso=db_market.close_time_iso,
            outcomes=db_market.outcomes,
            initial_prob=db_market.initial_prob,
            validation=MarketValidation(**db_market.validation),
            created_at=db_market.created_at,
            status=db_market.status,
            outcome=db_market.outcome,
            resolved_at=db_market.resolved_at,
            resolution_confidence=db_market.resolution_confidence
        )
        return market_data
    raise HTTPException(status_code=404, detail="Market not found")

@app.get("/markets/{market_id}/outcome")
def get_market_outcome(market_id: str, db: Session = Depends(get_db)):
    """Get the outcome of a market (true, false, or undefined)"""
    db_market = db.query(Market).filter(Market.id == market_id).first()
    if not db_market:
        raise HTTPException(status_code=404, detail="Market not found")
    
    # Check if market is resolved
    if db_market.status == "resolved" and db_market.outcome:
        if db_market.outcome == "YES":
            return {"outcome": True}
        elif db_market.outcome == "NO":
            return {"outcome": False}
        else:
            return {"outcome": False}  # Treat any other outcome as false
    elif db_market.status == "expired":
        return {"outcome": False}  # Expired markets are false
    else:
        return {"outcome": "undefined"}  # Market not yet resolved

@app.put("/markets/{market_id}/outcome")
def update_market_outcome(market_id: str, outcome_data: dict, db: Session = Depends(get_db)):
    """Update the outcome of a market (called by resolver)"""
    db_market = db.query(Market).filter(Market.id == market_id).first()
    if not db_market:
        raise HTTPException(status_code=404, detail="Market not found")
    
    # Update market with outcome data
    db_market.status = "resolved"
    db_market.outcome = outcome_data.get("outcome")  # YES, NO, or EXPIRED
    db_market.resolved_at = outcome_data.get("resolved_at", datetime.now().isoformat())
    db_market.resolution_confidence = outcome_data.get("confidence")
    
    # Save updated market
    db.commit()
    
    logger.info(f"Updated market {market_id} with outcome: {db_market.outcome}")
    
    return {
        "success": True,
        "message": f"Market {market_id} resolved as {db_market.outcome}"
    }

@app.delete("/markets/{market_id}")
def delete_market(market_id: str, db: Session = Depends(get_db)):
    """Delete a market by ID"""
    db_market = db.query(Market).filter(Market.id == market_id).first()
    if db_market:
        db.delete(db_market)
        db.commit()
        return {"message": "Market deleted successfully"}
    raise HTTPException(status_code=404, detail="Market not found")

@app.get("/health")
def health():
    """Health check endpoint"""
    try:
        # Try to get a database session
        db = SessionLocal()
        try:
            market_count = db.query(Market).count()
            return {
                "status": "healthy",
                "asi_api_configured": bool(ASI_API_KEY),
                "model": MODEL_NAME,
                "stored_markets": market_count
            }
        except Exception as e:
            logger.error(f"Health check DB error: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "asi_api_configured": bool(ASI_API_KEY),
                "model": MODEL_NAME
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "asi_api_configured": bool(ASI_API_KEY),
            "model": MODEL_NAME
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