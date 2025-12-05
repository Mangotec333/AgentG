# 🔐 Supabase Manual Setup (CAPTCHA Required)

## Current Status

I attempted to automate the Supabase account creation, but Supabase requires a CAPTCHA challenge that needs to be completed manually. Here's what you need to do:

## Quick Setup Steps

### 1. Complete Account Creation (Manual)

1. **Go to**: https://supabase.com/dashboard/sign-up
2. **Fill in**:
   - Email: `your_email@example.com`
   - Password: `your_strong_password_here`
3. **Complete the CAPTCHA** (visual challenge)
4. **Click "Sign up"**
5. **Check your email** for verification (if required)

### 2. Create a New Project

Once logged in:

1. Click **"New Project"** button
2. Fill in project details:
   - **Name**: `agentg` (or your preferred name)
   - **Database Password**: Use a strong password (save it!)
     - **Important**: Choose a unique, strong password and save it securely
   - **Region**: Choose closest to you (e.g., `US East (N. Virginia)`)
   - **Pricing Plan**: Free tier
3. Click **"Create new project"**
4. Wait 2-3 minutes for project to be provisioned

### 3. Get Connection String

1. In your project dashboard, go to **Settings** → **Database**
2. Scroll down to **Connection string** section
3. Select **"URI"** tab
4. Copy the connection string
5. **Important**: Replace `[YOUR-PASSWORD]` with your database password

The connection string will look like:
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

### 4. Run Schema

1. In Supabase dashboard, go to **SQL Editor** (left sidebar)
2. Click **"New query"**
3. Open `shared/schema.sql` from this project
4. Copy the entire contents
5. Paste into the SQL Editor
6. Click **"Run"** (or press Cmd/Ctrl + Enter)
7. You should see "Success. No rows returned"

### 5. Update .env File

Create or update `.env` file in project root:

```bash
# Database (Supabase)
# Replace [YOUR-PASSWORD] and [PROJECT-REF] with your actual values
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Your other config...
# Get your OpenAI API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Gemini API key (for fallback LLM)
# GEMINI_API_KEY=your_gemini_api_key_here
```

### 6. Test Connection

Run the test script:
```bash
python scripts/test_db_connection.py
```

## Alternative: I Can Help After You Complete CAPTCHA

Once you've:
1. ✅ Created the account (completed CAPTCHA)
2. ✅ Created a project
3. ✅ Got the connection string

I can help you:
- Run the schema automatically
- Update the .env file
- Test the connection
- Set up everything else

Just share the connection string with me!

## What's Already Done

✅ Schema updated with pgvector support  
✅ Vector columns added to events, incidents, and patterns tables  
✅ Setup documentation created  
✅ Test scripts ready  

You just need to complete the CAPTCHA and create the project manually.

