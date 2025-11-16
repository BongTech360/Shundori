# Telegram Attendance Bot

A production-ready Telegram bot for managing staff morning attendance with automatic fine calculation and daily reports.

## Features

- ✅ **Automatic Attendance Tracking**: Members send "1" between 09:00-10:00 AM (Asia/Phnom_Penh timezone)
- 💰 **Fine System**: Automatic $20 fine for late/absent members
- 📊 **Daily Reports**: Automated summary at 10:05 AM with present/absent members and fines
- 🔒 **Admin Controls**: Commands for reports, fine management, and manual overrides
- 📁 **CSV Export**: Export daily and monthly attendance reports
- ⏰ **Timezone-Aware**: All scheduling uses Asia/Phnom_Penh timezone
- 🐳 **Docker Support**: Easy deployment with Docker Compose

## Requirements

- Python 3.11+
- PostgreSQL 15+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Admin Telegram User ID

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Shundori
```

### 2. Environment Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

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

**Getting your Telegram User ID:**
- Send a message to [@userinfobot](https://t.me/userinfobot) on Telegram
- It will reply with your user ID

### 3. Docker Deployment (Recommended)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f bot

# Stop services
docker-compose down
```

### 4. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL (if not using Docker)
# Or use Docker for just the database:
docker-compose up -d db

# Run the bot
python bot.py
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    username VARCHAR(255),
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Attendance Records Table
```sql
CREATE TABLE attendance_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,  -- 'present', 'absent', 'late'
    timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Fines Table
```sql
CREATE TABLE fines (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date DATE NOT NULL,
    amount FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Settings Table
```sql
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Usage

### For Group Members

1. **Record Attendance**: Send "1" in the group chat between 09:00-10:00 AM
2. **Receive Greeting**: Bot sends a private message confirming attendance
3. **View Daily Report**: Bot posts summary at 10:05 AM in the group

### Admin Commands

All admin commands work in both group chat and private chat with the bot.

#### `/report [YYYY-MM-DD]`
View attendance report for a specific date (defaults to today).

```
/report 2024-01-15
```

#### `/monthly YYYY-MM`
Export monthly attendance report as CSV.

```
/monthly 2024-01
```

#### `/setfine <amount>`
Change the daily fine amount.

```
/setfine 25
```

#### `/set-window <HH:MM> <HH:MM>`
Change the attendance window times.

```
/set-window 08:30 09:30
```

#### `/force-mark <user_id> present|absent`
Manually override attendance for a user.

```
/force-mark 12345 present
```

#### `/export [YYYY-MM-DD]`
Export daily report as CSV file.

```
/export 2024-01-15
```

## How It Works

### Attendance Flow

1. **09:00 AM**: Attendance window opens automatically
2. **09:00-10:00 AM**: Members can send "1" to record attendance
3. **10:00 AM**: Window closes, absent members are marked and fined
4. **10:05 AM**: Daily report is posted in the group

### Fine Calculation

- Members who send "1" **before 10:00 AM**: No fine
- Members who send "1" **after 10:00 AM** (if window still open): Late, fine applied
- Members who **don't send "1"**: Absent, fine applied

### Timezone Handling

All times are in **Asia/Phnom_Penh** timezone. The bot uses:
- `pytz` for timezone conversion
- `APScheduler` with timezone-aware scheduling
- Server timezone doesn't matter (converted automatically)

## Testing

Run unit tests:

```bash
python -m pytest tests/
```

Or run specific test files:

```bash
python -m pytest tests/test_attendance.py
python -m pytest tests/test_reports.py
python -m pytest tests/integration_test.py
```

## Deployment

### Docker (Recommended)

The `docker-compose.yml` includes:
- PostgreSQL database
- Bot application
- Automatic restarts
- Volume for CSV exports

### Heroku

1. Create a Heroku app
2. Add PostgreSQL addon
3. Set environment variables
4. Deploy:

```bash
heroku create your-bot-name
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set BOT_TOKEN=your_token
heroku config:set ADMIN_ID=your_id
git push heroku main
```

### VPS Deployment

1. **Install dependencies:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip postgresql
```

2. **Setup PostgreSQL:**
```bash
sudo -u postgres createdb attendance_bot
sudo -u postgres createuser bot_user
```

3. **Clone and setup:**
```bash
git clone <repository-url>
cd Shundori
pip3 install -r requirements.txt
```

4. **Create systemd service** (`/etc/systemd/system/attendance-bot.service`):
```ini
[Unit]
Description=Telegram Attendance Bot
After=network.target postgresql.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/Shundori
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /path/to/Shundori/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Start service:**
```bash
sudo systemctl enable attendance-bot
sudo systemctl start attendance-bot
sudo systemctl status attendance-bot
```

### Webhook Setup (Alternative to Polling)

For production, webhooks are recommended:

```python
# In bot.py, replace run_polling with:
application.run_webhook(
    listen="0.0.0.0",
    port=8443,
    url_path=BOT_TOKEN,
    webhook_url="https://your-domain.com/" + BOT_TOKEN
)
```

**Nginx configuration:**
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    location /<BOT_TOKEN> {
        proxy_pass http://localhost:8443;
    }
}
```

## Project Structure

```
Shundori/
├── bot.py                 # Main bot application
├── database.py            # Database models and session
├── config.py              # Configuration management
├── attendance.py          # Attendance tracking logic
├── reports.py             # Report generation and CSV export
├── scheduler.py           # Scheduled tasks (window, reports)
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker Compose configuration
├── .env.example           # Environment variables template
├── README.md              # This file
└── tests/
    ├── test_attendance.py # Attendance unit tests
    ├── test_reports.py    # Report unit tests
    └── integration_test.py # Integration tests
```

## Troubleshooting

### Bot not responding
- Check BOT_TOKEN is correct
- Verify bot is added to the group
- Check logs: `docker-compose logs bot`

### Attendance not recorded
- Verify attendance window is open (09:00-10:00 AM)
- Check timezone settings
- Ensure bot has permission to read messages

### Database connection errors
- Verify DATABASE_URL is correct
- Check PostgreSQL is running: `docker-compose ps`
- Test connection: `psql $DATABASE_URL`

### Scheduler not working
- Check timezone configuration
- Verify APScheduler is running (check logs)
- Ensure system time is correct

## Security Notes

- Never commit `.env` file
- Keep BOT_TOKEN secret
- Use environment variables for sensitive data
- Restrict admin commands to authorized users only
- Regularly backup database

## License

MIT License

## Support

For issues and questions:
1. Check logs: `docker-compose logs -f bot`
2. Review this README
3. Check Telegram Bot API documentation

## Example Messages

### Daily Report Example
```
📊 Daily Attendance Report - 2024-01-15

👥 Total Members: 5

✅ Present Members:
  • John Doe (09:15:23)
  • Jane Smith (09:30:45)
  • Bob Johnson (09:45:12)

❌ Absent/Late Members:
  • Alice Brown - Fine: $20.00
  • Charlie Wilson - Fine: $20.00
```

### Greeting Message
```
Good morning, John Doe! Attendance recorded.
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

