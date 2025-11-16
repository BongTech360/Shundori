# Telegram Attendance Bot - Node.js Implementation

This is the Node.js/Telegraf implementation of the Telegram Attendance Bot.

## Quick Start

### Prerequisites
- Node.js 16+ and npm
- PostgreSQL 15+
- Telegram Bot Token from [@BotFather](https://t.me/botfather)
- Your Telegram User ID (from [@userinfobot](https://t.me/userinfobot))

### Installation

1. **Install dependencies:**
```bash
cd nodejs
npm install
```

2. **Create `.env` file:**
```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id_here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/attendance_bot
TZ=Asia/Phnom_Penh
DEFAULT_FINE_AMOUNT=20
ATTENDANCE_WINDOW_START=09:00
ATTENDANCE_WINDOW_END=10:00
REPORT_TIME=10:05
```

3. **Initialize database:**
The database tables will be created automatically on first run.

4. **Start the bot:**
```bash
npm start
```

Or for development with auto-reload:
```bash
npm run dev
```

## Project Structure

```
nodejs/
├── bot.js          # Main bot application
├── database.js     # PostgreSQL connection and initialization
├── attendance.js   # Attendance tracking logic
├── reports.js      # Report generation and CSV export
├── scheduler.js    # Cron job scheduling
├── config.js       # Configuration management
├── package.json    # Dependencies
└── README.md       # This file
```

## Features

- ✅ Attendance tracking with time windows
- ✅ Automatic fine calculation ($20 default)
- ✅ Daily reports at 10:05 AM
- ✅ Admin commands for management
- ✅ CSV export (daily and monthly)
- ✅ Timezone-aware (Asia/Phnom_Penh)

## Admin Commands

All commands work in group chat or private chat:

- `/report [YYYY-MM-DD]` - View daily report
- `/monthly YYYY-MM` - Export monthly CSV
- `/setfine <amount>` - Change fine amount
- `/set-window <HH:MM> <HH:MM>` - Change attendance window
- `/force-mark <user_id> present|absent` - Manual override
- `/export [YYYY-MM-DD]` - Export daily CSV

## Database Schema

The bot uses the same PostgreSQL schema as the Python version:
- `users` - Telegram user information
- `attendance_records` - Daily attendance status
- `fines` - Fine records
- `settings` - Bot configuration

## Deployment

### Docker

Create a `Dockerfile`:
```dockerfile
FROM node:18-slim

WORKDIR /app

COPY nodejs/package*.json ./
RUN npm install --production

COPY nodejs/ .

CMD ["node", "bot.js"]
```

### Systemd Service

Create `/etc/systemd/system/attendance-bot-nodejs.service`:
```ini
[Unit]
Description=Telegram Attendance Bot (Node.js)
After=network.target postgresql.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/Shundori/nodejs
Environment="NODE_ENV=production"
ExecStart=/usr/bin/node /path/to/Shundori/nodejs/bot.js
Restart=always

[Install]
WantedBy=multi-user.target
```

## Testing

Run tests (when implemented):
```bash
npm test
```

## Comparison with Python Version

See `../IMPLEMENTATION_COMPARISON.md` for a detailed comparison.

## Troubleshooting

### Bot not responding
- Check BOT_TOKEN is correct
- Verify bot is added to group
- Check console logs for errors

### Database errors
- Verify DATABASE_URL format
- Ensure PostgreSQL is running
- Check database permissions

### Scheduler not working
- Verify timezone settings
- Check node-cron logs
- Ensure system time is synchronized

## License

MIT License

