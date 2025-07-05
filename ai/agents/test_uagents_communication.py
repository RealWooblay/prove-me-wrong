#!/usr/bin/env python3
"""
Test script to verify μAgent communication via uagents protocols
"""

import asyncio
import uuid
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the agents
from market_generator_agent import generator_agent, MarketAnalysisRequest, MarketAnalysisResponse
from market_resolver_agent import resolver_agent, MarketResolutionRequest, MarketResolutionResponse
from market_coordinator_agent import coordinator_agent, MarketCreationRequest, MarketCreationResponse

# Create a test agent to send messages
from uagents import Agent, Context
from pydantic import BaseModel

class TestResponse(BaseModel):
    """Generic response model for testing"""
    sender: str
    message_type: str
    data: Dict[str, Any]

test_agent = Agent(
    name="test_agent",
    port=8003,
    seed="test_agent_seed_12345",
    endpoint=["http://127.0.0.1:8003/submit"],
)

# Track responses
responses = {}

@test_agent.on_event("startup")
async def startup_handler(ctx: Context):
    """Startup handler that sends test messages to all agents"""
    logger.info(f"🚀 Test agent started: {ctx.agent.name} at {ctx.agent.address}")
    
    # Wait a bit for other agents to be ready
    await asyncio.sleep(2)
    
    # Test generator agent
    await test_generator_agent(ctx)
    await asyncio.sleep(1)
    
    # Test resolver agent
    await test_resolver_agent(ctx)
    await asyncio.sleep(1)
    
    # Test coordinator agent
    await test_coordinator_agent(ctx)

async def test_generator_agent(ctx: Context):
    """Test generator agent via uagents protocol"""
    logger.info("🧪 Testing Generator Agent via μAgent protocol...")
    
    request_id = str(uuid.uuid4())
    request = MarketAnalysisRequest(
        prompt="Will Bitcoin reach $100k by end of 2026?",
        request_id=request_id
    )
    
    # Send request via uagents protocol using the correct API
    await ctx.send(generator_agent.address, request)
    
    logger.info(f"📤 Sent request to generator agent: {request_id}")
    return request_id

async def test_resolver_agent(ctx: Context):
    """Test resolver agent via uagents protocol"""
    logger.info("🧪 Testing Resolver Agent via μAgent protocol...")
    
    request_id = str(uuid.uuid4())
    request = MarketResolutionRequest(
        market_id="test-market-123",
        prompt="Will Bitcoin reach $100k by end of 2026?",
        reliable_sources=["Reuters", "Bloomberg"],
        request_id=request_id
    )
    
    # Send request via uagents protocol using the correct API
    await ctx.send(resolver_agent.address, request)
    
    logger.info(f"📤 Sent request to resolver agent: {request_id}")
    return request_id

async def test_coordinator_agent(ctx: Context):
    """Test coordinator agent via uagents protocol"""
    logger.info("🧪 Testing Coordinator Agent via μAgent protocol...")
    
    request_id = str(uuid.uuid4())
    request = MarketCreationRequest(
        prompt="Will Ethereum reach $10k by end of 2026?",
        market_id="test-eth-market",
        request_id=request_id
    )
    
    # Send request via uagents protocol (this should trigger the full flow)
    await ctx.send(coordinator_agent.address, request)
    
    logger.info(f"📤 Sent request to coordinator agent: {request_id}")
    return request_id

# Message handlers to receive responses
@test_agent.on_message(model=MarketAnalysisResponse)
async def handle_generator_response(ctx: Context, sender: str, msg: MarketAnalysisResponse):
    """Handle responses from generator agent"""
    logger.info(f"📥 Received generator response from {sender}")
    logger.info(f"   Request ID: {msg.request_id}")
    logger.info(f"   Success: {msg.success}")
    responses[sender] = msg.dict()

@test_agent.on_message(model=MarketResolutionResponse)
async def handle_resolver_response(ctx: Context, sender: str, msg: MarketResolutionResponse):
    """Handle responses from resolver agent"""
    logger.info(f"📥 Received resolver response from {sender}")
    logger.info(f"   Request ID: {msg.request_id}")
    logger.info(f"   Success: {msg.success}")
    responses[sender] = msg.dict()

@test_agent.on_message(model=MarketCreationResponse)
async def handle_coordinator_response(ctx: Context, sender: str, msg: MarketCreationResponse):
    """Handle responses from coordinator agent"""
    logger.info(f"📥 Received coordinator response from {sender}")
    logger.info(f"   Request ID: {msg.request_id}")
    logger.info(f"   Success: {msg.success}")
    responses[sender] = msg.dict()

async def test_http_endpoints():
    """Test HTTP endpoints (should work alongside uagents)"""
    logger.info("🧪 Testing HTTP endpoints...")
    
    import httpx
    
    async with httpx.AsyncClient() as client:
        # Test generator agent
        response = await client.post(
            "http://localhost:8000/analyze-market",
            json={"prompt": "Will Bitcoin reach $100k by end of 2026?"}
        )
        logger.info(f"✅ Generator HTTP: {response.status_code}")
        
        # Test resolver agent
        response = await client.post(
            "http://localhost:8001/resolve-market",
            json={
                "market_id": "test-market-123",
                "prompt": "Will Bitcoin reach $100k by end of 2026?",
                "reliable_sources": ["Reuters", "Bloomberg"]
            }
        )
        logger.info(f"✅ Resolver HTTP: {response.status_code}")
        
        # Test coordinator agent
        response = await client.post(
            "http://localhost:8002/create-market",
            json={"prompt": "Will Ethereum reach $10k by end of 2026?"}
        )
        logger.info(f"✅ Coordinator HTTP: {response.status_code}")

async def main():
    """Main test function"""
    logger.info("🎯 Starting μAgent Communication Tests...")
    
    # Start the test agent
    logger.info("🚀 Starting test agent...")
    
    # Run the test agent
    test_agent.run()
    
    # Wait for responses
    await asyncio.sleep(10)
    
    # Test HTTP endpoints
    await test_http_endpoints()
    
    logger.info("✅ All tests completed!")
    logger.info(f"📊 Responses received: {len(responses)}")

if __name__ == "__main__":
    test_agent.run() 