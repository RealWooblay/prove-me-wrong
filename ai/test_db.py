#!/usr/bin/env python3
"""
Simple database test for Prove Me Wrong AI
"""

import os
import sys
from database import init_db, engine, Base, Market, Resolution, SessionLocal
from sqlalchemy import text

def test_database():
    """Test database connection and table creation"""
    print("🔍 Testing database setup...")
    
    try:
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Test table creation
        init_db()
        print("✅ Database tables created successfully")
        
        # Test session creation
        db = SessionLocal()
        try:
            # Test market count
            market_count = db.query(Market).count()
            print(f"✅ Market table accessible: {market_count} markets")
            
            # Test resolution count
            resolution_count = db.query(Resolution).count()
            print(f"✅ Resolution table accessible: {resolution_count} resolutions")
            
        finally:
            db.close()
        
        print("🎉 All database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1) 