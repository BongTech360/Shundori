# Deploy to Railway - Step by Step (Right Now!)

## Your Configuration ✅
- **Bot Token:** `8221249139:AAFKdgbFIoSUa5loMzrN-tJOd_BFsdFXSYA`
- **Admin ID:** `7715502429` (@morphine_here)
- **Everything is ready!**

---

## Step 1: Sign Up for Railway (2 minutes)

1. Go to **https://railway.app**
2. Click **"Start a New Project"**
3. Sign up with:
   - **GitHub** (recommended - easiest)
   - Or **Email**

---

## Step 2: Create PostgreSQL Database (1 minute)

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Wait ~30 seconds for it to provision
5. ✅ Database is ready!

---

## Step 3: Deploy Your Bot Code

### Option A: From GitHub (Recommended)

**First, push your code to GitHub:**

1. **Create a GitHub repository:**
   - Go to https://github.com/new
   - Name it (e.g., `telegram-attendance-bot`)
   - Make it **Private** (recommended)
   - Click "Create repository"

2. **Push your code:**
   ```bash
   cd /Users/macos/Desktop/Shundori
   git init
   git add .
   git commit -m "Initial commit - Telegram Attendance Bot"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```
   (Replace YOUR_USERNAME and YOUR_REPO with your actual GitHub details)

3. **In Railway:**
   - Click **"+ New"** → **"GitHub Repo"**
   - Select your repository
   - Railway will auto-detect Python

### Option B: Deploy from Local Files (Using Railway CLI)

1. **Install Railway CLI:**
   ```bash
   brew install railway
   ```

2. **Login:**
   ```bash
   railway login
   ```

3. **Initialize:**
   ```bash
   cd /Users/macos/Desktop/Shundori
   railway init
   ```

4. **Link to PostgreSQL:**
   ```bash
   railway link
   # Select your PostgreSQL service
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

---

## Step 4: Set Environment Variables (CRITICAL!)

1. **In Railway dashboard:**
   - Click on your **bot service** (not PostgreSQL)
   - Go to **"Variables"** tab
   - Click **"+ New Variable"**

2. **Add these variables one by one:**

   ```
   BOT_TOKEN = 8221249139:AAFKdgbFIoSUa5loMzrN-tJOd_BFsdFXSYA
   ```
   
   ```
   ADMIN_ID = 7715502429
   ```
   
   ```
   DATABASE_URL = ${{Postgres.DATABASE_URL}}
   ```
   (Click "Reference Variable" and select your PostgreSQL service's DATABASE_URL)
   
   ```
   TZ = Asia/Phnom_Penh
   ```
   
   ```
   DEFAULT_FINE_AMOUNT = 20
   ```
   
   ```
   ATTENDANCE_WINDOW_START = 09:00
   ```
   
   ```
   ATTENDANCE_WINDOW_END = 10:00
   ```
   
   ```
   REPORT_TIME = 10:05
   ```

3. **Save** - Railway will auto-redeploy

---

## Step 5: Set Start Command

1. **In Railway dashboard:**
   - Click on your **bot service**
   - Go to **"Settings"** tab
   - Scroll to **"Start Command"**
   - Enter: `python bot.py`
   - **Save**

---

## Step 6: Verify Deployment

1. **Check logs:**
   - Click on your bot service
   - Go to **"Deployments"** tab
   - Click on the latest deployment
   - View logs

2. **Look for:**
   ```
   Bot initialized successfully
   Scheduler started
   Starting bot...
   ```

3. **If you see errors:**
   - Check all environment variables are set correctly
   - Make sure DATABASE_URL is linked to PostgreSQL
   - Check ADMIN_ID is correct: `7715502429`

---

## Step 7: Add Bot to Your Telegram Group

1. **Open your Telegram group**
2. **Click group name** (at top)
3. **Click "Add Members"**
4. **Search for your bot** (username from @BotFather)
5. **Add the bot**
6. **Optional:** Make bot admin in group settings

---

## Step 8: Test the Bot

1. **In your Telegram group, send:**
   ```
   /start
   ```
   Bot should respond!

2. **As admin, send:**
   ```
   /report
   ```
   You should see today's attendance report!

3. **During 09:00-10:00 AM (Asia/Phnom_Penh):**
   - Send `1` in the group
   - You'll receive a private message confirming attendance

---

## ✅ Success Checklist

- [ ] Railway account created
- [ ] PostgreSQL database created
- [ ] Bot code deployed
- [ ] All environment variables set
- [ ] Start command set to `python bot.py`
- [ ] Bot is running (check logs)
- [ ] Bot added to Telegram group
- [ ] Bot responds to `/start`
- [ ] Bot responds to `/report` (admin)

---

## Troubleshooting

### Bot Not Responding?

1. **Check Railway logs:**
   - Look for errors in deployment logs
   - Common issues:
     - Missing ADMIN_ID
     - Wrong BOT_TOKEN
     - Database connection error

2. **Verify environment variables:**
   - All 8 variables must be set
   - DATABASE_URL must reference PostgreSQL

3. **Check bot is in group:**
   - Verify bot is added to Telegram group
   - Try sending `/start`

### Database Connection Error?

1. **Verify PostgreSQL is running:**
   - Check PostgreSQL service status in Railway
   - Should show "Active"

2. **Check DATABASE_URL:**
   - Must use reference: `${{Postgres.DATABASE_URL}}`
   - Or copy actual connection string from PostgreSQL service

### Scheduler Not Working?

1. **Check timezone:**
   - Verify `TZ=Asia/Phnom_Penh` is set
   - Check logs for "Scheduler started"

---

## Railway Free Tier

- ✅ 500 hours/month free
- ✅ $5 credit monthly
- ✅ PostgreSQL included
- ⚠️ Service may sleep after inactivity (wakes on request)

**For 24/7 uptime:** Upgrade to paid plan ($5/month)

---

## Update Your Bot

When you make changes:

1. **If using GitHub:**
   - Push changes to GitHub
   - Railway auto-deploys

2. **If using CLI:**
   ```bash
   railway up
   ```

---

## View Logs Anytime

**In Railway dashboard:**
- Click on your bot service
- Go to "Deployments"
- Click on a deployment
- View logs

**Or using CLI:**
```bash
railway logs
```

---

## 🎉 You're Done!

Your bot is now:
- ✅ Running 24/7 on Railway
- ✅ Connected to PostgreSQL
- ✅ Ready to handle attendance
- ✅ Will automatically:
  - Open window at 09:00 AM
  - Accept "1" messages until 10:00 AM
  - Mark absent members at 10:00 AM
  - Post daily report at 10:05 AM

**Just add it to your Telegram group and you're all set!**

---

## Quick Reference

**Your Bot Details:**
- Token: `8221249139:AAFKdgbFIoSUa5loMzrN-tJOd_BFsdFXSYA`
- Admin: `7715502429` (@morphine_here)
- Timezone: Asia/Phnom_Penh
- Window: 09:00-10:00 AM
- Report: 10:05 AM

**Railway Dashboard:** https://railway.app

**Need Help?** Check logs in Railway dashboard for any errors!

