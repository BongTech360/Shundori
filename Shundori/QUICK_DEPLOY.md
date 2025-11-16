# Quick Deployment Guide

Follow these steps to deploy the bot to your Telegram group.

## Step 1: Get Your Bot Token

1. Open Telegram and search for **@BotFather**
2. Start a chat and send `/newbot`
3. Follow the instructions:
   - Choose a name for your bot (e.g., "Company Attendance Bot")
   - Choose a username (must end with 'bot', e.g., "company_attendance_bot")
4. BotFather will give you a token like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
5. **Copy this token** - you'll need it in Step 3

## Step 2: Get Your Admin ID

1. Open Telegram and search for **@userinfobot**
2. Start a chat (no need to send anything)
3. The bot will reply with your user information
4. Look for "Id: 123456789" - **this is your ADMIN_ID**
5. **Copy this number** - you'll need it in Step 3

## Step 3: Deploy the Bot

### Option A: Using the Deployment Script (Easiest)

```bash
cd /Users/macos/Desktop/Shundori
./deploy.sh
```

The script will:
- Ask for your BOT_TOKEN and ADMIN_ID
- Create the .env file
- Start Docker containers
- Set everything up automatically

### Option B: Manual Setup

1. **Create .env file:**
```bash
cd /Users/macos/Desktop/Shundori
cp env.example .env
```

2. **Edit .env file** with your values:
```env
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_ID=your_user_id_from_userinfobot
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/attendance_bot
TZ=Asia/Phnom_Penh
DEFAULT_FINE_AMOUNT=20
ATTENDANCE_WINDOW_START=09:00
ATTENDANCE_WINDOW_END=10:00
REPORT_TIME=10:05
```

3. **Start the bot:**
```bash
docker-compose up -d
```

4. **Check if it's running:**
```bash
docker-compose ps
docker-compose logs -f bot
```

## Step 4: Add Bot to Your Group

1. Open your Telegram group
2. Click on group name → "Add Members"
3. Search for your bot (by the username you created, e.g., `@company_attendance_bot`)
4. Add the bot to the group

## Step 5: Configure Bot in Group (Recommended)

1. Go to group settings → "Administrators"
2. Add your bot as an administrator
3. Give it permission to:
   - ✅ Read messages
   - ✅ Delete messages (optional)
   - ❌ Don't need "Restrict members" or "Ban members"

**Note:** The bot doesn't require admin rights, but it's recommended for better functionality.

## Step 6: Test the Bot

1. **Test in group:**
   - Send `/start` in the group
   - The bot should respond (if it's working)

2. **Test attendance (during window 09:00-10:00 AM):**
   - Send `1` in the group
   - You should receive a private message: "Good morning, [Your Name]! Attendance recorded."

3. **Test admin commands:**
   - Send `/report` in the group or private chat
   - You should see today's attendance report

## Step 7: Verify It's Working

Check the logs to see if everything is running:
```bash
docker-compose logs -f bot
```

You should see:
- "Bot initialized successfully"
- "Scheduler started"
- "Starting bot..."

## Troubleshooting

### Bot not responding?
1. Check if bot is running: `docker-compose ps`
2. Check logs: `docker-compose logs bot`
3. Verify BOT_TOKEN is correct in .env
4. Make sure bot is added to the group

### Can't send private messages?
- The bot will still record attendance
- Check logs for warnings about unreachable users
- Make sure you've started a chat with the bot (send /start privately)

### Scheduler not working?
- Check timezone: `docker-compose exec bot date`
- Verify TZ=Asia/Phnom_Penh in .env
- Check scheduler logs in bot output

### Database errors?
- Make sure PostgreSQL container is running: `docker-compose ps`
- Check database logs: `docker-compose logs db`
- Restart containers: `docker-compose restart`

## Daily Operation

The bot will automatically:
- **09:00 AM** - Open attendance window
- **09:00-10:00 AM** - Accept "1" messages for attendance
- **10:00 AM** - Close window, mark absent members, apply fines
- **10:05 AM** - Post daily report in group

## Admin Commands Reference

All commands work in group or private chat:

- `/report [YYYY-MM-DD]` - View attendance report
- `/monthly YYYY-MM` - Export monthly CSV
- `/setfine <amount>` - Change fine amount (e.g., `/setfine 25`)
- `/set-window <HH:MM> <HH:MM>` - Change window (e.g., `/set-window 08:30 09:30`)
- `/force-mark <user_id> present|absent` - Manual override
- `/export [YYYY-MM-DD]` - Export daily CSV

## Stop the Bot

```bash
docker-compose down
```

## Restart the Bot

```bash
docker-compose restart bot
```

## Update the Bot

```bash
git pull  # if using git
docker-compose up -d --build
```

## Need Help?

1. Check logs: `docker-compose logs -f bot`
2. Review README.md for detailed documentation
3. Check DEPLOYMENT.md for advanced deployment options

---

**Ready to deploy?** Run `./deploy.sh` or follow the manual steps above!

