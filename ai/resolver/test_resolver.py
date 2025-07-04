#!/usr/bin/env python3
"""
Test script for the Market Resolver Agent
"""

import asyncio
import json
import requests
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8001"
GENERATOR_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("Health Check:")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_root():
    """Test the root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print("\nRoot Endpoint:")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Root endpoint failed: {e}")
        return False

def test_generator_connection():
    """Test connection to generator API"""
    try:
        response = requests.get(f"{GENERATOR_URL}/health")
        print("\nGenerator Connection:")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Generator markets: {data.get('stored_markets', 0)}")
            return True
        else:
            print("Failed to connect to generator")
            return False
    except Exception as e:
        print(f"Generator connection failed: {e}")
        return False

def test_list_resolutions():
    """Test listing resolutions"""
    try:
        response = requests.get(f"{BASE_URL}/resolutions")
        print("\nList Resolutions:")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total resolutions: {data.get('total', 0)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"List resolutions failed: {e}")
        return False

def test_resolve_all():
    """Test resolving all markets"""
    try:
        response = requests.post(f"{BASE_URL}/resolve-all")
        print("\nResolve All Markets:")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Processed: {data.get('processed', 0)} markets")
            results = data.get('results', [])
            for result in results[:5]:  # Show first 5 results
                print(f"  - {result.get('market_id', 'unknown')}: {result.get('outcome', 'unknown')}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Resolve all failed: {e}")
        return False

def test_resolve_specific_market():
    """Test resolving a specific market"""
    # First, get a market from the generator
    try:
        response = requests.get(f"{GENERATOR_URL}/markets")
        if response.status_code == 200:
            data = response.json()
            markets = data.get('markets', [])
            if markets:
                market_id = markets[0]['id']
                print(f"\nTesting resolution for market: {market_id}")
                
                # Test resolving this specific market
                resolve_response = requests.post(
                    f"{BASE_URL}/resolve",
                    json={"market_id": market_id}
                )
                print(f"Resolve Status: {resolve_response.status_code}")
                if resolve_response.status_code == 200:
                    result = resolve_response.json()
                    if result.get('success'):
                        resolution = result.get('resolution', {})
                        print(f"Outcome: {resolution.get('outcome', 'unknown')}")
                        print(f"Confidence: {resolution.get('confidence', 0)}")
                        print(f"Auto-expired: {resolution.get('auto_expired', False)}")
                    else:
                        print(f"Resolution failed: {result.get('error')}")
                else:
                    print(f"Error: {resolve_response.text}")
                return True
            else:
                print("No markets found to test")
                return False
        else:
            print("Failed to get markets from generator")
            return False
    except Exception as e:
        print(f"Test resolve specific market failed: {e}")
        return False

def test_auto_expiration():
    """Test auto-expiration functionality"""
    print("\nAuto-Expiration Test:")
    print("This would test markets that have passed their close date")
    print("In a real scenario, you would create a market with a past date")
    print("and verify it gets auto-expired")
    return True

def main():
    """Run all tests"""
    print("=== Market Resolver Agent Tests ===\n")
    
    # Test basic endpoints
    health_ok = test_health()
    root_ok = test_root()
    
    if not health_ok or not root_ok:
        print("\nBasic endpoint tests failed. Make sure the resolver is running.")
        return
    
    # Test generator connection
    generator_ok = test_generator_connection()
    if not generator_ok:
        print("\nGenerator connection failed. Make sure the generator is running.")
        return
    
    # Test resolver functionality
    test_list_resolutions()
    test_resolve_all()
    test_resolve_specific_market()
    test_auto_expiration()
    
    print("\n=== Tests Complete ===")
    print("\nTo test the full workflow:")
    print("1. Create a market using the generator: POST /generate")
    print("2. Wait for the resolver to check it automatically (every hour)")
    print("3. Or manually trigger resolution: POST /resolve-all")
    print("4. Check results: GET /resolutions")

if __name__ == "__main__":
    main() 