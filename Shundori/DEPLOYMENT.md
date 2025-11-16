# Deployment Guide

This guide covers deployment options for the Telegram Attendance Bot.

## Prerequisites

- Telegram Bot Token from [@BotFather](https://t.me/botfather)
- Your Telegram User ID (get it from [@userinfobot](https://t.me/userinfobot))
- PostgreSQL database (or use Docker)
- Server/VPS with Python 3.11+ or Docker support

## Option 1: Docker Deployment (Recommended)

### Local Development

1. **Clone and setup:**
```bash
git clone <repository-url>
cd Shundori
cp env.example .env
```

2. **Edit `.env` file:**
```env
BOT_TOKEN=your_bot_token
ADMIN_ID=your_user_id
DATABASE_URL=postgresql://postgres:postgres@db:5432/attendance_bot
```

3. **Start services:**
```bash
docker-compose up -d
```

4. **View logs:**
```bash
docker-compose logs -f bot
```

5. **Stop services:**
```bash
docker-compose down
```

### Production Deployment

1. **On your server, clone the repository:**
```bash
git clone <repository-url>
cd Shundori
```

2. **Create `.env` file with production values:**
```env
BOT_TOKEN=your_production_token
ADMIN_ID=your_user_id
DATABASE_URL=postgresql://user:password@db:5432/attendance_bot
TZ=Asia/Phnom_Penh
```

3. **Start with Docker Compose:**
```bash
docker-compose up -d
```

4. **Setup auto-restart (if systemd available):**
Create `/etc/systemd/system/attendance-bot.service`:
```ini
[Unit]
Description=Telegram Attendance Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/Shundori
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable attendance-bot
sudo systemctl start attendance-bot
```

## Option 2: Heroku Deployment

1. **Install Heroku CLI:**
```bash
# macOS
brew install heroku/brew/heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Login and create app:**
```bash
heroku login
heroku create your-bot-name
```

3. **Add PostgreSQL addon:**
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

4. **Set environment variables:**
```bash
heroku config:set BOT_TOKEN=your_token
heroku config:set ADMIN_ID=your_user_id
heroku config:set TZ=Asia/Phnom_Penh
```

5. **Create `Procfile`:**
```
worker: python bot.py
```

6. **Deploy:**
```bash
git push heroku main
```

7. **View logs:**
```bash
heroku logs --tail
```

## Option 3: VPS Deployment (Manual)

### Step 1: Server Setup

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and dependencies
sudo apt-get install python3 python3-pip python3-venv postgresql postgresql-contrib

# Install PostgreSQL
sudo -u postgres createdb attendance_bot
sudo -u postgres createuser bot_user
sudo -u postgres psql -c "ALTER USER bot_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE attendance_bot TO bot_user;"
```

### Step 2: Application Setup

```bash
# Clone repository
cd /opt
sudo git clone <repository-url> attendance-bot
cd attendance-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
sudo nano .env
# Add your configuration
```

### Step 3: Initialize Database

```bash
python migrations/init_db.py
```

### Step 4: Create Systemd Service

Create `/etc/systemd/system/attendance-bot.service`:

```ini
[Unit]
Description=Telegram Attendance Bot
After=network.target postgresql.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/opt/attendance-bot
Environment="PATH=/opt/attendance-bot/venv/bin"
ExecStart=/opt/attendance-bot/venv/bin/python /opt/attendance-bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 5: Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable attendance-bot
sudo systemctl start attendance-bot
sudo systemctl status attendance-bot
```

### Step 6: View Logs

```bash
sudo journalctl -u attendance-bot -f
```

## Option 4: Webhook Deployment

For production, webhooks are more efficient than polling.

### Modify `bot.py`:

Replace the `main()` function:

```python
def main():
    """Main entry point."""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable is not set")
    
    if not ADMIN_ID:
        raise ValueError("ADMIN_ID environment variable is not set")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # Setup handlers
    setup_handlers(application)
    
    # Run with webhook
    import os
    port = int(os.getenv('PORT', 8443))
    webhook_url = os.getenv('WEBHOOK_URL')
    
    if webhook_url:
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=BOT_TOKEN,
            webhook_url=f"{webhook_url}/{BOT_TOKEN}"
        )
    else:
        # Fallback to polling
        application.run_polling(allowed_updates=Update.ALL_TYPES)
```

### Nginx Configuration

Create `/etc/nginx/sites-available/attendance-bot`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /<BOT_TOKEN> {
        proxy_pass http://localhost:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/attendance-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Monitoring

### Health Check

Create a simple health check endpoint (optional):

```python
# Add to bot.py
from aiohttp import web

async def health_check(request):
    return web.Response(text="OK")

# In main(), add:
app = web.Application()
app.router.add_get('/health', health_check)
web.run_app(app, port=8080)
```

### Logging

Logs are automatically written to stdout. For file logging, modify `bot.py`:

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('bot.log', maxBytes=10485760, backupCount=5)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(handler)
```

## Backup

### Database Backup

```bash
# Manual backup
pg_dump attendance_bot > backup_$(date +%Y%m%d).sql

# Automated daily backup (cron)
0 2 * * * pg_dump attendance_bot > /backups/attendance_$(date +\%Y\%m\%d).sql
```

### Restore

```bash
psql attendance_bot < backup_20240115.sql
```

## Troubleshooting

### Bot not responding
- Check BOT_TOKEN is correct
- Verify bot is added to group
- Check logs for errors

### Database connection errors
- Verify DATABASE_URL format
- Check PostgreSQL is running
- Test connection: `psql $DATABASE_URL`

### Scheduler not working
- Check timezone settings
- Verify APScheduler logs
- Ensure system time is synchronized

### Permission errors
- Check file permissions
- Verify user has access to database
- Check systemd service user

## Security Checklist

- [ ] `.env` file is not committed to git
- [ ] Database password is strong
- [ ] Bot token is kept secret
- [ ] Admin commands are restricted
- [ ] Regular backups are configured
- [ ] Logs don't contain sensitive data
- [ ] Firewall rules are configured
- [ ] SSL/TLS is enabled (for webhooks)

## Updates

To update the bot:

```bash
# Docker
cd /path/to/Shundori
git pull
docker-compose restart bot

# Systemd
cd /opt/attendance-bot
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart attendance-bot
```

