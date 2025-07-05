from uagents import Agent, Context, Protocol
from pydantic import BaseModel, Field
import requests
import json
import re
from datetime import datetime
from typing import List, Optional, Dict
import logging
import sys
import os

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from generator.server import analyze_market_prompt, MarketValidation
except ImportError:
    # For Railway deployment, try direct import
    from generator.server import analyze_market_prompt, MarketValidation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent configuration
GENERATOR_AGENT_SEED = "market_generator_seed_12345"
GENERATOR_AGENT_PORT = 8000

# Create the agent
generator_agent = Agent(
    name="market_generator",
    port=GENERATOR_AGENT_PORT,
    seed=GENERATOR_AGENT_SEED,
    endpoint=["http://0.0.0.0:8000/submit"],
)

# Fund the agent (commented out for now)
# fund_agent_if_low(generator_agent.wallet.address())

# Message models
class MarketAnalysisRequest(BaseModel):
    prompt: str = Field(..., description="The market prompt to analyze")
    request_id: str = Field(..., description="Unique request identifier")

class MarketAnalysisResponse(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    validation: Dict = Field(..., description="Market validation result")
    success: bool = Field(..., description="Whether analysis was successful")
    error: Optional[str] = Field(None, description="Error message if failed")

# Protocol for market analysis
class MarketGeneratorProtocol(Protocol):
    def __init__(self):
        super().__init__()
        
    @generator_agent.on_message(model=MarketAnalysisRequest)
    async def handle_market_analysis(self, ctx: Context, sender: str, msg: MarketAnalysisRequest):
        """Handle market analysis requests - PRESERVES ALL EXISTING LOGIC"""
        logger.info(f"🔍 Received market analysis request: {msg.request_id}")
        logger.info(f"   Prompt: {msg.prompt}")
        
        try:
            # PRESERVE EXACTLY the existing analyze_market_prompt function
            validation = await analyze_market_prompt(msg.prompt)
            
            logger.info(f"✅ Market analysis completed: {msg.request_id}")
            logger.info(f"   Valid: {validation.is_valid}")
            logger.info(f"   Confidence: {validation.confidence}")
            
            # Send response
            response = MarketAnalysisResponse(
                request_id=msg.request_id,
                validation=validation.dict(),
                success=True
            )
            
            await ctx.send(sender, response)
            
        except Exception as e:
            logger.error(f"❌ Market analysis failed: {msg.request_id}")
            logger.error(f"   Error: {e}")
            
            # Send error response
            error_validation = MarketValidation(
                is_valid=False,
                confidence=0.0,
                reasoning=f"Error during analysis: {str(e)}",
                yes_probability=0.5,
                no_probability=0.5,
                reliable_sources=[],
                resolution_date="",
                auto_expire=False
            )
            response = MarketAnalysisResponse(
                request_id=msg.request_id,
                validation=error_validation.dict(),
                success=False,
                error=str(e)
            )
            
            await ctx.send(sender, response)

# Create protocol instance
market_generator_protocol = MarketGeneratorProtocol()

# Register protocol with agent
generator_agent.include(market_generator_protocol)

# FastAPI integration for HTTP endpoints
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Market Generator μAgent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HTTPMarketAnalysisRequest(BaseModel):
    prompt: str = Field(..., description="The market prompt to analyze")

@app.post("/analyze-market")
async def http_analyze_market(request: HTTPMarketAnalysisRequest):
    """HTTP endpoint that EXACTLY mirrors current behavior"""
    import uuid
    
    request_id = str(uuid.uuid4())
    logger.info(f"🌐 HTTP request received: {request_id}")
    
    try:
        # PRESERVE EXACTLY the existing analyze_market_prompt function
        validation = await analyze_market_prompt(request.prompt)
        
        logger.info(f"✅ HTTP analysis completed: {request_id}")
        
        return {
            "request_id": request_id,
            "validation": validation.dict(),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"❌ HTTP analysis failed: {request_id}")
        logger.error(f"   Error: {e}")
        
        raise HTTPException(
            status_code=500, 
            detail=f"Market analysis failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "market_generator",
        "address": generator_agent.address
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Market Generator μAgent",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze-market": "Analyze market prompt",
            "GET /health": "Health check"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=GENERATOR_AGENT_PORT) 