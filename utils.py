"""
Utility functions for the attendance bot.
"""
from datetime import datetime, date, time
from typing import Optional
import pytz
from config import TIMEZONE, get_window_start, get_window_end


def get_phnom_penh_now() -> datetime:
    """Get current datetime in Phnom Penh timezone."""
    return datetime.now(TIMEZONE)


def get_phnom_penh_date() -> date:
    """Get current date in Phnom Penh timezone."""
    return get_phnom_penh_now().date()


def get_phnom_penh_time() -> time:
    """Get current time in Phnom_penh timezone."""
    return get_phnom_penh_now().time()


def is_attendance_window_open() -> bool:
    """Check if attendance window is currently open."""
    # Check scheduler flag (primary source - set by scheduler)
    try:
        from scheduler import get_attendance_window_status
        scheduler_flag = get_attendance_window_status()
    except (ImportError, AttributeError):
        # Fallback to time check if scheduler not available
        scheduler_flag = None
    
    # Also check actual time as validation/fallback
    now = get_phnom_penh_time()
    window_start = get_window_start()
    window_end = get_window_end()
    time_check = window_start <= now < window_end
    
    # If scheduler flag is available, use it; otherwise use time check
    if scheduler_flag is not None:
        # Window is open if scheduler says so AND we're in the time window
        return scheduler_flag and time_check
    else:
        # Fallback to time check only
        return time_check


def is_before_deadline(timestamp: Optional[datetime] = None) -> bool:
    """Check if timestamp is before 10:00 AM Phnom Penh time."""
    if timestamp is None:
        timestamp = get_phnom_penh_now()
    
    # Ensure timestamp is timezone-aware
    if timestamp.tzinfo is None:
        timestamp = TIMEZONE.localize(timestamp)
    else:
        timestamp = timestamp.astimezone(TIMEZONE)
    
    deadline = timestamp.replace(hour=10, minute=0, second=0, microsecond=0)
    return timestamp < deadline


def format_user_name(user) -> str:
    """Format user name for display."""
    if user.full_name:
        return user.full_name
    elif user.username:
        return f"@{user.username}"
    else:
        return f"User {user.telegram_id}"

