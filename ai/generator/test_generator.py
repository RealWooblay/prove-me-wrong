#!/usr/bin/env python3
"""
Test script for the Market Generator Agent
"""

import asyncio
import json
import requests
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"

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

def test_market_generation():
    """Test market generation with a sample prompt"""
    test_prompts = [
        "Tesla stock price will be above $250 on December 31, 2024",
        "Bitcoin will reach $100,000 by the end of 2024",
        "The US will have a recession in 2024"
    ]
    
    for prompt in test_prompts:
        print(f"\nTesting market generation for: {prompt}")
        
        try:
            payload = {
                "prompt": prompt,
                "max_search_results": 3
            }
            
            response = requests.post(
                f"{BASE_URL}/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success: {result.get('success')}")
                
                if result.get('success') and result.get('market'):
                    market = result['market']
                    print(f"Market Title: {market['title']}")
                    print(f"Initial Probability: {market['initialProb']}")
                    print(f"Validation Confidence: {market['validation']['confidence']}")
                    print(f"Valid Market: {market['validation']['is_valid']}")
                else:
                    print(f"Error: {result.get('error')}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Request failed: {e}")

def main():
    """Run all tests"""
    print("=== Market Generator Agent Tests ===\n")
    
    # Test basic endpoints
    health_ok = test_health()
    root_ok = test_root()
    
    if not health_ok or not root_ok:
        print("\nBasic endpoint tests failed. Make sure the server is running.")
        return
    
    # Test market generation
    print("\n=== Testing Market Generation ===")
    test_market_generation()
    
    print("\n=== Tests Complete ===")

if __name__ == "__main__":
    main() 