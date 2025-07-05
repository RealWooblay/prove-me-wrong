#!/usr/bin/env python3
"""
Simple deployment test script
"""

import requests
import time
import os

def test_deployment():
    """Test the deployment"""
    print("🧪 Testing μAgent deployment...")
    
    # Get Railway URL from environment or use localhost
    base_url = os.getenv("RAILWAY_URL", "http://localhost")
    
    # Test endpoints
    endpoints = [
        ("Coordinator Agent", f"{base_url}/health"),
        ("Generator Agent", f"{base_url}:8000/health"),
        ("Resolver Agent", f"{base_url}:8001/health"),
        ("Generator Server", f"{base_url}:8003/health"),
        ("Resolver Server", f"{base_url}:8004/health"),
        ("Proxy Server", f"{base_url}:8005/health"),
    ]
    
    for name, url in endpoints:
        try:
            print(f"Testing {name}...")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: Healthy")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ {name}: Unhealthy (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    print("\n🎯 Testing market creation...")
    try:
        # Test market creation through coordinator
        market_data = {
            "prompt": "Will Bitcoin reach $100k by end of 2026?",
            "market_id": "test-btc-2026",
            "request_id": "test-request-123"
        }
        
        response = requests.post(
            f"{base_url}/create-market",
            json=market_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Market creation successful: {result}")
        else:
            print(f"❌ Market creation failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Market creation test failed: {e}")
    
    print("\n✅ Deployment test completed!")

if __name__ == "__main__":
    test_deployment() 