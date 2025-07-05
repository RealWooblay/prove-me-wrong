#!/usr/bin/env python3
"""
Example usage of the ProveMeWrong blockchain integration
"""

import requests
import json
import os
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

def generate_and_deploy_market(prompt: str, market_id: str | None = None):
    """
    Generate a market and optionally deploy it to the blockchain
    
    Args:
        prompt: The market prompt to analyze
        market_id: Optional custom market ID (required for blockchain deployment)
    """
    
    print(f"🎯 Generating market: {prompt}")
    
    # Prepare request payload
    payload = {
        "prompt": prompt,
        "market_id": market_id
    }
    
    # Generate market
    response = requests.post(
        f"{API_BASE_URL}/generate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ Market generation failed: {response.status_code}")
        return None
    
    data = response.json()
    
    if not data.get("success"):
        print(f"❌ Market validation failed: {data.get('error')}")
        return None
    
    market = data["market"]
    print(f"✅ Market generated successfully!")
    print(f"   ID: {market['id']}")
    print(f"   Title: {market['title']}")
    print(f"   Valid: {market['validation']['is_valid']}")
    print(f"   Yes Probability: {market['validation']['yes_probability']:.2%}")
    print(f"   No Probability: {market['validation']['no_probability']:.2%}")
    print(f"   Close Date: {market['close_time_iso']}")
    
    return market

def check_blockchain_deployment_status(market_data):
    """Check if market was deployed to blockchain"""
    
    if market_data.get("blockchain_deployed"):
        print(f"✅ Market deployed to blockchain!")
        return True
    else:
        print(f"⚠️ Market not deployed to blockchain (check configuration)")
        return False

def check_blockchain_status():
    """Check if blockchain is properly configured"""
    
    response = requests.get(f"{API_BASE_URL}/health")
    
    if response.status_code != 200:
        print("❌ Health check failed")
        return False
    
    data = response.json()
    
    print("🔍 Blockchain Configuration Status:")
    print(f"   Blockchain configured: {data.get('blockchain_configured', False)}")
    print(f"   Blockchain connected: {data.get('blockchain_connected', False)}")
    
    return data.get('blockchain_configured', False)

def main():
    """Example usage of the blockchain integration"""
    
    print("🚀 ProveMeWrong Blockchain Integration Example")
    print("=" * 50)
    
    # Check blockchain status
    blockchain_configured = check_blockchain_status()
    
    if not blockchain_configured:
        print("\n⚠️ Blockchain not configured!")
        print("   Set the following environment variables:")
        print("   - RPC_URL: Your Ethereum RPC URL")
        print("   - PMW_ADDRESS: Deployed ProveMeWrong contract address")
        print("   - ADMIN_PRIVATE_KEY: Admin wallet private key")
        print("   - CHAIN_ID: Chain ID (e.g., 11155111 for Sepolia)")
        print("\n   Or run: ./deploy_blockchain.sh")
        return
    
    # Example 1: Generate market (blockchain deployment happens automatically)
    print("\n📊 Example 1: Generate market with automatic blockchain deployment")
    market1 = generate_and_deploy_market(
        "Will the US Federal Reserve raise interest rates in Q1 2025?"
    )
    
    if market1:
        check_blockchain_deployment_status(market1)
    
    # Example 2: Generate market with custom ID
    print("\n⛓️ Example 2: Generate market with custom ID")
    market_id = f"example-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    market2 = generate_and_deploy_market(
        "Will Bitcoin reach $150,000 by the end of 2025?",
        market_id=market_id
    )
    
    if market2:
        check_blockchain_deployment_status(market2)
    
    print("\n✅ Example completed!")
    print("\n📝 Next steps:")
    print("   1. Check your blockchain explorer for deployed markets")
    print("   2. Use the ProveMeWrong frontend to interact with markets")
    print("   3. Monitor market activity and trading volume")

if __name__ == "__main__":
    main() 