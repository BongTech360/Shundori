# Deploy to Railway - Step by Step Guide

Railway is the **easiest** way to deploy your Telegram bot. Follow these steps:

## Step 1: Sign Up for Railway

1. Go to https://railway.app
2. Click "Start a New Project"
3. Sign up with GitHub (recommended) or email

## Step 2: Create PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Wait for it to provision (takes ~30 seconds)
5. Click on the PostgreSQL service
6. Go to **"Variables"** tab
7. Copy the `DATABASE_URL` - you'll need this

## Step 3: Deploy Your Bot

### Option A: From GitHub (Recommended)

1. **Push your code to GitHub:**
   ```bash
   cd /Users/macos/Desktop/Shundori
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   # Create a repo on GitHub, then:
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin main
   ```

2. **In Railway:**
   - Click **"+ New"** → **"GitHub Repo"**
   - Select your repository
   - Railway will auto-detect Python

3. **Set Environment Variables:**
   - Click on your service
   - Go to **"Variables"** tab
   - Add these variables:
     ```
     BOT_TOKEN=8221249139:AAFKdgbFIoSUa5loMzrN-tJOd_BFsdFXSYA
     ADMIN_ID=your_telegram_user_id_here
     DATABASE_URL=${{Postgres.DATABASE_URL}}
     TZ=Asia/Phnom_Penh
     DEFAULT_FINE_AMOUNT=20
     ATTENDANCE_WINDOW_START=09:00
     ATTENDANCE_WINDOW_END=10:00
     REPORT_TIME=10:05
     ```
   - **Important:** For `DATABASE_URL`, click "Reference Variable" and select your PostgreSQL service's `DATABASE_URL`

4. **Set Start Command:**
   - Go to **"Settings"** tab
   - Under "Start Command", enter: `python bot.py`

5. **Deploy:**
   - Railway will automatically deploy
   - Watch the logs to see it start

### Option B: Deploy from Local Files

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

5. **Set environment variables:**
   ```bash
   railway variables set BOT_TOKEN=8221249139:AAFKdgbFIoSUa5loMzrN-tJOd_BFsdFXSYA
   railway variables set ADMIN_ID=your_telegram_user_id_here
   railway variables set TZ=Asia/Phnom_Penh
   railway variables set DEFAULT_FINE_AMOUNT=20
   railway variables set ATTENDANCE_WINDOW_START=09:00
   railway variables set ATTENDANCE_WINDOW_END=10:00
   railway variables set REPORT_TIME=10:05
   ```

6. **Deploy:**
   ```bash
   railway up
   ```

## Step 4: Get Your Admin ID

Before the bot works, you need to set your ADMIN_ID:

1. Open Telegram
2. Message **@userinfobot**
3. Copy your user ID (the number)
4. Update the `ADMIN_ID` variable in Railway:
   - Go to your service → Variables
   - Edit `ADMIN_ID` with your actual ID
   - Save (will auto-redeploy)

## Step 5: Verify Deployment

1. **Check logs:**
   - In Railway, click on your service
   - Go to **"Deployments"** tab
   - Click on the latest deployment
   - View logs - you should see:
     ```
     Bot initialized successfully
     Scheduler started
     Starting bot...
     ```

2. **Test in Telegram:**
   - Add your bot to a Telegram group
   - Send `/start` - bot should respond
   - Send `/report` (as admin) - should show report

## Step 6: Add Bot to Your Group

1. Open your Telegram group
2. Click group name → "Add Members"
3. Search for your bot (by username from @BotFather)
4. Add the bot
5. (Optional) Make bot an admin in group settings

## Troubleshooting

### Bot Not Responding?

1. **Check logs in Railway:**
   - Look for errors in the deployment logs
   - Common issues:
     - Missing ADMIN_ID
     - Wrong BOT_TOKEN
     - Database connection error

2. **Verify environment variables:**
   - Make sure all variables are set correctly
   - Check `DATABASE_URL` is linked to PostgreSQL

3. **Check bot is in group:**
   - Make sure bot is added to your Telegram group
   - Try sending `/start` in the group

### Database Errors?

1. **Verify PostgreSQL is running:**
   - Check PostgreSQL service status in Railway
   - Should show "Active"

2. **Check DATABASE_URL:**
   - Make sure it's using the reference variable: `${{Postgres.DATABASE_URL}}`
   - Or copy the actual connection string from PostgreSQL service

### Scheduler Not Working?

1. **Check timezone:**
   - Verify `TZ=Asia/Phnom_Penh` is set
   - Check logs for scheduler start message

2. **Check logs:**
   - Look for "Scheduler started" message
   - Check for any scheduler errors

## Railway Free Tier Limits

- ✅ 500 hours/month free
- ✅ $5 credit monthly
- ✅ PostgreSQL included
- ⚠️ Service sleeps after inactivity (wakes on request)

**Note:** For 24/7 uptime, you may need to upgrade to paid plan ($5/month).

## Update Your Bot

When you make changes:

1. **If using GitHub:**
   - Push changes to GitHub
   - Railway auto-deploys

2. **If using CLI:**
   ```bash
   railway up
   ```

## View Logs

```bash
railway logs
```

Or in Railway dashboard:
- Click on your service
- Go to "Deployments"
- Click on a deployment
- View logs

## Stop/Start Service

In Railway dashboard:
- Click on your service
- Toggle the power button to stop/start

---

**🎉 Your bot is now deployed and running on Railway!**

The bot will automatically:
- Handle attendance at 09:00-10:00 AM (Asia/Phnom_Penh)
- Post daily reports at 10:05 AM
- Process fines automatically

