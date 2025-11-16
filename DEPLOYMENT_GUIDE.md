# Free-Tier Deployment Guide: Supabase + Render

This guide will help you deploy your Flask app with a split architecture:
- **Database**: Supabase (Free 500MB PostgreSQL)
- **Application**: Render (Free Flask hosting)

## Database Reduction Summary

✅ **Database optimized from 865 MB → 637 MB (26.4% reduction)**
- Removed 15 unused columns
- Kept only 7 essential columns: NOMBRE, PATERNO, MATERNO, FECNAC, CALLE, COLONIA, CURP
- Total records: 2,994,101

---

## Part 1: Set Up Supabase (Free PostgreSQL Database)

### Step 1: Create Supabase Account

1. Go to https://supabase.com
2. Sign up for a free account
3. Create a new project:
   - Project name: `sensible-data` (or your choice)
   - Database password: Create a strong password (save it!)
   - Region: Choose closest to your users
   - Wait ~2 minutes for project creation

### Step 2: Get Database Credentials

1. In your Supabase dashboard, go to **Settings** → **Database**
2. Find the **Connection string** section
3. Copy the **URI** (connection pooling mode) - it looks like:
   ```
   postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
4. Replace `[YOUR-PASSWORD]` with your actual database password

### Step 3: Upload Data to Supabase

We need to convert SQLite to PostgreSQL and upload it:

```bash
# Install required tools
pip install psycopg2-binary

# Run the migration script (provided below)
python migrate_to_postgres.py
```

**Note**: The migration script is `migrate_to_postgres.py` (see below)

---

## Part 2: Update Application for PostgreSQL

Your application will be updated to:
1. Connect to PostgreSQL (Supabase) instead of SQLite
2. Use environment variables for database URL
3. Work seamlessly on Render

### Environment Variables Needed

Create a `.env` file locally (for testing):
```env
DATABASE_URL=postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
AUTH_USER=Storytelling
AUTH_PASSWORD=DatosSensibles2025$
FLASK_SECRET=your-random-secret-key-here
```

**IMPORTANT**: Add `.env` to your `.gitignore` to avoid committing secrets!

---

## Part 3: Deploy to Render

### Step 1: Prepare Repository

1. Make sure these files are in your repo:
   - `requirements.txt` (updated with psycopg2)
   - `api.py` (updated for PostgreSQL)
   - `Procfile` (should exist)
   - `render.yaml` (optional, for auto-deploy)

2. Commit and push to GitHub:
```bash
git add .
git commit -m "Optimized database and added PostgreSQL support"
git push origin main
```

### Step 2: Create Render Web Service

1. Go to https://render.com
2. Sign up / Log in with GitHub
3. Click **New** → **Web Service**
4. Connect your GitHub repository
5. Configure:
   - **Name**: `sensible-data-app`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn api:app`
   - **Plan**: Free

### Step 3: Add Environment Variables in Render

In your Render service settings, add these environment variables:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Your Supabase connection string |
| `AUTH_USER` | Storytelling |
| `AUTH_PASSWORD` | DatosSensibles2025$ |
| `FLASK_SECRET` | (generate random string) |
| `PYTHON_VERSION` | 3.11.0 |

### Step 4: Deploy

1. Click **Create Web Service**
2. Wait for deployment (~5 minutes)
3. Your app will be live at: `https://sensible-data-app.onrender.com`

---

## Cost Breakdown (All FREE!)

### Supabase Free Tier
- ✅ 500 MB database (your optimized DB: 637 MB → **will need optimization or upgrade**)
- ✅ Unlimited API requests
- ✅ 2 GB file storage
- ✅ 50,000 monthly active users

### Render Free Tier
- ✅ 750 hours/month (enough for 1 app)
- ✅ 512 MB RAM
- ✅ Automatic HTTPS
- ⚠️ Spins down after 15 min inactivity (cold starts)

---

## Database Size Solutions

Your optimized database (637 MB) is still larger than Supabase's free 500 MB limit. Here are options:

### Option 1: Further Data Reduction (Recommended)
**Sample only the most recent records**:
```python
# In migrate_to_postgres.py, limit to recent data
# Example: Last 1.5 million records instead of 2.99 million
SELECT * FROM clients ORDER BY FECNAC DESC LIMIT 1500000
```

### Option 2: Upgrade Supabase ($25/month)
- 8 GB database
- Better performance
- No cold starts

### Option 3: Use Render PostgreSQL ($7/month)
- 1 GB database
- Integrated with your app
- Simpler setup

### Option 4: Split by Region
- Create multiple free Supabase projects
- Split data by region/state
- Update app to query correct database

---

## Testing Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with your credentials

3. Run locally:
```bash
python api.py
```

4. Test at http://localhost:5000

---

## Monitoring & Maintenance

### Check Database Size
```sql
SELECT pg_size_pretty(pg_database_size('postgres'));
```

### Check Table Size
```sql
SELECT pg_size_pretty(pg_total_relation_size('clients'));
```

### Backup Strategy
1. Supabase auto-backups (free tier: 7 days)
2. Manual export: Use `pg_dump` command
3. Keep SQLite backup locally

---

## Troubleshooting

### Issue: "Database too large"
- Solution: Further reduce data (see Option 1 above)

### Issue: "Render app sleeps"
- Expected on free tier
- First request after sleep takes ~30 seconds
- Consider upgrade or keep-alive service

### Issue: "Connection timeout"
- Check DATABASE_URL is correct
- Verify Supabase project is active
- Check firewall/network settings

### Issue: "Module not found"
- Run: `pip install -r requirements.txt`
- Verify all dependencies in requirements.txt

---

## Next Steps

1. ✅ Run `migrate_to_postgres.py` to upload data
2. ✅ Test locally with PostgreSQL
3. ✅ Deploy to Render
4. ✅ Update GitHub repo
5. ✅ Monitor performance

---

## Support & Resources

- **Supabase Docs**: https://supabase.com/docs
- **Render Docs**: https://render.com/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

Good luck with your deployment! 🚀
