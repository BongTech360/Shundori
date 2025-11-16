# Project Summary: Telegram Attendance Bot

## Overview

A production-ready Telegram bot for managing staff morning attendance with automatic fine calculation, daily reports, and comprehensive admin controls. Built with Python using `python-telegram-bot`, PostgreSQL, and APScheduler.

## Architecture

### Core Components

1. **bot.py** - Main bot application with command handlers
2. **database.py** - SQLAlchemy models and database session management
3. **attendance.py** - Attendance tracking logic and fine calculation
4. **reports.py** - Report generation and CSV export functionality
5. **scheduler.py** - APScheduler setup for automated tasks
6. **config.py** - Configuration management
7. **utils.py** - Timezone and utility functions

### Database Schema

- **users** - Telegram user information
- **attendance_records** - Daily attendance status
- **fines** - Fine records for late/absent members
- **settings** - Bot configuration (fine amount, window times)

### Key Features

✅ **Automatic Attendance Tracking**
- Members send "1" between 09:00-10:00 AM (Asia/Phnom_Penh)
- Window automatically opens/closes via scheduler
- Private greeting message on successful attendance

✅ **Fine System**
- $20 default fine for late/absent members
- Configurable via admin command
- Running totals tracked per user

✅ **Daily Reports**
- Automated summary at 10:05 AM
- Lists present and absent members
- Shows fines for the day

✅ **Admin Commands**
- `/report [date]` - View daily report
- `/monthly YYYY-MM` - Export monthly CSV
- `/setfine <amount>` - Change fine amount
- `/set-window <start> <end>` - Change attendance window
- `/force-mark <user_id> <status>` - Manual override
- `/export [date]` - Export daily CSV

✅ **CSV Export**
- Daily attendance reports
- Monthly aggregated reports
- Includes all user data and fines

✅ **Timezone Handling**
- All times in Asia/Phnom_Penh timezone
- Server timezone independent
- Timezone-aware scheduling

## File Structure

```
Shundori/
├── bot.py                 # Main bot application
├── database.py            # Database models
├── config.py              # Configuration
├── attendance.py          # Attendance logic
├── reports.py             # Reports & CSV export
├── scheduler.py           # Scheduled tasks
├── utils.py               # Utilities
├── requirements.txt       # Dependencies
├── Dockerfile            # Docker image
├── docker-compose.yml    # Docker Compose config
├── README.md             # Main documentation
├── DEPLOYMENT.md         # Deployment guide
├── migrations/
│   └── init_db.py        # Database initialization
└── tests/
    ├── test_attendance.py
    ├── test_reports.py
    └── integration_test.py
```

## Technology Stack

- **Python 3.11+**
- **python-telegram-bot 20.7** - Telegram Bot API
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL** - Database
- **APScheduler 3.10** - Task scheduling
- **pandas** - CSV export
- **pytz** - Timezone handling

## Deployment Options

1. **Docker Compose** (Recommended)
   - Includes PostgreSQL
   - Easy setup and management
   - Production-ready

2. **Heroku**
   - Simple deployment
   - Managed PostgreSQL
   - Auto-scaling

3. **VPS/Server**
   - Full control
   - Systemd service
   - Custom configuration

4. **Webhook** (Production)
   - More efficient than polling
   - Requires HTTPS endpoint

## Testing

- Unit tests for attendance logic
- Unit tests for report generation
- Integration tests simulating multiple users
- Run with: `pytest tests/`

## Security Features

- Admin-only commands
- Environment variable configuration
- Database connection pooling
- Error handling and logging
- No sensitive data in logs

## Configuration

All configuration via environment variables:
- `BOT_TOKEN` - Telegram bot token
- `ADMIN_ID` - Admin user ID
- `DATABASE_URL` - PostgreSQL connection string
- `TZ` - Timezone (default: Asia/Phnom_Penh)
- `DEFAULT_FINE_AMOUNT` - Default fine (default: 20)
- `ATTENDANCE_WINDOW_START` - Window start (default: 09:00)
- `ATTENDANCE_WINDOW_END` - Window end (default: 10:00)
- `REPORT_TIME` - Report time (default: 10:05)

## Workflow

1. **09:00 AM** - Attendance window opens
2. **09:00-10:00 AM** - Members send "1" to record attendance
3. **10:00 AM** - Window closes, absent members marked and fined
4. **10:05 AM** - Daily report posted in group

## Future Enhancements

Potential improvements:
- Multiple group support
- Custom fine amounts per user
- Attendance statistics dashboard
- Email notifications
- Integration with payroll systems
- Mobile app companion

## License

MIT License

## Support

For issues:
1. Check logs: `docker-compose logs -f bot`
2. Review README.md
3. Check DEPLOYMENT.md for deployment issues

