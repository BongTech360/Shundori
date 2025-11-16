"""
Configuration management for the bot.
"""
import os
from dotenv import load_dotenv
from datetime import time
import pytz

# Load environment variables from .env file if it exists
# This won't override existing environment variables (good for Docker/cloud)
load_dotenv(override=False)

# Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')
try:
    ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
except (ValueError, TypeError):
    ADMIN_ID = 0

# Database
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'BongTech_db')

# Timezone
TIMEZONE = pytz.timezone(os.getenv('TZ', 'Asia/Phnom_Penh'))

# Fine Configuration
DEFAULT_FINE_AMOUNT = float(os.getenv('DEFAULT_FINE_AMOUNT', '20'))

# Attendance Window
ATTENDANCE_WINDOW_START = os.getenv('ATTENDANCE_WINDOW_START', '09:00')
ATTENDANCE_WINDOW_END = os.getenv('ATTENDANCE_WINDOW_END', '10:00')

# Report Time
REPORT_TIME = os.getenv('REPORT_TIME', '10:05')


def parse_time(time_str: str) -> time:
    """Parse time string (HH:MM) to time object."""
    hour, minute = map(int, time_str.split(':'))
    return time(hour, minute)


def get_window_start() -> time:
    """Get attendance window start time from database or config."""
    try:
        from database import get_db, Settings
        with get_db() as db:
            setting = db.query(Settings).filter(Settings.key == 'window_start').first()
            if setting:
                return parse_time(setting.value)
    except Exception:
        pass
    return parse_time(ATTENDANCE_WINDOW_START)


def get_window_end() -> time:
    """Get attendance window end time from database or config."""
    try:
        from database import get_db, Settings
        with get_db() as db:
            setting = db.query(Settings).filter(Settings.key == 'window_end').first()
            if setting:
                return parse_time(setting.value)
    except Exception:
        pass
    return parse_time(ATTENDANCE_WINDOW_END)


def get_report_time() -> time:
    """Get daily report time from database or config."""
    try:
        from database import get_db, Settings
        with get_db() as db:
            setting = db.query(Settings).filter(Settings.key == 'report_time').first()
            if setting:
                return parse_time(setting.value)
    except Exception:
        pass
    return parse_time(REPORT_TIME)

