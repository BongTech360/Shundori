# 🚀 Deploy to Your Telegram Group - Step by Step

Follow these steps to get your bot running in your Telegram group.

## Prerequisites Checklist

Before starting, you need:
- [ ] Bot Token from @BotFather
- [ ] Your Telegram User ID from @userinfobot
- [ ] PostgreSQL installed (or Docker)

---

## Step 1: Get Your Bot Token (5 minutes)

1. **Open Telegram** on your phone or computer
2. **Search for @BotFather** and start a chat
3. **Send this command:** `/newbot`
4. **Follow the prompts:**
   - Bot name: `Company Attendance Bot` (or any name you like)
   - Bot username: `your_company_attendance_bot` (must end with 'bot', must be unique)
5. **Copy the token** - it looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
   - ⚠️ **Keep this secret!** Don't share it publicly.

**Example:**
```
BotFather: Alright, a new bot. How are we going to call it? Please choose a name for your bot.
You: Company Attendance Bot

BotFather: Good. Now let's choose a username for your bot. It must end in 'bot'.
You: company_attendance_bot

BotFather: Done! Use this token to access the HTTP API:
123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

---

## Step 2: Get Your Admin ID (2 minutes)

1. **Open Telegram**
2. **Search for @userinfobot** and start a chat
3. The bot will automatically reply with your info
4. **Find your ID** - it looks like: `Id: 123456789`
5. **Copy just the number** (e.g., `123456789`)

**Example:**
```
@userinfobot: 
First name: John
Last name: Doe
Username: @johndoe
Language: en
Id: 123456789
```

---

## Step 3: Choose Your Setup Method

You have 2 options:

### Option A: Docker (Easiest - Recommended) 🐳

**If you don't have Docker:**
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install and launch Docker Desktop
3. Wait for it to start (whale icon in menu bar)

**Then run:**
```bash
cd /Users/macos/Desktop/Shundori
./deploy.sh
```

The script will ask for your BOT_TOKEN and ADMIN_ID and set everything up automatically.

---

### Option B: Direct Python (No Docker) 🐍

**First, install PostgreSQL:**

**Using Homebrew (Recommended):**
```bash
# Install Homebrew if you don't have it:
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL
brew services start postgresql@15
```

**Or download from:**
https://www.postgresql.org/download/macosx/

**Then run:**
```bash
cd /Users/macos/Desktop/Shundori
./setup_direct.sh
```

This will:
- Ask for your BOT_TOKEN and ADMIN_ID
- Create .env file
- Set up Python virtual environment
- Install dependencies
- Initialize database

**To run the bot:**
```bash
./run_bot.sh
```

---

## Step 4: Create .env File (If Not Done Automatically)

If the scripts didn't create it, create `.env` file manually:

```bash
cd /Users/macos/Desktop/Shundori
cp env.example .env
```

Then edit `.env` and replace:
- `your_bot_token_here` → Your actual bot token
- `your_telegram_user_id_here` → Your actual user ID

**Example .env:**
```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_ID=123456789
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/attendance_bot
TZ=Asia/Phnom_Penh
DEFAULT_FINE_AMOUNT=20
ATTENDANCE_WINDOW_START=09:00
ATTENDANCE_WINDOW_END=10:00
REPORT_TIME=10:05
```

---

## Step 5: Start the Bot

### If using Docker:
```bash
cd /Users/macos/Desktop/Shundori
docker-compose up -d
```

### If using Direct Python:
```bash
cd /Users/macos/Desktop/Shundori
./run_bot.sh
```

**You should see:**
```
Bot initialized successfully
Scheduler started
Starting bot...
```

---

## Step 6: Add Bot to Your Telegram Group

1. **Open your Telegram group**
2. **Click on the group name** (at the top)
3. **Click "Add Members"** or "Add Participants"
4. **Search for your bot** by username (e.g., `@company_attendance_bot`)
5. **Add the bot** to the group

**Optional but Recommended:**
- Go to group settings → "Administrators"
- Add your bot as admin
- Give it permission to "Read messages"

---

## Step 7: Test the Bot

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

## Step 8: Verify Everything Works

### Check Bot Logs

**Docker:**
```bash
docker-compose logs -f bot
```

**Direct Python:**
The logs will show in the terminal where you ran `./run_bot.sh`

**You should see:**
- ✅ "Bot initialized successfully"
- ✅ "Scheduler started"
- ✅ "Starting bot..."

### Check Bot Status

**Docker:**
```bash
docker-compose ps
```
Both `db` and `bot` should show "Up"

**Direct Python:**
The bot process should be running in your terminal.

---

## Daily Operation

Once deployed, the bot will automatically:

- **09:00 AM** (Asia/Phnom_Penh) - Opens attendance window
- **09:00-10:00 AM** - Accepts "1" messages for attendance
- **10:00 AM** - Closes window, marks absent members, applies fines
- **10:05 AM** - Posts daily report in group

**No manual intervention needed!**

---

## Troubleshooting

### Bot Not Responding?

1. **Check if bot is running:**
   - Docker: `docker-compose ps`
   - Python: Check terminal where you ran it

2. **Check logs for errors:**
   - Docker: `docker-compose logs bot`
   - Python: Look at terminal output

3. **Verify BOT_TOKEN:**
   - Make sure it's correct in `.env` file
   - No extra spaces or quotes

4. **Check bot is in group:**
   - Make sure bot is added to the group
   - Try sending `/start` in the group

### Database Connection Error?

1. **Check PostgreSQL is running:**
   ```bash
   # Docker
   docker-compose ps db
   
   # Direct Python
   brew services list | grep postgresql
   ```

2. **Start PostgreSQL if needed:**
   ```bash
   # Docker (should auto-start)
   docker-compose up -d db
   
   # Direct Python
   brew services start postgresql@15
   ```

3. **Check DATABASE_URL in .env:**
   - Make sure it matches your PostgreSQL setup

### Scheduler Not Working?

1. **Check timezone:**
   - Verify `TZ=Asia/Phnom_Penh` in `.env`
   - Check system time is correct

2. **Check logs:**
   - Look for "Scheduler started" message
   - Check for any scheduler errors

### Can't Send Private Messages?

- The bot will still record attendance
- Make sure you've started a chat with the bot (send `/start` privately)
- Check logs for warnings about unreachable users

---

## Quick Commands Reference

### Start/Stop Bot

**Docker:**
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart bot

# View logs
docker-compose logs -f bot
```

**Direct Python:**
```bash
# Start
./run_bot.sh

# Stop
Press Ctrl+C in the terminal

# View logs
Check the terminal output
```

### Admin Commands (in Telegram)

- `/report [YYYY-MM-DD]` - View attendance report
- `/monthly YYYY-MM` - Export monthly CSV
- `/setfine <amount>` - Change fine amount
- `/set-window <HH:MM> <HH:MM>` - Change attendance window
- `/force-mark <user_id> present|absent` - Manual override
- `/export [YYYY-MM-DD]` - Export daily CSV

---

## Need Help?

1. **Check logs** for error messages
2. **Review README.md** for detailed documentation
3. **Check SETUP_GUIDE.md** for setup options
4. **Verify all prerequisites** are installed

---

## Success Checklist

Once everything is working, you should have:

- [x] Bot token obtained from @BotFather
- [x] Admin ID obtained from @userinfobot
- [x] .env file created with correct values
- [x] Bot running (Docker or Python)
- [x] Bot added to Telegram group
- [x] Bot responds to `/start` command
- [x] Bot responds to `/report` command (admin)
- [x] Scheduler running (check logs)
- [x] Ready for first attendance window at 09:00 AM

---

**🎉 Once all checkboxes are done, your bot is deployed and ready!**

The bot will automatically handle attendance starting from the next 09:00 AM (Asia/Phnom_Penh time).

