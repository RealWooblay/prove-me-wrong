#!/usr/bin/env python3
"""
Test script to run the actual deployment function locally
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import the deployment function
from server import deploy_market

def test_actual_deployment():
    """Test the actual deployment function"""
    
    print("🚀 Testing actual deployment function...")
    
    # Test parameters
    market_id = "test-market-123"
    title = "Test Market"
    url = "https://prove-me-wrong-production.up.railway.app/resolver/resolutions/test-market-123/outcome"
    yes_probability = 0.45
    no_probability = 0.55
    
    print(f"Market ID: {market_id}")
    print(f"Title: {title}")
    print(f"URL: {url}")
    print(f"YES probability: {yes_probability}")
    print(f"NO probability: {no_probability}")
    
    try:
        # Call the actual deployment function
        result = deploy_market(
            market_id=market_id,
            title=title,
            url=url,
            yes_probability=yes_probability,
            no_probability=no_probability
        )
        
        if result:
            print("✅ Deployment successful!")
        else:
            print("❌ Deployment failed!")
            
        return result
        
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Actual Deployment Test")
    print("=" * 50)
    
    success = test_actual_deployment()
    
    if success:
        print("\n🎉 Deployment test passed!")
    else:
        print("\n❌ Deployment test failed!")
    
    print("\n" + "=" * 50) 