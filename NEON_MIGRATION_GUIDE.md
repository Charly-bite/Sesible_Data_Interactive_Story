# 🚀 Neon.tech Migration Guide

## Why Migrate from Supabase to Neon?

**Problem:** Supabase free tier only provides IPv6 addresses, which Render's free tier doesn't support.

**Solution:** Neon.tech provides IPv4 support on free tier and is optimized for serverless deployments.

---

## Step 1: Create Neon Account

1. Go to https://neon.tech
2. Click "Sign Up" (free, no credit card required)
3. Sign in with GitHub or email

---

## Step 2: Create a New Project

1. Click "Create Project"
2. Choose settings:
   - **Project Name:** `sensible-data` (or your preferred name)
   - **Region:** Choose closest to your Render deployment
     - US East (Ohio) - for US East Render
     - US West (Oregon) - for US West Render
   - **Postgres Version:** 16 (latest)
3. Click "Create Project"

---

## Step 3: Get Connection String

1. On the project dashboard, click "Connection Details"
2. Select "Parameters only" or "Connection string"
3. Copy the connection string that looks like:
   ```
   postgresql://username:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. **Save this connection string** - you'll need it!

---

## Step 4: Run Migration

### On your local machine:

```bash
# 1. Set the Neon connection string
export NEON_DATABASE_URL='your-neon-connection-string-here'

# 2. Run the migration script
python3 migrate_to_neon.py

# 3. Type 'yes' when prompted to confirm
```

**Expected output:**
```
🚀 Neon PostgreSQL Migration
============================================================
Source: data.db
Target: Neon PostgreSQL

⚠️  This will DROP and recreate the 'clients' table in Neon.
Continue? (yes/no): yes

📂 Opening SQLite database: data.db
📊 Total rows to migrate: 1,500,000
🔌 Connecting to Neon PostgreSQL...
✓ Connected to Neon successfully
📋 Creating table structure...
✓ Table created
⏳ Migrating 1,500,000 rows in batches of 5000...
  Progress: 5,000/1,500,000 rows (0.3%)
  Progress: 10,000/1,500,000 rows (0.7%)
  ...
  Progress: 1,500,000/1,500,000 rows (100.0%)
✓ Migrated 1,500,000 rows successfully
🔧 Creating indexes...
  Creating idx_nombre_lc...
  Creating idx_paterno_lc...
  Creating idx_materno_lc...
  Creating idx_curp_lc...
✓ Indexes created
📊 Running ANALYZE...
✓ ANALYZE complete
✅ Verifying migration...
  PostgreSQL row count: 1,500,000
  Database size: 370 MB
```

---

## Step 5: Update Environment Variables

### Local (.env file):

```bash
# Update your .env file
DATABASE_URL=your-neon-connection-string-here
AUTH_USER=Storytelling
AUTH_PASSWORD=DatosSensibles2025$
FLASK_SECRET=storytelling-sensible-data-2025-secret-key-random
PYTHON_VERSION=3.13.0
```

### Render (Dashboard):

1. Go to https://render.com/dashboard
2. Click your web service
3. Go to "Environment" tab
4. Update `DATABASE_URL` to your Neon connection string
5. Click "Save Changes"
6. Render will auto-deploy with the new database

---

## Step 6: Test Locally

```bash
# Test the connection
python3 -c "from database import execute_query; result = execute_query('SELECT COUNT(*) as count FROM clients'); print(f'✅ Total rows: {result[0][\"count\"]:,}')"

# Expected output:
# ✓ Using PostgreSQL database
# ✅ Total rows: 1,500,000

# Start the application
python3 api.py

# Visit: http://localhost:5000
# Login and test search functionality
```

---

## Step 7: Verify Production

1. Wait for Render deployment to complete (2-3 minutes)
2. Visit: https://sesible-data-interactive-story.onrender.com
3. Login with credentials
4. Test search functionality
5. Check Render logs for:
   ```
   ✓ Using PostgreSQL database
   ✓ Connected successfully
   ```

---

## Neon Free Tier Limits

- **Storage:** 500 MB (you're using ~370 MB = 74%)
- **Compute:** 100 compute hours/month
- **Branches:** 10 branches
- **IPv4:** ✅ Supported (unlike Supabase)
- **Auto-scaling:** ✅ Scales to zero when inactive

---

## Benefits of Neon

✅ **IPv4 Support** - Works with Render free tier  
✅ **Serverless** - Auto-scales, pay only for compute used  
✅ **Fast Cold Starts** - ~100ms startup (vs Supabase ~1s)  
✅ **Branching** - Git-like database branches  
✅ **Free Tier** - 500 MB storage, 100 compute hours/month  

---

## Troubleshooting

### Connection fails locally
- Check DATABASE_URL is set: `echo $DATABASE_URL`
- Verify connection string format
- Ensure SSL mode is included: `?sslmode=require`

### Migration fails
- Check you have 1.5M row database (data.db)
- Verify NEON_DATABASE_URL is correct
- Ensure psycopg2-binary is installed

### Render deployment fails
- Check DATABASE_URL in Render environment variables
- Look for "Connected successfully" in logs
- Verify no typos in connection string

---

## Rollback (if needed)

If something goes wrong, you can rollback to local SQLite:

1. In Render, remove or comment out DATABASE_URL
2. Application will fallback to SQLite automatically
3. Note: SQLite won't work long-term on Render (ephemeral filesystem)

---

## Next Steps After Migration

1. ✅ Verify all searches work
2. ✅ Monitor Neon dashboard for usage
3. ✅ Delete Supabase project (optional, to avoid confusion)
4. ✅ Update README.md with new database info
5. ✅ Celebrate! 🎉

---

## Support

- **Neon Docs:** https://neon.tech/docs
- **Neon Discord:** https://discord.gg/neon
- **Issue?** Share error logs for help
