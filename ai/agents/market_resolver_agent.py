from uagents import Agent, Context, Protocol
from pydantic import BaseModel, Field
import requests
import json
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
import sys
import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from resolver.server import resolve_market
except ImportError:
    # For Railway deployment, try direct import
    from resolver.server import resolve_market

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent configuration
RESOLVER_AGENT_SEED = "market_resolver_seed_67890"
RESOLVER_AGENT_PORT = 8001

# Create the agent
resolver_agent = Agent(
    name="market_resolver",
    port=RESOLVER_AGENT_PORT,
    seed=RESOLVER_AGENT_SEED,
    endpoint=["http://0.0.0.0:8001/submit"],
)

# Fund the agent (commented out for now)
# fund_agent_if_low(resolver_agent.wallet.address())

# Message models
class MarketResolutionRequest(BaseModel):
    market_id: str = Field(..., description="Market ID to resolve")
    prompt: str = Field(..., description="Market prompt")
    reliable_sources: List[str] = Field(..., description="List of reliable sources")
    request_id: str = Field(..., description="Unique request identifier")

class MarketResolutionResponse(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    market_id: str = Field(..., description="Market ID")
    outcome: Optional[str] = Field(None, description="YES, NO, or INSUFFICIENT_EVIDENCE")
    confidence: Optional[float] = Field(None, description="Confidence score")
    evidence: List[str] = Field(default_factory=list, description="Evidence found")
    success: bool = Field(..., description="Whether resolution was successful")
    error: Optional[str] = Field(None, description="Error message if failed")

# Protocol for market resolution
class MarketResolverProtocol(Protocol):
    def __init__(self):
        super().__init__()
        
    @resolver_agent.on_message(model=MarketResolutionRequest)
    async def handle_market_resolution(self, ctx: Context, sender: str, msg: MarketResolutionRequest):
        """Handle market resolution requests - PRESERVES ALL EXISTING LOGIC"""
        logger.info(f"🔍 Received market resolution request: {msg.request_id}")
        logger.info(f"   Market ID: {msg.market_id}")
        logger.info(f"   Prompt: {msg.prompt}")
        
        try:
            # PRESERVE EXACTLY the existing resolve_market function
            resolution_result = await resolve_market(
                market_id=msg.market_id,
                prompt=msg.prompt,
                reliable_sources=msg.reliable_sources
            )
            
            logger.info(f"✅ Market resolution completed: {msg.request_id}")
            logger.info(f"   Outcome: {resolution_result.get('outcome')}")
            logger.info(f"   Confidence: {resolution_result.get('confidence')}")
            
            # Send response
            response = MarketResolutionResponse(
                request_id=msg.request_id,
                market_id=msg.market_id,
                outcome=resolution_result.get('outcome'),
                confidence=resolution_result.get('confidence'),
                evidence=resolution_result.get('evidence', []),
                success=True
            )
            
            await ctx.send(sender, response)
            
        except Exception as e:
            logger.error(f"❌ Market resolution failed: {msg.request_id}")
            logger.error(f"   Error: {e}")
            
            # Send error response
            response = MarketResolutionResponse(
                request_id=msg.request_id,
                market_id=msg.market_id,
                outcome=None,
                confidence=None,
                evidence=[],
                success=False,
                error=str(e)
            )
            
            await ctx.send(sender, response)

# Create protocol instance
market_resolver_protocol = MarketResolverProtocol()

# Register protocol with agent
resolver_agent.include(market_resolver_protocol)

# FastAPI integration for HTTP endpoints
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Market Resolver μAgent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HTTPMarketResolutionRequest(BaseModel):
    market_id: str = Field(..., description="Market ID to resolve")
    prompt: str = Field(..., description="Market prompt")
    reliable_sources: List[str] = Field(..., description="List of reliable sources")

@app.post("/resolve-market")
async def http_resolve_market(request: HTTPMarketResolutionRequest):
    """HTTP endpoint that EXACTLY mirrors current behavior"""
    import uuid
    
    request_id = str(uuid.uuid4())
    logger.info(f"🌐 HTTP resolution request received: {request_id}")
    
    try:
        # PRESERVE EXACTLY the existing resolve_market function
        resolution_result = await resolve_market(
            market_id=request.market_id,
            prompt=request.prompt,
            reliable_sources=request.reliable_sources
        )
        
        logger.info(f"✅ HTTP resolution completed: {request_id}")
        
        return {
            "request_id": request_id,
            "market_id": request.market_id,
            "outcome": resolution_result.get('outcome'),
            "confidence": resolution_result.get('confidence'),
            "evidence": resolution_result.get('evidence', []),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"❌ HTTP resolution failed: {request_id}")
        logger.error(f"   Error: {e}")
        
        raise HTTPException(
            status_code=500, 
            detail=f"Market resolution failed: {str(e)}"
        )

@app.get("/resolutions/{market_id}/outcome")
async def get_market_outcome(market_id: str):
    """Get market outcome - mirrors existing endpoint"""
    try:
        # This would typically query the database
        # For now, return a placeholder
        return {"outcome": "undefined"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Market not found")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "market_resolver",
        "address": resolver_agent.address
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Market Resolver μAgent",
        "version": "1.0.0",
        "endpoints": {
            "POST /resolve-market": "Resolve market outcome",
            "GET /resolutions/{market_id}/outcome": "Get market outcome",
            "GET /health": "Health check"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=RESOLVER_AGENT_PORT) 