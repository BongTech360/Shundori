# Deploy to Cloud Platforms

**Note:** Netlify is **NOT suitable** for Telegram bots because:
- ❌ Netlify is for static sites and serverless functions
- ❌ Telegram bots need long-running processes
- ❌ Netlify functions have execution time limits
- ❌ No built-in PostgreSQL database

## ✅ Recommended Cloud Platforms

### Option 1: Railway (Easiest - Recommended) 🚂

**Why Railway:**
- ✅ Free tier available
- ✅ Supports Docker
- ✅ Built-in PostgreSQL
- ✅ Easy deployment
- ✅ Automatic HTTPS

**Steps:**

1. **Sign up:** https://railway.app
2. **Create new project**
3. **Add PostgreSQL:**
   - Click "New" → "Database" → "PostgreSQL"
4. **Deploy bot:**
   - Click "New" → "GitHub Repo" (or "Empty Project")
   - Connect your repository or upload files
   - Add environment variables:
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
   - Set start command: `python bot.py`
5. **Deploy!**

---

### Option 2: Render (Free Tier Available) 🎨

**Why Render:**
- ✅ Free tier (with limitations)
- ✅ Built-in PostgreSQL
- ✅ Easy setup
- ✅ Automatic deployments

**Steps:**

1. **Sign up:** https://render.com
2. **Create PostgreSQL:**
   - New → PostgreSQL
   - Copy the connection string
3. **Create Web Service:**
   - New → Web Service
   - Connect GitHub repo or upload
   - Settings:
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `python bot.py`
     - **Environment Variables:**
       ```
       BOT_TOKEN=8221249139:AAFKdgbFIoSUa5loMzrN-tJOd_BFsdFXSYA
       ADMIN_ID=your_telegram_user_id_here
       DATABASE_URL=<from PostgreSQL service>
       TZ=Asia/Phnom_Penh
       DEFAULT_FINE_AMOUNT=20
       ATTENDANCE_WINDOW_START=09:00
       ATTENDANCE_WINDOW_END=10:00
       REPORT_TIME=10:05
       ```
4. **Deploy!**

---

### Option 3: Heroku (Paid, but Reliable) 🟣

**Why Heroku:**
- ✅ Well-established platform
- ✅ Easy deployment
- ✅ Good documentation
- ⚠️ No free tier anymore (paid)

**Steps:**

1. **Install Heroku CLI:**
   ```bash
   brew tap heroku/brew && brew install heroku
   ```

2. **Login:**
   ```bash
   heroku login
   ```

3. **Create app:**
   ```bash
   cd /Users/macos/Desktop/Shundori
   heroku create your-bot-name
   ```

4. **Add PostgreSQL:**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

5. **Set environment variables:**
   ```bash
   heroku config:set BOT_TOKEN=8221249139:AAFKdgbFIoSUa5loMzrN-tJOd_BFsdFXSYA
   heroku config:set ADMIN_ID=your_telegram_user_id_here
   heroku config:set TZ=Asia/Phnom_Penh
   heroku config:set DEFAULT_FINE_AMOUNT=20
   heroku config:set ATTENDANCE_WINDOW_START=09:00
   heroku config:set ATTENDANCE_WINDOW_END=10:00
   heroku config:set REPORT_TIME=10:05
   ```

6. **Create Procfile:**
   ```bash
   echo "worker: python bot.py" > Procfile
   ```

7. **Deploy:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   heroku git:remote -a your-bot-name
   git push heroku main
   ```

---

### Option 4: Fly.io (Free Tier) ✈️

**Why Fly.io:**
- ✅ Free tier available
- ✅ Supports Docker
- ✅ Global deployment
- ✅ PostgreSQL available

**Steps:**

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login:**
   ```bash
   fly auth login
   ```

3. **Create app:**
   ```bash
   cd /Users/macos/Desktop/Shundori
   fly launch
   ```

4. **Add PostgreSQL:**
   ```bash
   fly postgres create
   fly postgres attach <postgres-app-name>
   ```

5. **Set secrets:**
   ```bash
   fly secrets set BOT_TOKEN=8221249139:AAFKdgbFIoSUa5loMzrN-tJOd_BFsdFXSYA
   fly secrets set ADMIN_ID=your_telegram_user_id_here
   fly secrets set TZ=Asia/Phnom_Penh
   ```

6. **Deploy:**
   ```bash
   fly deploy
   ```

---

## 🚀 Quick Deploy Script for Railway

Create `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python bot.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## 📋 Environment Variables Checklist

Make sure to set these on your chosen platform:

- ✅ `BOT_TOKEN=8221249139:AAFKdgbFIoSUa5loMzrN-tJOd_BFsdFXSYA`
- ⚠️ `ADMIN_ID=your_telegram_user_id_here` (get from @userinfobot)
- ✅ `DATABASE_URL` (provided by platform)
- ✅ `TZ=Asia/Phnom_Penh`
- ✅ `DEFAULT_FINE_AMOUNT=20`
- ✅ `ATTENDANCE_WINDOW_START=09:00`
- ✅ `ATTENDANCE_WINDOW_END=10:00`
- ✅ `REPORT_TIME=10:05`

---

## 🎯 My Recommendation

**For easiest deployment:** Use **Railway**
- Free tier available
- One-click PostgreSQL
- Simple environment variable setup
- Automatic HTTPS

**For free tier:** Use **Render**
- Free PostgreSQL included
- Easy setup
- Good for small bots

**For production:** Use **Heroku** or **Fly.io**
- More reliable
- Better support
- Paid but worth it

---

## ⚠️ Important Notes

1. **Get your ADMIN_ID:**
   - Message @userinfobot on Telegram
   - Copy your user ID
   - Replace `your_telegram_user_id_here` in environment variables

2. **Database will be created automatically:**
   - Most platforms create tables on first run
   - Or run: `python migrations/init_db.py`

3. **After deployment:**
   - Add bot to your Telegram group
   - Test with `/start` and `/report`
   - Wait for 09:00 AM for first attendance window

---

## 🔧 Need Help?

If you want me to help you deploy to a specific platform, let me know which one and I'll create detailed step-by-step instructions!

