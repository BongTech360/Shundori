# Add Bot to Your Telegram Group - Quick Guide

## Step 1: Get Your Admin ID (2 minutes)

1. **Open Telegram** (phone or desktop)
2. **Search for @userinfobot**
3. **Start a chat** (it will reply automatically)
4. **Copy your ID number** - it looks like: `Id: 123456789`
5. **Update the .env file** with your ID

---

## Step 2: Choose How to Run the Bot

You have 2 options:

### Option A: Deploy to Cloud (Recommended - Always Running) ☁️

**Best for:** 24/7 operation, no need to keep computer on

**Railway (Easiest):**
1. Go to https://railway.app
2. Sign up (free)
3. Create project → Add PostgreSQL → Deploy code
4. See `DEPLOY_RAILWAY.md` for detailed steps

**Render (Also Easy):**
1. Go to https://render.com
2. Sign up (free)
3. Create PostgreSQL → Create Web Service
4. Deploy with `render.yaml` config

### Option B: Run Locally (Quick Test) 💻

**Best for:** Testing before cloud deployment

**Using Docker:**
```bash
cd /Users/macos/Desktop/Shundori
docker-compose up -d
```

**Using Python:**
```bash
cd /Users/macos/Desktop/Shundori
./setup_direct.sh  # First time only
./run_bot.sh
```

---

## Step 3: Add Bot to Your Telegram Group

1. **Open your Telegram group**
2. **Click on the group name** (at the top)
3. **Click "Add Members"** or "Add Participants"
4. **Search for your bot** by username
   - The username you created with @BotFather
   - Example: `@company_attendance_bot`
5. **Add the bot** to the group

---

## Step 4: Configure Bot in Group (Recommended)

1. **Go to group settings:**
   - Click group name → "Administrators"
2. **Add bot as admin:**
   - Click "Add Administrator"
   - Select your bot
   - Give permissions:
     - ✅ **Read messages** (required)
     - ✅ **Delete messages** (optional, for cleanup)
     - ❌ Don't need "Restrict members" or "Ban members"

**Note:** Bot doesn't require admin rights, but it's recommended for better functionality.

---

## Step 5: Test the Bot

### Test 1: Basic Response
In your group, send:
```
/start
```
Bot should respond with a welcome message.

### Test 2: Admin Command
Send (you must be the admin):
```
/report
```
You should see today's attendance report.

### Test 3: Attendance (During Window)
**Wait for 09:00-10:00 AM (Asia/Phnom_Penh time)**, then:
- Send `1` in the group
- You should receive a private message: "Good morning, [Your Name]! Attendance recorded."

---

## Step 6: Verify Everything Works

### Check Bot Status

**If running locally:**
- Check terminal/Docker logs
- Should see: "Bot initialized successfully"

**If on cloud:**
- Check platform logs (Railway/Render dashboard)
- Should see: "Bot initialized successfully"

### Check Bot is in Group
- Bot should appear in group members list
- Bot should respond to `/start`

---

## Daily Operation

Once set up, the bot automatically:

- **09:00 AM** (Asia/Phnom_Penh) - Opens attendance window
- **09:00-10:00 AM** - Accepts "1" messages for attendance
- **10:00 AM** - Closes window, marks absent members, applies fines
- **10:05 AM** - Posts daily report in group

**No manual intervention needed!**

---

## Quick Commands for Group Members

- **Record attendance:** Send `1` between 09:00-10:00 AM
- **View help:** Send `/start`

## Admin Commands (You Only)

- `/report [YYYY-MM-DD]` - View attendance report
- `/monthly YYYY-MM` - Export monthly CSV
- `/setfine <amount>` - Change fine amount
- `/set-window <HH:MM> <HH:MM>` - Change attendance window
- `/force-mark <user_id> present|absent` - Manual override
- `/export [YYYY-MM-DD]` - Export daily CSV

---

## Troubleshooting

### Bot Not Responding?

1. **Check if bot is running:**
   - Local: Check terminal/Docker
   - Cloud: Check platform dashboard

2. **Check bot is in group:**
   - Verify bot appears in members list
   - Try sending `/start`

3. **Check ADMIN_ID:**
   - Make sure it's set correctly in .env or platform
   - Get it from @userinfobot if needed

### Can't Send Private Messages?

- Bot will still record attendance
- Make sure you've started a chat with bot (send `/start` privately)
- Check logs for warnings

### Scheduler Not Working?

- Check timezone: Should be `Asia/Phnom_Penh`
- Check logs for "Scheduler started" message
- Verify system time is correct

---

## Need Help?

1. **Check logs** for error messages
2. **Review README.md** for detailed documentation
3. **Check DEPLOY_RAILWAY.md** for cloud deployment
4. **Verify all steps** above are completed

---

**🎉 Once bot is running and added to group, you're all set!**

The bot will automatically handle attendance starting from the next 09:00 AM (Asia/Phnom_Penh time).

