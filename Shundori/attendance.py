"""
Attendance tracking logic.
"""
from datetime import datetime, date
from typing import Optional
from database import get_db, User, AttendanceRecord, Fine, Settings
from utils import get_phnom_penh_now, get_phnom_penh_date, is_before_deadline, is_attendance_window_open
from config import DEFAULT_FINE_AMOUNT
from reports import get_fine_amount


def get_or_create_user(telegram_id: int, username: str = None, full_name: str = None) -> User:
    """Get or create a user in the database."""
    with get_db() as db:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update user info if provided
            updated = False
            if username and user.username != username:
                user.username = username
                updated = True
            if full_name and user.full_name != full_name:
                user.full_name = full_name
                updated = True
            if updated:
                db.commit()
        return user


def record_attendance(telegram_id: int, timestamp: datetime = None, username: str = None, full_name: str = None) -> tuple[bool, str]:
    """
    Record attendance for a user.
    Returns (success, message)
    """
    if timestamp is None:
        timestamp = get_phnom_penh_now()
    
    # Check if window is open
    if not is_attendance_window_open():
        return False, "Attendance window is closed. Please send '1' between 09:00 and 10:00 AM."
    
    current_date = get_phnom_penh_date()
    
    # Get or create user first (outside transaction to avoid nested contexts)
    user = get_or_create_user(telegram_id, username=username, full_name=full_name)
    
    with get_db() as db:
        # Check if already recorded for today
        existing = db.query(AttendanceRecord).filter(
            AttendanceRecord.user_id == user.id,
            AttendanceRecord.date == current_date
        ).first()
        
        if existing:
            return False, "You have already recorded your attendance for today."
        
        # Check if before deadline
        is_on_time = is_before_deadline(timestamp)
        status = 'present' if is_on_time else 'late'
        
        # Create attendance record
        record = AttendanceRecord(
            user_id=user.id,
            date=current_date,
            status=status,
            timestamp=timestamp
        )
        db.add(record)
        
        # If late, create fine
        if not is_on_time:
            fine_amount = get_fine_amount()
            fine = Fine(
                user_id=user.id,
                date=current_date,
                amount=fine_amount
            )
            db.add(fine)
        
        db.commit()
        
        if is_on_time:
            return True, "Good morning! Attendance recorded."
        else:
            return True, "Attendance recorded, but you were late. A fine has been applied."


def process_daily_attendance():
    """
    Process attendance for all members at 10:00 AM.
    Mark absent members and apply fines.
    """
    current_date = get_phnom_penh_date()
    fine_amount = get_fine_amount()
    
    with get_db() as db:
        # Get all active users
        users = db.query(User).filter(User.is_active == True).all()
        
        for user in users:
            # Check if user has attendance record for today
            record = db.query(AttendanceRecord).filter(
                AttendanceRecord.user_id == user.id,
                AttendanceRecord.date == current_date
            ).first()
            
            if not record:
                # Mark as absent
                record = AttendanceRecord(
                    user_id=user.id,
                    date=current_date,
                    status='absent',
                    timestamp=None
                )
                db.add(record)
                
                # Apply fine
                fine = Fine(
                    user_id=user.id,
                    date=current_date,
                    amount=fine_amount
                )
                db.add(fine)
        
        db.commit()


def force_mark_attendance(telegram_id: int, status: str, target_date: date = None) -> bool:
    """
    Force mark attendance for a user (admin only).
    status: 'present' or 'absent'
    """
    if target_date is None:
        target_date = get_phnom_penh_date()
    
    with get_db() as db:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            return False
        
        # Remove existing record and fine
        existing_record = db.query(AttendanceRecord).filter(
            AttendanceRecord.user_id == user.id,
            AttendanceRecord.date == target_date
        ).first()
        
        existing_fine = db.query(Fine).filter(
            Fine.user_id == user.id,
            Fine.date == target_date
        ).first()
        
        if existing_record:
            db.delete(existing_record)
        if existing_fine:
            db.delete(existing_fine)
        
        # Create new record
        if status == 'present':
            record = AttendanceRecord(
                user_id=user.id,
                date=target_date,
                status='present',
                timestamp=get_phnom_penh_now()
            )
            db.add(record)
        elif status == 'absent':
            record = AttendanceRecord(
                user_id=user.id,
                date=target_date,
                status='absent',
                timestamp=None
            )
            db.add(record)
            
            # Apply fine
            fine_amount = get_fine_amount()
            fine = Fine(
                user_id=user.id,
                date=target_date,
                amount=fine_amount
            )
            db.add(fine)
        
        db.commit()
        return True

