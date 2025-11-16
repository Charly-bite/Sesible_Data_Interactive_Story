# 🔧 Render Deployment Fix - IPv6 Connection Issue

## Problem

Render's free tier doesn't support IPv6 connections to Supabase, causing this error:
```
Network is unreachable - connection to server at IPv6 address
```

## ✅ Solution Applied

### 1. Updated `database.py`
- Modified connection to use **port 6543** (connection pooling) instead of 5432
- Added SSL requirement
- Code automatically handles IPv4 preference

### 2. Update Your Environment Variable on Render

You need to update the `DATABASE_URL` on Render to use **port 6543** (connection pooling):

**OLD (won't work on Render):**
```
postgresql://postgres:6#eeirGH.GbvVsF@db.uufmmcuesaayudnburpt.supabase.co:5432/postgres
```

**NEW (use this on Render):**
```
postgresql://postgres:6#eeirGH.GbvVsF@db.uufmmcuesaayudnburpt.supabase.co:6543/postgres
```

**Key change:** `:5432` → `:6543`

---

## 🚀 How to Fix on Render

### Step 1: Update Local .env File

```bash
cd /home/byte/Storytelling_tareas/Sensible
```

Edit `.env` file and change port from 5432 to 6543:

```env
DATABASE_URL=postgresql://postgres:6#eeirGH.GbvVsF@db.uufmmcuesaayudnburpt.supabase.co:6543/postgres
AUTH_USER=Storytelling
AUTH_PASSWORD=DatosSensibles2025$
FLASK_SECRET=storytelling-sensible-data-2025-secret-key-random
PYTHON_VERSION=3.11.0
```

### Step 2: Commit and Push Updated Code

```bash
git add database.py
git commit -m "Fix: Use connection pooling port for Render IPv4 compatibility"
git push origin main
```

### Step 3: Update Environment Variable on Render

1. Go to your Render dashboard
2. Click on your web service
3. Go to **"Environment"** tab
4. Find `DATABASE_URL`
5. Click **"Edit"**
6. Change the value to:
   ```
   postgresql://postgres:6#eeirGH.GbvVsF@db.uufmmcuesaayudnburpt.supabase.co:6543/postgres
   ```
7. Click **"Save Changes"**

### Step 4: Manual Deploy (or wait for auto-deploy)

1. Go to **"Manual Deploy"** tab
2. Click **"Clear build cache & deploy"**

---

## 📝 Alternative: Get Connection String from Supabase

If you want to verify the correct connection string:

1. Go to your Supabase Dashboard
2. Click **Settings** → **Database**
3. Under **Connection string**, select **"Connection Pooling"** mode
4. Copy the **URI** (should have port 6543)
5. Replace `[YOUR-PASSWORD]` with: `6#eeirGH.GbvVsF`

---

## ✅ Expected Result

After these changes:
- Application will connect to Supabase using IPv4-compatible connection pooling
- Port 6543 works better with Render's networking
- Connection will be stable and fast

---

## 🧪 Test Locally First

Before deploying, test locally with the new connection string:

```bash
# Update .env with port 6543
export $(grep -v '^#' .env | xargs)
python3 api.py
```

Visit `http://localhost:5000` and test the search functionality.

---

## 📊 What Changed

| Setting | Before | After | Why |
|---------|--------|-------|-----|
| Port | 5432 (direct) | 6543 (pooling) | Better for Render |
| SSL | Not specified | Required | Security |
| Connection | Direct | Pooled | More stable |

---

## ⚠️ Important Notes

1. **Use port 6543 on Render** - This is the connection pooling port
2. **Port 5432 works locally** - But not on Render free tier
3. **The code handles both** - `database.py` now converts automatically
4. **SSL is required** - Added automatically by the code

---

## 🔍 Verification Steps

After deploying:

1. Check Render logs for connection success
2. Test a search on your deployed app
3. Verify no "Network unreachable" errors
4. Confirm data loads correctly

---

## 💡 Why This Happens

- **Supabase** uses IPv6 for direct connections (port 5432)
- **Render free tier** only supports IPv4
- **Connection pooling** (port 6543) uses IPv4-compatible routing
- **Solution:** Use pooled connections with IPv4 preference

---

## 🆘 If Still Not Working

1. **Double-check the DATABASE_URL** on Render environment variables
2. **Verify port is 6543** (not 5432)
3. **Check Supabase project is active**
4. **Look at Render logs** for specific error messages
5. **Try manual deploy** with cleared cache

---

**Status: Fix ready to deploy!** 🚀

Push the code changes and update the environment variable on Render.
