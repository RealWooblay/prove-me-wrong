#!/usr/bin/env python3
"""
Test script to verify μAgent communication and deployment
"""

import asyncio
import httpx
import time
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_agent_communication():
    """Test that agents are communicating with each other"""
    logger.info("🧪 Testing μAgent Communication...")
    
    async with httpx.AsyncClient() as client:
        # Test 1: Check if all agents are running
        logger.info("📡 Checking agent health...")
        
        agents = [
            ("Generator Agent", "http://localhost:8000/health"),
            ("Resolver Agent", "http://localhost:8001/health"),
            ("Coordinator Agent", "http://localhost:8002/health"),
            ("Generator Server", "http://localhost:8003/health"),
            ("Resolver Server", "http://localhost:8004/health"),
            ("Proxy Server", "http://localhost:8005/health"),
        ]
        
        for name, url in agents:
            try:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ {name}: Healthy")
                else:
                    logger.error(f"❌ {name}: Unhealthy (Status: {response.status_code})")
            except Exception as e:
                logger.error(f"❌ {name}: Error - {e}")
        
        # Test 2: Test market creation flow through coordinator
        logger.info("🎯 Testing market creation flow...")
        
        try:
            # Create a market through the coordinator
            market_data = {
                "prompt": "Will Bitcoin reach $100k by end of 2026?",
                "market_id": "test-btc-2026",
                "request_id": "test-request-123"
            }
            
            response = await client.post(
                "http://localhost:8002/create-market",
                json=market_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Market creation successful: {result}")
                
                # Check if market was created in database
                markets_response = await client.get("http://localhost:8003/markets")
                if markets_response.status_code == 200:
                    markets = markets_response.json()
                    logger.info(f"📊 Markets in database: {markets.get('total', 0)}")
                    
                    # Look for our test market
                    for market in markets.get('markets', []):
                        if market.get('id') == 'test-btc-2026':
                            logger.info(f"✅ Test market found in database: {market.get('title')}")
                            break
                    else:
                        logger.warning("⚠️ Test market not found in database")
                else:
                    logger.error(f"❌ Failed to get markets: {markets_response.status_code}")
            else:
                logger.error(f"❌ Market creation failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Market creation test failed: {e}")
        
        # Test 3: Test direct agent communication via uagents protocol
        logger.info("🔗 Testing direct μAgent communication...")
        
        try:
            # Test generator agent directly
            generator_data = {
                "prompt": "Will Ethereum reach $10k by end of 2026?",
                "request_id": "test-gen-456"
            }
            
            response = await client.post(
                "http://localhost:8000/analyze-market",
                json=generator_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Generator agent response: {result}")
            else:
                logger.error(f"❌ Generator agent failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Direct agent communication test failed: {e}")
        
        # Test 4: Test resolver agent
        logger.info("🔍 Testing resolver agent...")
        
        try:
            resolver_data = {
                "market_id": "test-btc-2026",
                "prompt": "Will Bitcoin reach $100k by end of 2026?",
                "reliable_sources": ["Reuters", "Bloomberg", "CoinDesk"],
                "request_id": "test-res-789"
            }
            
            response = await client.post(
                "http://localhost:8001/resolve-market",
                json=resolver_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Resolver agent response: {result}")
            else:
                logger.error(f"❌ Resolver agent failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Resolver agent test failed: {e}")

async def test_railway_deployment():
    """Test Railway deployment if RAILWAY_URL is available"""
    import os
    
    railway_url = os.getenv("RAILWAY_URL")
    if not railway_url:
        logger.info("⚠️ RAILWAY_URL not set, skipping Railway deployment test")
        return
    
    logger.info(f"🌐 Testing Railway deployment: {railway_url}")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test coordinator agent on Railway
            response = await client.get(f"{railway_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ Railway deployment healthy: {response.json()}")
            else:
                logger.error(f"❌ Railway deployment unhealthy: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Railway deployment test failed: {e}")

async def main():
    """Main test function"""
    logger.info("🎯 Starting μAgent Communication Tests...")
    
    # Test local deployment
    await test_agent_communication()
    
    # Test Railway deployment
    await test_railway_deployment()
    
    logger.info("✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 