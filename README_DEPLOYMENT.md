# 🚀 Quick Start: Deploy Your App (Free Tier)

This guide will get your app running on free hosting with an optimized database.

## ✅ What's Been Done

- ✅ Database optimized: 865 MB → 637 MB (26% reduction)
- ✅ Reduced columns: 22 → 7 (only what you display)
- ✅ Added PostgreSQL support (Supabase/Render compatible)
- ✅ Created migration scripts
- ✅ Updated application code

## 🎯 Choose Your Deployment Path

### Path 1: **FREE** - Supabase + Render (Recommended)

**Requirements:** Reduce database to ~1.5M rows (fits 500 MB free tier)

```bash
# 1. Reduce database size
python3 reduce_data_size.py
# Choose option 1: "Free tier optimized (1.5M rows → ~320 MB)"

# 2. Create Supabase account at https://supabase.com
# 3. Create new project, get DATABASE_URL

# 4. Set environment variable
export DATABASE_URL='postgresql://postgres.xxxxx:PASSWORD@host:6543/postgres'

# 5. Migrate to Supabase
python3 migrate_to_postgres.py

# 6. Test locally
python3 api.py

# 7. Deploy to Render (see DEPLOYMENT_GUIDE.md)
```

**Cost:** $0/month ✨  
**Pros:** Completely free, good for demos  
**Cons:** Only 1.5M of 3M rows, cold starts on Render

---

### Path 2: **$7/month** - Render PostgreSQL (All Data)

**Requirements:** None - keeps all 3M rows

```bash
# 1. Create Render account
# 2. Create PostgreSQL database (1 GB - $7/month)
# 3. Get DATABASE_URL from Render dashboard

# 4. Set environment variable
export DATABASE_URL='postgresql://...'

# 5. Migrate all data
python3 migrate_to_postgres.py

# 6. Create web service on Render
# 7. Deploy
```

**Cost:** $7/month  
**Pros:** All data, integrated, reliable  
**Cons:** Not free

---

### Path 3: Keep SQLite (Local Development Only)

```bash
# Just run locally - no migration needed
python3 api.py
```

**Cost:** $0  
**Pros:** Simple, no setup  
**Cons:** Can't deploy to production

---

## 📦 What's Included

### Scripts

- `reduce_database.py` - Removes unused columns from SQLite (DONE ✅)
- `reduce_data_size.py` - Reduces row count to fit free tier
- `migrate_to_postgres.py` - Migrates SQLite → PostgreSQL
- `setup_deployment.sh` - Interactive setup wizard

### Documentation

- `DEPLOYMENT_GUIDE.md` - Complete deployment instructions
- `OPTIMIZATION_SUMMARY.md` - What was optimized and why
- `README_DEPLOYMENT.md` - This file

### Updated Code

- `api.py` - Now supports SQLite AND PostgreSQL
- `database.py` - Unified database module
- `client_data.py` - Updated for 7-column schema
- `requirements.txt` - Added PostgreSQL dependencies

---

## 🏃 Quick Commands

### Install dependencies
```bash
pip install -r requirements.txt
```

### Test locally
```bash
python3 api.py
```

### Check database size
```bash
ls -lh data.db
```

### Reduce database for free tier
```bash
python3 reduce_data_size.py
```

### Migrate to PostgreSQL
```bash
export DATABASE_URL='your-postgres-url'
python3 migrate_to_postgres.py
```

### Interactive setup
```bash
./setup_deployment.sh
```

---

## 📊 Database Size Guide

| Rows | Estimated Size | Fits In |
|------|---------------|---------|
| 3M (all) | 637 MB | Render PostgreSQL ($7/mo) |
| 1.5M | ~320 MB | Supabase Free (500 MB) ✅ |
| 750K | ~160 MB | Supabase Free (comfortable) |

---

## 🔧 Environment Variables

Create a `.env` file (or set on Render):

```env
DATABASE_URL=postgresql://postgres.xxxxx:PASSWORD@host:6543/postgres
AUTH_USER=Storytelling
AUTH_PASSWORD=DatosSensibles2025$
FLASK_SECRET=your-random-secret-key
```

---

## ❓ FAQ

**Q: Why reduce from 3M to 1.5M rows?**  
A: Supabase's free tier has a 500 MB limit. 1.5M rows = ~320 MB.

**Q: Will I lose important data?**  
A: The sampling is random and even. You keep a representative subset. For production with all data, use paid hosting.

**Q: Can I upgrade later?**  
A: Yes! You can always migrate the full database to paid hosting.

**Q: How long does migration take?**  
A: 1.5M rows: ~15-20 minutes | 3M rows: ~30-40 minutes

**Q: What if Supabase fills up?**  
A: Monitor usage in Supabase dashboard. Upgrade to Pro ($25/mo) for 8 GB if needed.

---

## 🆘 Troubleshooting

### "Database too large"
→ Run `reduce_data_size.py` and choose option 1 or 2

### "Connection failed"
→ Check DATABASE_URL format  
→ Verify database is running  
→ Check firewall settings

### "Module not found"
→ Run `pip install -r requirements.txt`

### "Cold start slow on Render"
→ Expected on free tier (first request takes 30-60s)  
→ Upgrade to paid tier for always-on service

---

## 📚 More Information

- **Full deployment guide:** `DEPLOYMENT_GUIDE.md`
- **Optimization details:** `OPTIMIZATION_SUMMARY.md`
- **Supabase docs:** https://supabase.com/docs
- **Render docs:** https://render.com/docs

---

## ✅ Recommended Steps (Start Here!)

1. **Test locally first**
   ```bash
   python3 api.py
   ```

2. **Reduce database for free tier**
   ```bash
   python3 reduce_data_size.py
   # Choose option 1
   ```

3. **Create Supabase account**
   - Go to https://supabase.com
   - Create new project
   - Copy DATABASE_URL

4. **Migrate to Supabase**
   ```bash
   export DATABASE_URL='your-supabase-url'
   python3 migrate_to_postgres.py
   ```

5. **Deploy to Render**
   - Push to GitHub
   - Connect to Render
   - Add environment variables
   - Deploy!

---

**Need help?** Check the detailed guides in this repository.

Good luck! 🚀
