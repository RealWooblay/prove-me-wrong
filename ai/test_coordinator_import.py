#!/usr/bin/env python3
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

print("Testing coordinator agent import...")

try:
    # Test basic imports
    print("1. Testing basic imports...")
    from agents.market_coordinator_agent import app, coordinator_agent
    print("✅ Basic imports successful")
    
    # Test database imports
    print("2. Testing database imports...")
    from database import get_db, init_db, Market, SessionLocal
    print("✅ Database imports successful")
    
    # Test generator imports
    print("3. Testing generator imports...")
    from generator.server import create_market_data, save_market_to_db, deploy_market, MarketValidation
    print("✅ Generator imports successful")
    
    # Test other agent imports
    print("4. Testing other agent imports...")
    from agents.market_generator_agent import generator_agent
    from agents.market_resolver_agent import resolver_agent
    print("✅ Other agent imports successful")
    
    print("🎉 All imports successful!")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 