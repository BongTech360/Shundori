"""
Scheduler for attendance window and daily reports.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
from config import TIMEZONE, get_window_start, get_window_end, get_report_time
from attendance import process_daily_attendance
from reports import generate_daily_report, format_daily_report_message
from database import get_db, Settings
import logging

logger = logging.getLogger(__name__)

# Global flag for attendance window
attendance_window_open = False

# Store group chat ID (set when bot starts)
group_chat_id = None

# Bot instance (set by bot.py)
bot_instance = None


def set_bot_instance(bot_app):
    """Set the bot application instance."""
    global bot_instance
    bot_instance = bot_app


def set_group_chat_id(chat_id: int):
    """Set the group chat ID for reports."""
    global group_chat_id
    group_chat_id = chat_id


def get_attendance_window_status() -> bool:
    """Get current attendance window status."""
    return attendance_window_open


def set_attendance_window_status(status: bool):
    """Set attendance window status."""
    global attendance_window_open
    attendance_window_open = status
    logger.info(f"Attendance window {'opened' if status else 'closed'}")


async def open_attendance_window():
    """Open attendance window at 09:00 AM."""
    set_attendance_window_status(True)
    logger.info("Attendance window opened at 09:00 AM")
    
    if group_chat_id and bot_instance:
        try:
            await bot_instance.bot.send_message(
                chat_id=group_chat_id,
                text="✅ Attendance window is now open! Send '1' to record your attendance."
            )
        except Exception as e:
            logger.error(f"Failed to send window open message: {e}")


async def close_attendance_window():
    """Close attendance window at 10:00 AM and process attendance."""
    set_attendance_window_status(False)
    logger.info("Attendance window closed at 10:00 AM")
    
    # Process attendance for all members
    process_daily_attendance()
    
    if group_chat_id and bot_instance:
        try:
            await bot_instance.bot.send_message(
                chat_id=group_chat_id,
                text="⏰ Attendance window is now closed. Processing attendance..."
            )
        except Exception as e:
            logger.error(f"Failed to send window close message: {e}")


async def send_daily_report():
    """Send daily report at 10:05 AM."""
    logger.info("Generating daily report")
    
    if not group_chat_id or not bot_instance:
        logger.warning("Group chat ID or bot instance not set, cannot send daily report")
        return
    
    try:
        report = generate_daily_report()
        message = format_daily_report_message(report, include_running_fines=False)
        
        await bot_instance.bot.send_message(
            chat_id=group_chat_id,
            text=message
        )
        
        logger.info("Daily report sent successfully")
    except Exception as e:
        logger.error(f"Failed to send daily report: {e}")


def setup_scheduler():
    """Setup and start the scheduler."""
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    
    # Get times
    window_start = get_window_start()
    window_end = get_window_end()
    report_time = get_report_time()
    
    # Schedule window opening
    scheduler.add_job(
        open_attendance_window,
        trigger=CronTrigger(
            hour=window_start.hour,
            minute=window_start.minute,
            timezone=TIMEZONE
        ),
        id='open_window',
        replace_existing=True
    )
    
    # Schedule window closing
    scheduler.add_job(
        close_attendance_window,
        trigger=CronTrigger(
            hour=window_end.hour,
            minute=window_end.minute,
            timezone=TIMEZONE
        ),
        id='close_window',
        replace_existing=True
    )
    
    # Schedule daily report
    scheduler.add_job(
        send_daily_report,
        trigger=CronTrigger(
            hour=report_time.hour,
            minute=report_time.minute,
            timezone=TIMEZONE
        ),
        id='daily_report',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started")
    
    return scheduler

