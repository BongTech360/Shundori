"""
Configuration management for the bot.
"""
import os
from dotenv import load_dotenv
from datetime import time
import pytz

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/attendance_bot')

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
    """Get attendance window start time."""
    return parse_time(ATTENDANCE_WINDOW_START)


def get_window_end() -> time:
    """Get attendance window end time."""
    return parse_time(ATTENDANCE_WINDOW_END)


def get_report_time() -> time:
    """Get daily report time."""
    return parse_time(REPORT_TIME)

