# 🚀 Supabase Setup Guide for AgentG

This guide will help you set up Supabase (PostgreSQL with pgvector) for AgentG.

## Step 1: Create Supabase Account & Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up for a free account (or sign in)
3. Click **"New Project"**
4. Fill in:
   - **Name**: `agentg` (or your preferred name)
   - **Database Password**: Choose a strong password (save it!)
   - **Region**: Choose closest to you
   - **Pricing Plan**: Free tier is fine to start
5. Click **"Create new project"**
6. Wait 2-3 minutes for project to be created

## Step 2: Get Connection String

1. In your Supabase project dashboard, go to **Settings** → **Database**
2. Scroll down to **Connection string** section
3. Select **"URI"** tab
4. Copy the connection string (it looks like):
   ```
   postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```
5. **Important**: Replace `[YOUR-PASSWORD]` with the password you set in Step 1

## Step 3: Run Schema in Supabase

1. In Supabase dashboard, go to **SQL Editor** (left sidebar)
2. Click **"New query"**
3. Open `shared/schema.sql` from this project
4. Copy the entire contents
5. Paste into the SQL Editor
6. Click **"Run"** (or press Cmd/Ctrl + Enter)
7. You should see "Success. No rows returned"

## Step 4: Configure .env File

1. Copy the connection string from Step 2
2. Create/update `.env` file in project root:
   ```bash
   # Database (Supabase)
   DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   
   # Your other config...
   GEMINI_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   # etc.
   ```

## Step 5: Test Connection

Run the test script:
```bash
python scripts/test_db_connection.py
```

You should see:
```
✅ Connected successfully!
📊 PostgreSQL version: PostgreSQL 15.x
📋 Found 11 tables:
   - agents: 0 rows
   - compliance_evidence: 0 rows
   ...
✅ Database connection test passed!
```

## 🎉 Done!

Your database is now set up with:
- ✅ All required tables
- ✅ pgvector extension enabled
- ✅ Vector columns for RAG capabilities
- ✅ Indexes for fast queries

## Next Steps

1. **Test the connection**: Run `python scripts/test_db_connection.py`
2. **Start the backend**: The system will now use Supabase for storage
3. **Add embeddings**: When you implement RAG, embeddings will be stored in the vector columns

## Troubleshooting

### Connection fails
- Check that password in DATABASE_URL matches your Supabase password
- Verify project is active (not paused)
- Check network/firewall settings

### Schema errors
- Make sure you're using the updated `schema.sql` with pgvector
- Check Supabase SQL Editor for error messages
- Verify pgvector extension is available (it should be by default)

### Vector operations not working
- Ensure `CREATE EXTENSION vector;` ran successfully
- Check that embedding columns exist in tables
- Verify vector indexes were created

## Supabase Dashboard

You can view your data in Supabase:
- **Table Editor**: View/edit data
- **SQL Editor**: Run queries
- **Database**: View schema, indexes, etc.

## Free Tier Limits

Supabase free tier includes:
- 500 MB database storage
- 2 GB bandwidth
- Unlimited API requests
- pgvector included ✅

This is plenty for development and small deployments!

