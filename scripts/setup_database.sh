#!/bin/bash
# Database setup script for AgentG

set -e

echo "🗄️  AgentG Database Setup"
echo "========================"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL not found. Please install PostgreSQL first."
    echo "   macOS: brew install postgresql"
    echo "   Ubuntu: sudo apt-get install postgresql"
    exit 1
fi

# Get database name from env or use default
DB_NAME="${DB_NAME:-shield_db}"
DB_USER="${DB_USER:-$(whoami)}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

echo "📋 Configuration:"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo "   Host: $DB_HOST"
echo "   Port: $DB_PORT"
echo ""

# Check if database exists
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "⚠️  Database '$DB_NAME' already exists."
    read -p "   Drop and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Dropping existing database..."
        dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" || true
    else
        echo "✅ Using existing database."
    fi
fi

# Create database if it doesn't exist
if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "📦 Creating database '$DB_NAME'..."
    createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME"
    echo "✅ Database created."
else
    echo "✅ Database exists."
fi

# Run schema
echo "📄 Running schema migrations..."
SCHEMA_FILE="$(dirname "$0")/../shared/schema.sql"
if [ -f "$SCHEMA_FILE" ]; then
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SCHEMA_FILE"
    echo "✅ Schema applied."
else
    echo "❌ Schema file not found: $SCHEMA_FILE"
    exit 1
fi

# Test connection
echo "🧪 Testing database connection..."
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ Database connection successful!"
    
    # Show tables
    echo ""
    echo "📊 Created tables:"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\dt" | grep -v "List of relations" | grep -v "----" | grep -v "^$" || true
    
    # Generate DATABASE_URL
    echo ""
    echo "✅ Database setup complete!"
    echo ""
    echo "📝 Add this to your .env file:"
    echo "   DATABASE_URL=postgresql://$DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
    if [ -n "$PGPASSWORD" ]; then
        echo "   DATABASE_URL=postgresql://$DB_USER:$PGPASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
    fi
else
    echo "❌ Database connection failed!"
    exit 1
fi



