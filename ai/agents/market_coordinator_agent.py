import os
import sys
import uuid
import logging
import asyncio
from typing import Dict, Optional, List
from pydantic import BaseModel, Field
from fastapi import FastAPI, Depends, HTTPException

# Ensure 'agents' is importable from anywhere
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import database modules (these should work)
try:
    from database import get_db, init_db, Market, SessionLocal
except ImportError as e:
    print(f"Failed to import database modules: {e}")
    raise

# Import generator modules (these might fail if generator isn't ready)
try:
    from generator.server import create_market_data, save_market_to_db, deploy_market, MarketValidation
except ImportError as e:
    print(f"Warning: Failed to import generator modules: {e}")
    create_market_data = None
    save_market_to_db = None
    deploy_market = None
    MarketValidation = None

from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent configuration
COORDINATOR_AGENT_SEED = "market_coordinator_seed_11111"
COORDINATOR_AGENT_PORT = 8002

# Create the agent
coordinator_agent = Agent(
    name="market_coordinator",
    port=COORDINATOR_AGENT_PORT,
    seed=COORDINATOR_AGENT_SEED,
    endpoint=["http://0.0.0.0:8002/submit"],
)

# Fund the agent (commented out for now)
# fund_agent_if_low(coordinator_agent.wallet.address())

# Message models
class MarketCreationRequest(BaseModel):
    prompt: str = Field(..., description="The market prompt to analyze")
    market_id: Optional[str] = Field(None, description="Optional custom market ID")
    request_id: str = Field(..., description="Unique request identifier")

class MarketCreationResponse(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    market_id: str = Field(..., description="Created market ID")
    success: bool = Field(..., description="Whether creation was successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    market_data: Optional[Dict] = Field(None, description="Market data if successful")

class MarketAnalysisRequest(BaseModel):
    prompt: str = Field(..., description="The market prompt to analyze")
    request_id: str = Field(..., description="Unique request identifier")

class MarketAnalysisResponse(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    validation: Dict = Field(..., description="Market validation data")
    success: bool = Field(..., description="Whether analysis was successful")
    error: Optional[str] = Field(None, description="Error message if failed")

class MarketResolutionRequest(BaseModel):
    market_id: str = Field(..., description="Market ID to resolve")
    prompt: str = Field(..., description="The market prompt")
    reliable_sources: List[str] = Field(default_factory=list, description="Reliable sources to check")
    request_id: str = Field(..., description="Unique request identifier")

class MarketResolutionResponse(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    market_id: str = Field(..., description="Market ID")
    outcome: str = Field(..., description="YES, NO, or INSUFFICIENT_EVIDENCE")
    confidence: float = Field(..., description="Confidence score")
    evidence: List[str] = Field(default_factory=list, description="Evidence found")
    success: bool = Field(..., description="Whether resolution was successful")
    error: Optional[str] = Field(None, description="Error message if failed")

# Store pending requests
pending_requests: Dict[str, Dict] = {}

# Lazy import function for other agents
def get_generator_agent():
    """Lazy import of generator agent"""
    try:
        from agents.market_generator_agent import generator_agent
        return generator_agent
    except ImportError as e:
        logger.error(f"Failed to import generator agent: {e}")
        return None

def get_resolver_agent():
    """Lazy import of resolver agent"""
    try:
        from agents.market_resolver_agent import resolver_agent
        return resolver_agent
    except ImportError as e:
        logger.error(f"Failed to import resolver agent: {e}")
        return None

# Protocol for market coordination
class MarketCoordinatorProtocol(Protocol):
    def __init__(self):
        super().__init__()
        
    @coordinator_agent.on_message(model=MarketCreationRequest)
    async def handle_market_creation(self, ctx: Context, sender: str, msg: MarketCreationRequest):
        """Handle market creation requests - coordinates between generator and blockchain"""
        logger.info(f"🎯 Received market creation request: {msg.request_id}")
        logger.info(f"   Prompt: {msg.prompt}")
        
        try:
            # Step 1: Send to generator agent for analysis via μAgent protocol
            generator_request = MarketAnalysisRequest(
                prompt=msg.prompt,
                request_id=str(uuid.uuid4())
            )
            
            # Store the original request for later processing
            pending_requests[generator_request.request_id] = {
                "type": "market_creation",
                "original_request": msg,
                "sender": sender
            }
            
            # Send to generator agent via uagents protocol
            logger.info(f"📤 Sending to generator agent: {generator_request.request_id}")
            # Import generator agent to get its address
            generator_agent = get_generator_agent()
            if not generator_agent:
                response = MarketCreationResponse(
                    request_id=msg.request_id,
                    market_id="",
                    success=False,
                    error="Generator agent not available"
                )
                await ctx.send(sender, response)
                return
            
            await ctx.send(generator_agent.address, generator_request)
            
        except Exception as e:
            logger.error(f"❌ Market creation failed: {msg.request_id}")
            logger.error(f"   Error: {e}")
            
            response = MarketCreationResponse(
                request_id=msg.request_id,
                market_id="",
                success=False,
                error=str(e)
            )
            
            await ctx.send(sender, response)
    
    @coordinator_agent.on_message(model=MarketAnalysisResponse)
    async def handle_market_analysis_response(self, ctx: Context, sender: str, msg: MarketAnalysisResponse):
        """Handle response from generator agent"""
        logger.info(f"📥 Received market analysis response: {msg.request_id}")
        
        if msg.request_id not in pending_requests:
            logger.error(f"❌ Unknown request ID: {msg.request_id}")
            return
            
        pending_request = pending_requests[msg.request_id]
        original_request = pending_request["original_request"]
        original_sender = pending_request["sender"]
        
        if not msg.success:
            # Analysis failed
            response = MarketCreationResponse(
                request_id=original_request.request_id,
                market_id="",
                success=False,
                error=msg.error
            )
            await ctx.send(original_sender, response)
            del pending_requests[msg.request_id]
            return
        
        try:
            # Step 2: Create market data
            market_id = original_request.market_id or str(uuid.uuid4())
            
            # Initialize database
            init_db()
            
            # Create market data from generator response
            if MarketValidation:
                validation = MarketValidation(
                    is_valid=msg.validation.get("is_valid", True),
                    confidence=msg.validation.get("confidence", 0.85),
                    reasoning=msg.validation.get("reasoning", "Market validation completed"),
                    yes_probability=msg.validation.get("yes_probability", 0.5),
                    no_probability=msg.validation.get("no_probability", 0.5),
                    reliable_sources=msg.validation.get("reliable_sources", ["Reuters", "Bloomberg"]),
                    resolution_date=msg.validation.get("resolution_date", "2026-12-31"),
                    auto_expire=msg.validation.get("auto_expire", True)
                )
            else:
                validation = {
                    "is_valid": msg.validation.get("is_valid", True),
                    "confidence": msg.validation.get("confidence", 0.85),
                    "reasoning": msg.validation.get("reasoning", "Market validation completed"),
                    "yes_probability": msg.validation.get("yes_probability", 0.5),
                    "no_probability": msg.validation.get("no_probability", 0.5),
                    "reliable_sources": msg.validation.get("reliable_sources", ["Reuters", "Bloomberg"]),
                    "resolution_date": msg.validation.get("resolution_date", "2026-12-31"),
                    "auto_expire": msg.validation.get("auto_expire", True)
                }
            
            if create_market_data:
                market_data = create_market_data(original_request.prompt, validation, market_id)
            else:
                market_data = {"id": market_id, "title": f"Market for {original_request.prompt}", "validation": validation}
            
            # Step 3: Save to database
            db = SessionLocal()
            try:
                if save_market_to_db:
                    save_market_to_db(db, market_data)
                    logger.info(f"💾 Market saved to database: {market_id}")
                else:
                    logger.warning(f"⚠️ save_market_to_db is not available, skipping database save for {market_id}")
            finally:
                db.close()
            
            # Step 4: Deploy to blockchain
            url = f"https://prove-me-wrong-production.up.railway.app/resolver/resolutions/{market_id}/outcome"
            
            blockchain_deployed = False
            if deploy_market:
                try:
                    blockchain_deployed = deploy_market(
                        market_id=market_data.id,
                        title=market_data.title,
                        url=url,
                        yes_probability=market_data.validation.yes_probability,
                        no_probability=market_data.validation.no_probability,
                    )
                    
                    if blockchain_deployed:
                        logger.info(f"✅ Market deployed to blockchain: {market_id}")
                    else:
                        logger.error(f"❌ Blockchain deployment failed: {market_id}")
                        # Delete from database if blockchain deployment fails
                        db = SessionLocal()
                        try:
                            db_market = db.query(Market).filter(Market.id == market_id).first()
                            if db_market:
                                db.delete(db_market)
                                db.commit()
                                logger.info(f"🗑️ Deleted market from database: {market_id}")
                        finally:
                            db.close()
                        
                        response = MarketCreationResponse(
                            request_id=original_request.request_id,
                            market_id=market_id,
                            success=False,
                            error="Blockchain deployment failed"
                        )
                        await ctx.send(original_sender, response)
                        del pending_requests[msg.request_id]
                        return
                    
                except Exception as e:
                    logger.error(f"❌ Blockchain deployment error: {e}")
                    # Delete from database
                    db = SessionLocal()
                    try:
                        db_market = db.query(Market).filter(Market.id == market_id).first()
                        if db_market:
                            db.delete(db_market)
                            db.commit()
                            logger.info(f"🗑️ Deleted market from database: {market_id}")
                    finally:
                        db.close()
                    
                    response = MarketCreationResponse(
                        request_id=original_request.request_id,
                        market_id=market_id,
                        success=False,
                        error=f"Blockchain deployment failed: {str(e)}"
                    )
                    await ctx.send(original_sender, response)
                    del pending_requests[msg.request_id]
                    return
            else:
                logger.error(f"❌ deploy_market is not available, blockchain deployment is mandatory")
                # Delete from database since blockchain deployment is mandatory
                db = SessionLocal()
                try:
                    db_market = db.query(Market).filter(Market.id == market_id).first()
                    if db_market:
                        db.delete(db_market)
                        db.commit()
                        logger.info(f"🗑️ Deleted market from database: {market_id}")
                finally:
                    db.close()
                
                response = MarketCreationResponse(
                    request_id=original_request.request_id,
                    market_id=market_id,
                    success=False,
                    error="Blockchain deployment is mandatory but deploy_market function is not available"
                )
                await ctx.send(original_sender, response)
                del pending_requests[msg.request_id]
                return
            
            # Step 5: Send success response
            logger.info(f"✅ Market creation completed: {market_id}")
            
            response = MarketCreationResponse(
                request_id=original_request.request_id,
                market_id=market_id,
                success=True,
                market_data=market_data.dict()
            )
            
            await ctx.send(original_sender, response)
            del pending_requests[msg.request_id]
            
        except Exception as e:
            logger.error(f"❌ Market creation failed: {original_request.request_id}")
            logger.error(f"   Error: {e}")
            
            response = MarketCreationResponse(
                request_id=original_request.request_id,
                market_id="",
                success=False,
                error=str(e)
            )
            
            await ctx.send(original_sender, response)
            del pending_requests[msg.request_id]

    @coordinator_agent.on_message(model=MarketResolutionResponse)
    async def handle_market_resolution_response(self, ctx: Context, sender: str, msg: MarketResolutionResponse):
        """Handle response from resolver agent"""
        logger.info(f"📥 Received market resolution response: {msg.request_id}")
        
        if msg.request_id not in pending_requests:
            logger.error(f"❌ Unknown request ID: {msg.request_id}")
            return
            
        pending_request = pending_requests[msg.request_id]
        original_request = pending_request["original_request"]
        original_sender = pending_request["sender"]
        
        if not msg.success:
            # Resolution failed
            response = MarketResolutionResponse(
                request_id=original_request.request_id,
                market_id=original_request.market_id,
                outcome="INSUFFICIENT_EVIDENCE",
                confidence=0.0,
                evidence=[],
                success=False,
                error=msg.error
            )
            await ctx.send(original_sender, response)
            del pending_requests[msg.request_id]
            return
        
        # Resolution successful
        logger.info(f"✅ Market resolution completed: {msg.market_id}")
        logger.info(f"   Outcome: {msg.outcome}")
        logger.info(f"   Confidence: {msg.confidence}")
        
        # Send response back to original sender
        await ctx.send(original_sender, msg)
        del pending_requests[msg.request_id]

# Create FastAPI app for HTTP endpoints
app = FastAPI(title="Market Coordinator Agent", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Startup event to ensure the coordinator agent starts properly"""
    logger.info("🚀 Coordinator agent starting up...")
    try:
        # Try to register protocol but don't fail if it doesn't work
        register_protocol()
        logger.info("✅ Coordinator agent startup completed")
    except Exception as e:
        logger.error(f"❌ Coordinator agent startup error: {e}")
        logger.warning("⚠️ Coordinator agent starting in HTTP-only mode")

# HTTP endpoint models
class HTTPMarketCreationRequest(BaseModel):
    prompt: str = Field(..., description="The market prompt to analyze")
    market_id: Optional[str] = Field(None, description="Optional custom market ID")

class HTTPMarketResolutionRequest(BaseModel):
    market_id: str = Field(..., description="Market ID to resolve")
    prompt: str = Field(..., description="The market prompt")
    reliable_sources: List[str] = Field(default_factory=list, description="Reliable sources to check")

@app.post("/create-market")
async def http_create_market(request: HTTPMarketCreationRequest):
    """HTTP endpoint for market creation - uses μAgent communication"""
    request_id = str(uuid.uuid4())
    
    # Create μAgent request
    uagent_request = MarketCreationRequest(
        prompt=request.prompt,
        market_id=request.market_id,
        request_id=request_id
    )
    
    # Store the original request for later processing
    pending_requests[request_id] = {
        "type": "market_creation",
        "original_request": uagent_request,
        "sender": "http_client"
    }
    
    # Send via μAgent protocol
    generator_agent = get_generator_agent()
    if not generator_agent:
        return {
            "request_id": request_id,
            "status": "error",
            "message": "Generator agent not available"
        }

    try:
        await coordinator_agent.send(generator_agent.address, uagent_request)
    except Exception as e:
        logger.error(f"Failed to send market creation request to generator agent: {e}")
        return {
            "request_id": request_id,
            "status": "error",
            "message": f"Failed to send request to generator agent: {e}"
        }
    
    # For now, return immediate response (in real implementation, you'd wait for the response)
    return {
        "request_id": request_id,
        "status": "processing",
        "message": "Market creation request sent to μAgent system"
    }

@app.post("/resolve-market")
async def http_resolve_market(request: HTTPMarketResolutionRequest):
    """HTTP endpoint for market resolution - uses μAgent communication"""
    request_id = str(uuid.uuid4())
    
    # Create μAgent request
    uagent_request = MarketResolutionRequest(
        market_id=request.market_id,
        prompt=request.prompt,
        reliable_sources=request.reliable_sources,
        request_id=request_id
    )
    
    # Store the original request for later processing
    pending_requests[request_id] = {
        "type": "market_resolution",
        "original_request": uagent_request,
        "sender": "http_client"
    }
    
    # Send via μAgent protocol
    resolver_agent = get_resolver_agent()
    if not resolver_agent:
        return {
            "request_id": request_id,
            "status": "error",
            "message": "Resolver agent not available - μAgent communication disabled"
        }

    try:
        await coordinator_agent.send(resolver_agent.address, uagent_request)
    except Exception as e:
        logger.error(f"Failed to send market resolution request to resolver agent: {e}")
        return {
            "request_id": request_id,
            "status": "error",
            "message": f"Failed to send request to resolver agent: {e}"
        }
    
    # For now, return immediate response (in real implementation, you'd wait for the response)
    return {
        "request_id": request_id,
        "status": "processing",
        "message": "Market resolution request sent to μAgent system"
    }

@app.get("/markets")
async def list_markets(db: Session = Depends(get_db)):
    """List all markets in database"""
    markets = db.query(Market).all()
    return [
        {
            "id": market.id,
            "title": market.title,
            "status": market.status,
            "outcome": market.outcome,
            "created_at": market.created_at.isoformat() if market.created_at else None,
            "resolved_at": market.resolved_at.isoformat() if market.resolved_at else None
        }
        for market in markets
    ]

@app.get("/resolutions/{market_id}/outcome")
async def get_market_outcome(market_id: str, db: Session = Depends(get_db)):
    """Get the outcome of a market (0, 1, or 2) - EXACT SAME AS ORIGINAL RESOLVER"""
    db_market = db.query(Market).filter(Market.id == market_id).first()
    if not db_market:
        raise HTTPException(status_code=404, detail="Market not found")
    
    # Check if market is resolved - EXACT SAME LOGIC AS ORIGINAL
    if db_market.outcome == "YES":
        return {"outcome": 1}
    elif db_market.outcome == "NO":
        return {"outcome": 0}
    else:
        return {"outcome": 2}  # INSUFFICIENT_EVIDENCE, EXPIRED, etc.

@app.get("/resolutions")
async def list_resolutions(db: Session = Depends(get_db)):
    """List all resolved markets - EXACT SAME AS ORIGINAL RESOLVER"""
    markets = db.query(Market).filter(Market.outcome.isnot(None)).all()
    return {
        "total": len(markets),
        "resolutions": [
            {
                "market_id": market.id,
                "outcome": market.outcome,
                "resolved_at": market.resolved_at.isoformat() if market.resolved_at else None
            }
            for market in markets
        ]
    }

@app.get("/resolutions/{market_id}")
async def get_resolution(market_id: str, db: Session = Depends(get_db)):
    """Get a specific resolution by market ID - EXACT SAME AS ORIGINAL RESOLVER"""
    db_market = db.query(Market).filter(Market.id == market_id).first()
    if not db_market:
        raise HTTPException(status_code=404, detail="Market not found")
    
    return {
        "market_id": db_market.id,
        "outcome": db_market.outcome,
        "resolved_at": db_market.resolved_at.isoformat() if db_market.resolved_at else None
    }

@app.post("/resolve-all")
async def resolve_all_markets(db: Session = Depends(get_db)):
    """Resolve all active markets - EXACT SAME AS ORIGINAL RESOLVER"""
    # Get all unresolved markets
    unresolved_markets = db.query(Market).filter(Market.outcome.is_(None)).all()
    
    results = []
    for market in unresolved_markets:
        try:
            # Create resolution request
            request_id = str(uuid.uuid4())
            uagent_request = MarketResolutionRequest(
                market_id=market.id,
                prompt=market.title,
                reliable_sources=["Reuters", "Bloomberg", "AP"],
                request_id=request_id
            )
            
            # Store the request
            pending_requests[request_id] = {
                "type": "market_resolution",
                "original_request": uagent_request,
                "sender": "resolve_all"
            }
            
            # Send to resolver agent
            resolver_agent = get_resolver_agent()
            if not resolver_agent:
                results.append({
                    "market_id": market.id,
                    "status": "error",
                    "error": "Resolver agent not available - μAgent communication disabled"
                })
                continue

            try:
                await coordinator_agent.send(resolver_agent.address, uagent_request)
            except Exception as e:
                logger.error(f"Failed to send market resolution request to resolver agent for resolve_all: {e}")
                results.append({
                    "market_id": market.id,
                    "status": "error",
                    "error": f"Failed to send request to resolver agent: {e}"
                })
                continue
            
            results.append({
                "market_id": market.id,
                "status": "processing",
                "request_id": request_id
            })
            
        except Exception as e:
            results.append({
                "market_id": market.id,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "total_markets": len(unresolved_markets),
        "results": results
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check if other agents are available
    generator_agent = get_generator_agent()
    resolver_agent = get_resolver_agent()
    
    return {
        "status": "healthy",
        "agent": "market_coordinator",
        "port": COORDINATOR_AGENT_PORT,
        "pending_requests": len(pending_requests),
        "uagent_communication": {
            "generator_available": generator_agent is not None,
            "resolver_available": resolver_agent is not None
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Prove Me Wrong - Market Coordinator Agent",
        "version": "1.0.0",
        "endpoints": {
            "create_market": "POST /create-market",
            "resolve_market": "POST /resolve-market",
            "resolve_all": "POST /resolve-all",
            "list_markets": "GET /markets",
            "list_resolutions": "GET /resolutions",
            "get_resolution": "GET /resolutions/{market_id}",
            "get_outcome": "GET /resolutions/{market_id}/outcome",
            "health": "GET /health"
        }
    }

# Include the protocol only if other agents are available
def register_protocol():
    try:
        # Test if other agents are available
        generator_agent = get_generator_agent()
        resolver_agent = get_resolver_agent()
        if generator_agent and resolver_agent:
            coordinator_agent.include(MarketCoordinatorProtocol())
            logger.info("✅ μAgent protocol registered successfully")
            return True
        else:
            logger.warning("⚠️ μAgent protocol not registered due to missing agents.")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to register μAgent protocol: {e}")
        logger.warning("⚠️ Running in HTTP-only mode (μAgent communication disabled)")
        return False

if __name__ == "__main__":
    import uvicorn
    # Don't register protocol at startup - let it be lazy
    uvicorn.run(app, host="0.0.0.0", port=COORDINATOR_AGENT_PORT) 