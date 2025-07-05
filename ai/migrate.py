#!/usr/bin/env python3
"""
Database migration script for Prove Me Wrong AI services
This script creates the necessary database tables
"""

import os
import sys
from database import init_db, engine, Base
from sqlalchemy import text

def main():
    """Initialize the database tables"""
    print("🚀 Initializing database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection test successful!")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 