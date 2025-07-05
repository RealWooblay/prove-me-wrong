#!/usr/bin/env python3
"""
Test script for Prove Me Wrong AI deployment
This script tests all the key functionality to ensure the deployment works correctly
"""

import requests
import json
import time
import sys
import os

# Configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
ASI_API_KEY = os.getenv("ASI_API_KEY")

def test_health_checks():
    """Test health endpoints"""
    print("🔍 Testing health checks...")
    
    # Test main health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Main health check: {data}")
        else:
            print(f"❌ Main health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Main health check error: {e}")
        return False
    
    # Test generator health
    try:
        response = requests.get(f"{BASE_URL}/generator/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Generator health: {data}")
        else:
            print(f"❌ Generator health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Generator health error: {e}")
        return False
    
    # Test resolver health
    try:
        response = requests.get(f"{BASE_URL}/resolver/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resolver health: {data}")
        else:
            print(f"❌ Resolver health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Resolver health error: {e}")
        return False
    
    return True

def test_market_generation():
    """Test market generation"""
    print("\n🔍 Testing market generation...")
    
    if not ASI_API_KEY:
        print("⚠️  ASI_API_KEY not set, skipping market generation test")
        return True
    
    test_prompt = "Will Bitcoin reach $100,000 by the end of 2025?"
    
    try:
        response = requests.post(
            f"{BASE_URL}/generator/generate",
            json={"prompt": test_prompt}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                market = data.get("market")
                print(f"✅ Market generated: {market['id']}")
                print(f"   Title: {market['title']}")
                print(f"   Status: {market['status']}")
                return market['id']
            else:
                print(f"❌ Market generation failed: {data.get('error')}")
                return None
        else:
            print(f"❌ Market generation request failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Market generation error: {e}")
        return None

def test_market_listing():
    """Test market listing"""
    print("\n🔍 Testing market listing...")
    
    try:
        response = requests.get(f"{BASE_URL}/generator/markets")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Markets listed: {data.get('total', 0)} markets found")
            return True
        else:
            print(f"❌ Market listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Market listing error: {e}")
        return False

def test_market_resolution(market_id):
    """Test market resolution"""
    print(f"\n🔍 Testing market resolution for {market_id}...")
    
    if not ASI_API_KEY:
        print("⚠️  ASI_API_KEY not set, skipping market resolution test")
        return True
    
    try:
        response = requests.post(
            f"{BASE_URL}/resolver/resolve",
            json={"market_id": market_id}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                resolution = data.get("resolution")
                print(f"✅ Market resolved: {resolution['outcome']}")
                print(f"   Confidence: {resolution['confidence']}")
                return True
            else:
                print(f"❌ Market resolution failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Market resolution request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Market resolution error: {e}")
        return False

def test_resolution_listing():
    """Test resolution listing"""
    print("\n🔍 Testing resolution listing...")
    
    try:
        response = requests.get(f"{BASE_URL}/resolver/resolutions")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resolutions listed: {data.get('total', 0)} resolutions found")
            return True
        else:
            print(f"❌ Resolution listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Resolution listing error: {e}")
        return False

def test_api_documentation():
    """Test API documentation"""
    print("\n🔍 Testing API documentation...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API documentation: {data.get('message', 'API info')}")
            return True
        else:
            print(f"❌ API documentation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API documentation error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Prove Me Wrong AI deployment tests...")
    print(f"📍 Testing against: {BASE_URL}")
    print(f"🔑 ASI API Key: {'✅ Set' if ASI_API_KEY else '❌ Not set'}")
    
    tests = [
        ("Health Checks", test_health_checks),
        ("API Documentation", test_api_documentation),
        ("Market Listing", test_market_listing),
        ("Market Generation", test_market_generation),
        ("Resolution Listing", test_resolution_listing),
    ]
    
    results = []
    market_id = None
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if test_name == "Market Generation":
                market_id = test_func()
                results.append((test_name, market_id is not None))
            else:
                success = test_func()
                results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Test resolution if we have a market
    if market_id:
        print(f"\n{'='*50}")
        print(f"Running: Market Resolution")
        print('='*50)
        success = test_market_resolution(market_id)
        results.append(("Market Resolution", success))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 