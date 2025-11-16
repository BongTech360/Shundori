"""
Main Telegram bot implementation.
"""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.error import TelegramError
from datetime import datetime, date
import os
from dotenv import load_dotenv

from config import BOT_TOKEN, ADMIN_ID
from attendance import get_or_create_user, record_attendance, force_mark_attendance
from reports import (
    generate_daily_report,
    format_daily_report_message,
    export_daily_csv,
    export_monthly_csv
)
from scheduler import get_attendance_window_status, set_group_chat_id
from database import get_db, Settings
from utils import format_user_name, get_phnom_penh_date
from reports import get_fine_amount

load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global bot instance (for scheduler)
bot_instance = None


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id == ADMIN_ID


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "Hello! I'm the attendance bot. "
        "Send '1' in the group chat between 09:00 and 10:00 AM to record your attendance."
    )


async def handle_attendance_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle '1' message for attendance."""
    # Only process in group chats
    if update.message.chat.type not in ['group', 'supergroup']:
        return
    
    # Store group chat ID
    set_group_chat_id(update.message.chat.id)
    
    # Check if message is exactly "1"
    if update.message.text.strip() != '1':
        return
    
    # Check if window is open
    if not get_attendance_window_status():
        await update.message.reply_text(
            "⏰ Attendance window is closed. Please send '1' between 09:00 and 10:00 AM."
        )
        return
    
    user = update.effective_user
    telegram_id = user.id
    username = user.username
    full_name = user.full_name or f"{user.first_name} {user.last_name or ''}".strip()
    
    # Record attendance
    success, message = record_attendance(
        telegram_id, 
        update.message.date,
        username=username,
        full_name=full_name
    )
    
    if success:
        # Send greeting in private chat
        try:
            await context.bot.send_message(
                chat_id=telegram_id,
                text=f"Good morning, {full_name}! {message}"
            )
        except TelegramError as e:
            logger.warning(f"Could not send private message to {telegram_id}: {e}")
            # Still record attendance, just notify admin
            if is_admin(ADMIN_ID):
                try:
                    await context.bot.send_message(
                        chat_id=ADMIN_ID,
                        text=f"⚠️ Could not send greeting to {full_name} (ID: {telegram_id}). Attendance still recorded."
                    )
                except:
                    pass
    else:
        await update.message.reply_text(message)


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /report command."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    # Parse date from command
    report_date = get_phnom_penh_date()
    if context.args:
        try:
            report_date = datetime.strptime(context.args[0], '%Y-%m-%d').date()
        except ValueError:
            await update.message.reply_text("❌ Invalid date format. Use YYYY-MM-DD")
            return
    
    report = generate_daily_report(report_date)
    message = format_daily_report_message(report, include_running_fines=True)
    
    await update.message.reply_text(message)


async def monthly_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /monthly command."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    # Parse month from command
    if not context.args:
        await update.message.reply_text("❌ Please provide month in YYYY-MM format.")
        return
    
    try:
        year, month = map(int, context.args[0].split('-'))
    except ValueError:
        await update.message.reply_text("❌ Invalid date format. Use YYYY-MM")
        return
    
    try:
        filepath = export_monthly_csv(year, month)
        with open(filepath, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=os.path.basename(filepath),
                caption=f"Monthly report for {year}-{month:02d}"
            )
    except Exception as e:
        logger.error(f"Error generating monthly report: {e}")
        await update.message.reply_text(f"❌ Error generating report: {str(e)}")


async def setfine_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setfine command."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Please provide fine amount. Usage: /setfine <amount>")
        return
    
    try:
        amount = float(context.args[0])
        if amount < 0:
            raise ValueError("Fine amount must be positive")
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Please provide a positive number.")
        return
    
    with get_db() as db:
        setting = db.query(Settings).filter(Settings.key == 'fine_amount').first()
        if setting:
            setting.value = str(amount)
        else:
            setting = Settings(key='fine_amount', value=str(amount))
            db.add(setting)
        db.commit()
    
    await update.message.reply_text(f"✅ Fine amount set to ${amount:.2f}")


async def set_window_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /set-window command."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: /set-window <HH:MM> <HH:MM>")
        return
    
    try:
        start_time = datetime.strptime(context.args[0], '%H:%M').time()
        end_time = datetime.strptime(context.args[1], '%H:%M').time()
    except ValueError:
        await update.message.reply_text("❌ Invalid time format. Use HH:MM")
        return
    
    with get_db() as db:
        # Store in settings
        start_setting = db.query(Settings).filter(Settings.key == 'window_start').first()
        if start_setting:
            start_setting.value = context.args[0]
        else:
            start_setting = Settings(key='window_start', value=context.args[0])
            db.add(start_setting)
        
        end_setting = db.query(Settings).filter(Settings.key == 'window_end').first()
        if end_setting:
            end_setting.value = context.args[1]
        else:
            end_setting = Settings(key='window_end', value=context.args[1])
            db.add(end_setting)
        
        db.commit()
    
    await update.message.reply_text(
        f"✅ Attendance window set to {context.args[0]} - {context.args[1]}"
    )


async def force_mark_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /force-mark command."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: /force-mark <user_id> present|absent")
        return
    
    try:
        user_id = int(context.args[0])
        status = context.args[1].lower()
        
        if status not in ['present', 'absent']:
            raise ValueError("Status must be 'present' or 'absent'")
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Invalid arguments. Usage: /force-mark <user_id> present|absent")
        return
    
    success = force_mark_attendance(user_id, status)
    
    if success:
        await update.message.reply_text(f"✅ Attendance marked as {status} for user {user_id}")
    else:
        await update.message.reply_text(f"❌ User {user_id} not found")


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /export command."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    # Parse date from command
    export_date = get_phnom_penh_date()
    if context.args:
        try:
            export_date = datetime.strptime(context.args[0], '%Y-%m-%d').date()
        except ValueError:
            await update.message.reply_text("❌ Invalid date format. Use YYYY-MM-DD")
            return
    
    try:
        filepath = export_daily_csv(export_date)
        with open(filepath, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=os.path.basename(filepath),
                caption=f"Daily attendance report for {export_date}"
            )
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        await update.message.reply_text(f"❌ Error exporting CSV: {str(e)}")


def setup_handlers(application: Application):
    """Setup bot handlers."""
    # Commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("report", report_command))
    application.add_handler(CommandHandler("monthly", monthly_command))
    application.add_handler(CommandHandler("setfine", setfine_command))
    application.add_handler(CommandHandler("set-window", set_window_command))
    application.add_handler(CommandHandler("force-mark", force_mark_command))
    application.add_handler(CommandHandler("export", export_command))
    
    # Message handler for attendance
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex(r'^1$'), handle_attendance_message)
    )


async def post_init(application: Application):
    """Post-initialization tasks."""
    global bot_instance
    bot_instance = application
    
    # Initialize database
    from database import init_db
    init_db()
    
    # Setup scheduler
    from scheduler import setup_scheduler, set_bot_instance
    set_bot_instance(application)
    scheduler = setup_scheduler()
    
    logger.info("Bot initialized successfully")


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
    
    # Run bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

