# Setup Guide - Choose Your Deployment Method

## Option 1: Docker (Recommended - Easiest) 🐳

### Install Docker Desktop

1. **Download Docker Desktop for Mac:**
   - Visit: https://www.docker.com/products/docker-desktop
   - Download and install Docker Desktop
   - Launch Docker Desktop and wait for it to start

2. **Verify installation:**
   ```bash
   docker --version
   docker-compose --version
   ```

3. **Deploy the bot:**
   ```bash
   cd /Users/macos/Desktop/Shundori
   ./deploy.sh
   ```

   Or manually:
   ```bash
   # Create .env file (see below)
   docker-compose up -d
   ```

---

## Option 2: Direct Python (No Docker) 🐍

If you prefer not to use Docker, you can run the bot directly with Python.

### Prerequisites

1. **Install Python 3.11+**
   ```bash
   python3 --version  # Should be 3.11 or higher
   ```

2. **Install PostgreSQL**
   - **Option A: Homebrew (Recommended)**
     ```bash
     brew install postgresql@15
     brew services start postgresql@15
     ```
   
   - **Option B: Download from postgresql.org**
     - Visit: https://www.postgresql.org/download/macosx/
     - Download and install PostgreSQL

3. **Create database:**
   ```bash
   createdb attendance_bot
   # Or using psql:
   psql postgres
   CREATE DATABASE attendance_bot;
   \q
   ```

### Setup Steps

1. **Create virtual environment:**
   ```bash
   cd /Users/macos/Desktop/Shundori
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create .env file:**
   ```bash
   cp env.example .env
   # Edit .env with your BOT_TOKEN and ADMIN_ID
   ```

4. **Initialize database:**
   ```bash
   python migrations/init_db.py
   ```

5. **Run the bot:**
   ```bash
   python bot.py
   ```

---

## Getting Your Bot Token and Admin ID

### Get Bot Token from @BotFather

1. Open Telegram
2. Search for **@BotFather**
3. Send `/newbot`
4. Follow instructions:
   - Name: "Company Attendance Bot" (or any name)
   - Username: "company_attendance_bot" (must end with 'bot')
5. Copy the token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Get Your Admin ID from @userinfobot

1. Open Telegram
2. Search for **@userinfobot**
3. Start a chat (it will reply automatically)
4. Look for "Id: 123456789" - this is your ADMIN_ID

---

## Create .env File

Create a file named `.env` in the project directory:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_ID=your_user_id_from_userinfobot

# Database Configuration
# For Docker:
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/attendance_bot
# For Direct Python (if different):
# DATABASE_URL=postgresql://your_username@localhost:5432/attendance_bot

# Timezone
TZ=Asia/Phnom_Penh

# Fine Configuration (default)
DEFAULT_FINE_AMOUNT=20

# Attendance Window (default)
ATTENDANCE_WINDOW_START=09:00
ATTENDANCE_WINDOW_END=10:00

# Report Time
REPORT_TIME=10:05
```

**Replace:**
- `your_bot_token_from_botfather` with your actual bot token
- `your_user_id_from_userinfobot` with your actual user ID

---

## Add Bot to Your Telegram Group

1. Open your Telegram group
2. Click group name → "Add Members"
3. Search for your bot (by username, e.g., `@company_attendance_bot`)
4. Add the bot
5. (Optional) Make bot an admin in group settings

---

## Test the Bot

1. **In the group, send:**
   - `/start` - Bot should respond

2. **During attendance window (09:00-10:00 AM):**
   - Send `1` in the group
   - You should receive a private message

3. **Test admin command:**
   - Send `/report` (you should see a report)

---

## Which Option Should I Choose?

### Choose Docker if:
- ✅ You want the easiest setup
- ✅ You don't want to manage PostgreSQL separately
- ✅ You want isolated environment
- ✅ You're comfortable with Docker

### Choose Direct Python if:
- ✅ You already have PostgreSQL installed
- ✅ You prefer not to use Docker
- ✅ You want direct control over the process
- ✅ You're familiar with Python virtual environments

---

## Troubleshooting

### Docker Issues
- **Docker not starting?** Make sure Docker Desktop is running
- **Port 5432 already in use?** Stop other PostgreSQL instances
- **Permission denied?** Check Docker Desktop permissions in System Settings

### Python Issues
- **Module not found?** Make sure virtual environment is activated
- **Database connection error?** Check PostgreSQL is running: `brew services list`
- **Port 5432 in use?** Check: `lsof -i :5432`

### Bot Issues
- **Bot not responding?** Check logs and verify BOT_TOKEN
- **Can't send private messages?** Make sure you've started a chat with the bot
- **Scheduler not working?** Check timezone settings

---

## Next Steps

Once the bot is running:

1. ✅ Bot is added to your group
2. ✅ Bot responds to commands
3. ✅ Wait for 09:00 AM (Asia/Phnom_Penh) for first attendance window
4. ✅ Test by sending "1" during the window
5. ✅ Check daily report at 10:05 AM

For more details, see `QUICK_DEPLOY.md` or `README.md`.

