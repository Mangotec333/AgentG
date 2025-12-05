#!/usr/bin/env python3
"""
Test database connection for AgentG.
"""
import asyncio
import asyncpg
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.config import BackendConfig


async def test_connection():
    """Test database connection."""
    config = BackendConfig()
    db_url = config.database_url
    
    if not db_url:
        print("❌ DATABASE_URL not configured in environment or .env file")
        print("   Set DATABASE_URL=postgresql://user:pass@host:port/dbname")
        return False
    
    print(f"🔌 Testing connection to: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    
    try:
        conn = await asyncpg.connect(db_url)
        print("✅ Connected successfully!")
        
        # Test query
        result = await conn.fetchval("SELECT version()")
        print(f"📊 PostgreSQL version: {result.split(',')[0]}")
        
        # Check tables
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        if tables:
            print(f"\n📋 Found {len(tables)} tables:")
            for table in tables:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table['table_name']}")
                print(f"   - {table['table_name']}: {count} rows")
        else:
            print("⚠️  No tables found. Run schema.sql first.")
        
        await conn.close()
        print("\n✅ Database connection test passed!")
        return True
        
    except asyncpg.exceptions.InvalidPasswordError:
        print("❌ Invalid password")
        return False
    except asyncpg.exceptions.InvalidCatalogNameError:
        print("❌ Database does not exist")
        print("   Run: scripts/setup_database.sh")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)



