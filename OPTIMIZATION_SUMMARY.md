# Database Optimization & Deployment Summary

## What Was Done

### 1. ✅ Database Size Reduction (COMPLETED)

**Original database:** 864.94 MB (22 columns, 2,994,101 rows)  
**Optimized database:** 636.79 MB (7 columns, 2,994,101 rows)  
**Reduction:** 26.4% (228.15 MB saved)

**Columns kept:**
- NOMBRE, PATERNO, MATERNO, FECNAC, CALLE, COLONIA, CURP

**Columns removed:** (15 columns)
- CVE, SEXO, INT, EXT, CP, E, D, M, S, L, MZA, CONSEC, CRED, FOLIO, NAC

### 2. ✅ Files Created/Updated

**New files:**
- `reduce_database.py` - Script to optimize SQLite database
- `migrate_to_postgres.py` - Script to migrate SQLite → PostgreSQL
- `database.py` - Unified database module (supports SQLite + PostgreSQL)
- `DEPLOYMENT_GUIDE.md` - Complete deployment instructions
- `setup_deployment.sh` - Automated setup script
- `.env.example` - Environment configuration template

**Updated files:**
- `api.py` - Now supports both SQLite and PostgreSQL
- `client_data.py` - Updated to 7-column schema
- `build_db.py` - Updated for reduced columns
- `requirements.txt` - Added psycopg2-binary, python-dotenv
- `.gitignore` - Added database backup files

### 3. ✅ Application Updates

The Flask application now:
- ✅ Supports both SQLite (local) and PostgreSQL (production)
- ✅ Automatically detects which database to use via DATABASE_URL
- ✅ Uses proper SQL parameter placeholders (? for SQLite, %s for PostgreSQL)
- ✅ Loads environment variables from .env file
- ✅ Works with reduced 7-column schema

---

## Deployment Options

### Option 1: Supabase + Render (Recommended Free Solution)

**Problem:** Your optimized database (637 MB) is still larger than Supabase's free 500 MB limit.

**Solutions:**

#### A. Reduce Data Further (Recommended)
Migrate only 1.5M rows instead of 3M rows:
```bash
python3 migrate_to_postgres.py --limit 1500000
```
This will reduce the database to ~300-350 MB, fitting within free tier.

#### B. Use Multiple Free Supabase Projects
- Split data by state/region
- Create 2 free Supabase projects
- Store 1.5M rows in each
- Update app logic to query appropriate database

#### C. Upgrade Plans (Paid)
- **Supabase Pro:** $25/month → 8 GB database
- **Render PostgreSQL:** $7/month → 1 GB database

### Option 2: Render PostgreSQL ($7/month)

**Pros:**
- Integrated with your Flask app
- 1 GB database (enough for your 637 MB)
- Simpler setup
- No external dependencies

**Cons:**
- Not free ($7/month)

**Setup:**
1. Create Render PostgreSQL database
2. Get connection URL from Render dashboard
3. Set DATABASE_URL environment variable
4. Run migration script

### Option 3: Railway (Alternative)

**Free tier includes:**
- 500 hours/month compute
- 512 MB RAM
- Shared CPU
- 1 GB disk

**Setup:** Similar to Render but with Railway CLI

---

## Quick Start Guide

### Step 1: Choose Your Path

**Path A: Free with Data Limit (Recommended)**
```bash
# 1. Create Supabase account and project
# 2. Get DATABASE_URL from Supabase dashboard
# 3. Set environment variable
export DATABASE_URL='postgresql://postgres.xxxxx:PASSWORD@host:6543/postgres'

# 4. Migrate limited data (1.5M rows to fit free tier)
python3 migrate_to_postgres.py --limit 1500000

# 5. Test locally
python3 api.py
```

**Path B: Paid for Full Data**
```bash
# 1. Upgrade Supabase to Pro ($25/mo) or use Render PostgreSQL ($7/mo)
# 2. Get DATABASE_URL
# 3. Migrate all data
python3 migrate_to_postgres.py
```

**Path C: Keep Using SQLite (Local Only)**
```bash
# Just use the optimized database locally
# No migration needed
python3 api.py
```

### Step 2: Deploy to Render

```bash
# 1. Push to GitHub
git add .
git commit -m "Optimized database and added PostgreSQL support"
git push origin main

# 2. Create Render Web Service
# - Connect GitHub repo
# - Set environment variables (DATABASE_URL, AUTH_USER, AUTH_PASSWORD, FLASK_SECRET)
# - Deploy
```

### Step 3: Monitor & Test

- Visit your app: `https://your-app.onrender.com`
- Test search functionality
- Monitor database size in Supabase dashboard

---

## File Sizes Reference

```
Original CSV files:     ~1.2 GB (combined)
Original SQLite DB:     865 MB (22 columns)
Optimized SQLite DB:    637 MB (7 columns)
PostgreSQL (estimated): 400-500 MB (with indexes)
PostgreSQL limited:     300-350 MB (1.5M rows)
```

---

## Cost Comparison

| Solution | Database | App Hosting | Total/Month |
|----------|----------|-------------|-------------|
| **Supabase Free + Render** | Free (500MB limit) | Free | **$0** ⭐ |
| **Supabase Pro + Render** | $25 (8GB) | Free | **$25** |
| **Render DB + Render App** | $7 (1GB) | Free | **$7** ✅ |
| **Railway** | ~$5 (500MB) | Free | **$5** |

---

## Troubleshooting

### Database too large for Supabase free tier
→ Use `--limit 1500000` flag when migrating

### Connection errors
→ Check DATABASE_URL format (should start with `postgresql://`)
→ Verify Supabase project is active
→ Check firewall/network settings

### Render app sleeps (cold start)
→ Expected behavior on free tier
→ First request after 15min inactivity takes 30-60 seconds
→ Consider upgrade or external ping service

### Missing data after migration
→ Check migration logs
→ Verify all 2.99M rows transferred (or your limit)
→ Query database: `SELECT COUNT(*) FROM clients;`

---

## Support

For issues or questions:
1. Check DEPLOYMENT_GUIDE.md for detailed steps
2. Review migration logs
3. Test locally before deploying
4. Check Supabase/Render status pages

---

## Next Actions

1. ✅ Database optimized (637 MB)
2. ⏳ Choose deployment path (Supabase vs Render PostgreSQL)
3. ⏳ Create database account (Supabase or Render)
4. ⏳ Run migration script
5. ⏳ Test locally
6. ⏳ Deploy to Render
7. ⏳ Configure environment variables
8. ⏳ Test production app
9. ⏳ Monitor usage

---

**Recommendation:** Start with **Supabase Free + Render Free** using the `--limit` flag (1.5M rows). This gives you a free working deployment. If you need all 3M rows later, upgrade to Render PostgreSQL for $7/month (cheapest paid option).

Good luck! 🚀
