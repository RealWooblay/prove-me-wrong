#!/usr/bin/env python3
"""
Test script for blockchain integration in the market generator
"""

import os
import sys
import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health endpoint to check blockchain configuration"""
    print("🔍 Testing health endpoint...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   ASI API configured: {data.get('asi_api_configured', False)}")
            print(f"   Blockchain configured: {data.get('blockchain_configured', False)}")
            print(f"   Blockchain connected: {data.get('blockchain_connected', False)}")
            print(f"   Stored markets: {data.get('stored_markets', 0)}")
            return data
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return None

def test_market_generation():
    """Test market generation with blockchain deployment"""
    print("\n🚀 Testing market generation...")
    
    test_prompt = "Will Bitcoin reach $100,000 by the end of 2025?"
    market_id = f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    payload = {
        "prompt": test_prompt,
        "market_id": market_id
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Market generation successful")
                print(f"   Market ID: {data['market']['id']}")
                print(f"   Title: {data['market']['title']}")
                print(f"   Valid: {data['market']['validation']['is_valid']}")
                print(f"   Blockchain Deployed: {data['market'].get('blockchain_deployed', False)}")
                return data['market']
            else:
                print(f"❌ Market generation failed: {data.get('error')}")
                return None
        else:
            print(f"❌ Market generation failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Market generation error: {e}")
        return None

def test_blockchain_deployment_status(market_data):
    """Test blockchain deployment status from market data"""
    print(f"\n⛓️ Testing blockchain deployment status for market: {market_data.get('id')}")
    
    blockchain_deployed = market_data.get('blockchain_deployed', False)
    
    if blockchain_deployed:
        print("✅ Blockchain deployment successful")
        return True
    else:
        print("⚠️ Blockchain deployment failed or not configured")
        return False

def test_market_retrieval(market_id):
    """Test retrieving a specific market"""
    print(f"\n📊 Testing market retrieval for: {market_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/markets/{market_id}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Market retrieval successful")
            print(f"   Title: {data.get('title')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Created: {data.get('created_at')}")
            return True
        else:
            print(f"❌ Market retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Market retrieval error: {e}")
        return False

def main():
    """Run all blockchain integration tests"""
    print("🧪 ProveMeWrong Blockchain Integration Test")
    print("=" * 50)
    
    # Test 1: Health endpoint
    health_data = test_health_endpoint()
    if not health_data:
        print("❌ Health check failed, stopping tests")
        return
    
    # Test 2: Market generation
    market_data = test_market_generation()
    if not market_data:
        print("❌ Market generation failed, stopping tests")
        return
    
    # Test 3: Market retrieval
    test_market_retrieval(market_data['id'])
    
    # Test 4: Blockchain deployment status (from market generation response)
    test_blockchain_deployment_status(market_data)
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 