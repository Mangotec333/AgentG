#!/usr/bin/env python3
"""
Run database schema in Supabase.
"""
import asyncio
import asyncpg
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load .env file if it exists
env_file = project_root / ".env"
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

async def run_schema():
    """Run schema.sql in the database."""
    # Read DATABASE_URL directly from environment or .env
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("❌ DATABASE_URL not configured in environment or .env file")
        return False
    
    print(f"🔌 Connecting to: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    
    # Read schema file
    schema_file = project_root / "shared" / "schema.sql"
    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        return False
    
    with open(schema_file, 'r') as f:
        schema_sql = f.read()
    
    try:
        # Connect to database
        conn = await asyncpg.connect(db_url)
        print("✅ Connected successfully!")
        
        # Split schema into individual statements
        # PostgreSQL doesn't support multiple statements in one execute()
        statements = []
        current_statement = []
        
        for line in schema_sql.split('\n'):
            # Skip comments and empty lines
            stripped = line.strip()
            if not stripped or stripped.startswith('--'):
                continue
            
            current_statement.append(line)
            
            # Check if this line ends a statement
            if stripped.endswith(';'):
                statement = '\n'.join(current_statement)
                if statement.strip():
                    statements.append(statement)
                current_statement = []
        
        # Execute each statement
        print(f"📄 Running {len(statements)} SQL statements...")
        for i, statement in enumerate(statements, 1):
            try:
                await conn.execute(statement)
                print(f"   ✅ Statement {i}/{len(statements)} executed")
            except Exception as e:
                # Some statements might fail if they already exist (CREATE EXTENSION, etc.)
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print(f"   ⚠️  Statement {i}/{len(statements)} skipped (already exists)")
                else:
                    print(f"   ❌ Statement {i}/{len(statements)} failed: {e}")
                    # Continue with other statements
        
        # Verify tables were created
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print(f"\n📋 Found {len(tables)} tables:")
        for table in tables:
            count = await conn.fetchval(f'SELECT COUNT(*) FROM "{table["table_name"]}"')
            print(f"   - {table['table_name']}: {count} rows")
        
        # Check for pgvector extension
        extensions = await conn.fetch("""
            SELECT extname 
            FROM pg_extension 
            WHERE extname = 'vector'
        """)
        
        if extensions:
            print("\n✅ pgvector extension is enabled")
        else:
            print("\n⚠️  pgvector extension not found (may need to enable manually)")
        
        await conn.close()
        print("\n✅ Schema setup complete!")
        return True
        
    except asyncpg.exceptions.InvalidPasswordError:
        print("❌ Invalid password")
        return False
    except asyncpg.exceptions.InvalidCatalogNameError:
        print("❌ Database does not exist")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_schema())
    sys.exit(0 if success else 1)

