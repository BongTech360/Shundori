"""
Report generation and CSV export functionality.
"""
from datetime import date
from typing import Dict
import pandas as pd
import os
from database import get_db, User, AttendanceRecord, Fine, Settings
from utils import format_user_name, get_phnom_penh_date
from config import DEFAULT_FINE_AMOUNT


def get_fine_amount() -> float:
    """Get current fine amount from settings."""
    with get_db() as db:
        setting = db.query(Settings).filter(Settings.key == 'fine_amount').first()
        if setting:
            return float(setting.value)
    return DEFAULT_FINE_AMOUNT


def generate_daily_report(report_date: date = None) -> Dict:
    """Generate daily attendance report."""
    if report_date is None:
        report_date = get_phnom_penh_date()
    
    with get_db() as db:
        # Get all active users
        users = db.query(User).filter(User.is_active == True).all()
        
        present_users = []
        absent_users = []
        fine_amount = get_fine_amount()
        
        for user in users:
            # Check attendance record for the date
            record = db.query(AttendanceRecord).filter(
                AttendanceRecord.user_id == user.id,
                AttendanceRecord.date == report_date
            ).first()
            
            if record and record.status == 'present':
                present_users.append({
                    'user': user,
                    'timestamp': record.timestamp
                })
            else:
                # Check if fine was already recorded
                fine = db.query(Fine).filter(
                    Fine.user_id == user.id,
                    Fine.date == report_date
                ).first()
                
                fine_amount_for_user = fine_amount
                if fine:
                    fine_amount_for_user = fine.amount
                elif record and record.status == 'late':
                    # Late users also get fined
                    fine_amount_for_user = fine_amount
                
                absent_users.append({
                    'user': user,
                    'fine': fine_amount_for_user
                })
        
        # Calculate running fines
        running_fines = {}
        for user in users:
            total_fines = db.query(Fine).filter(Fine.user_id == user.id).all()
            running_fines[user.id] = sum(f.amount for f in total_fines)
        
        return {
            'date': report_date,
            'total_members': len(users),
            'present': present_users,
            'absent': absent_users,
            'running_fines': running_fines,
            'all_users': users
        }


def format_daily_report_message(report: Dict, include_running_fines: bool = False) -> str:
    """Format daily report as a message."""
    date_str = report['date'].strftime('%Y-%m-%d')
    message = f"📊 Daily Attendance Report - {date_str}\n\n"
    message += f"👥 Total Members: {report['total_members']}\n\n"
    
    # Present members
    message += "✅ Present Members:\n"
    if report['present']:
        for item in report['present']:
            user_name = format_user_name(item['user'])
            timestamp_str = 'N/A'
            if item.get('timestamp'):
                try:
                    timestamp_str = item['timestamp'].strftime('%H:%M:%S')
                except (AttributeError, TypeError):
                    timestamp_str = 'N/A'
            message += f"  • {user_name} ({timestamp_str})\n"
    else:
        message += "  None\n"
    
    message += "\n"
    
    # Absent/Late members
    message += "❌ Absent/Late Members:\n"
    if report['absent']:
        for item in report['absent']:
            user_name = format_user_name(item['user'])
            fine = item['fine']
            message += f"  • {user_name} - Fine: ${fine:.2f}\n"
    else:
        message += "  None\n"
    
    if include_running_fines:
        message += "\n💰 Running Fines:\n"
        for user_id, total in report['running_fines'].items():
            if total > 0:
                # Find user
                user = next((u for u in report.get('all_users', []) if u.id == user_id), None)
                if user:
                    user_name = format_user_name(user)
                    message += f"  • {user_name}: ${total:.2f}\n"
    
    return message


def export_daily_csv(report_date: date = None, output_dir: str = 'exports') -> str:
    """Export daily report to CSV file."""
    if report_date is None:
        report_date = get_phnom_penh_date()
    
    os.makedirs(output_dir, exist_ok=True)
    
    with get_db() as db:
        users = db.query(User).filter(User.is_active == True).all()
        fine_amount = get_fine_amount()
        
        records = []
        for user in users:
            record = db.query(AttendanceRecord).filter(
                AttendanceRecord.user_id == user.id,
                AttendanceRecord.date == report_date
            ).first()
            
            fine = db.query(Fine).filter(
                Fine.user_id == user.id,
                Fine.date == report_date
            ).first()
            
            records.append({
                'Date': report_date.strftime('%Y-%m-%d'),
                'Telegram ID': user.telegram_id,
                'Username': user.username or '',
                'Full Name': user.full_name or '',
                'Status': record.status if record else 'absent',
                'Timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S') if record and record.timestamp else '',
                'Fine Amount': fine.amount if fine else (fine_amount if not record or record.status != 'present' else 0)
            })
    
    df = pd.DataFrame(records)
    filename = f"attendance_{report_date.strftime('%Y%m%d')}.csv"
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False)
    
    return filepath


def export_monthly_csv(year: int, month: int, output_dir: str = 'exports') -> str:
    """Export monthly report to CSV file."""
    from calendar import monthrange
    
    os.makedirs(output_dir, exist_ok=True)
    
    start_date = date(year, month, 1)
    end_date = date(year, month, monthrange(year, month)[1])
    
    with get_db() as db:
        users = db.query(User).filter(User.is_active == True).all()
        fine_amount = get_fine_amount()
        
        records = []
        for user in users:
            # Get all attendance records for the month
            attendance_records = db.query(AttendanceRecord).filter(
                AttendanceRecord.user_id == user.id,
                AttendanceRecord.date >= start_date,
                AttendanceRecord.date <= end_date
            ).all()
            
            # Get all fines for the month
            fines = db.query(Fine).filter(
                Fine.user_id == user.id,
                Fine.date >= start_date,
                Fine.date <= end_date
            ).all()
            
            # Create a set of dates with attendance
            present_dates = {r.date for r in attendance_records if r.status == 'present'}
            
            # Calculate totals
            total_present = len(present_dates)
            total_absent = (end_date - start_date).days + 1 - total_present
            total_fines = sum(f.amount for f in fines)
            
            records.append({
                'Telegram ID': user.telegram_id,
                'Username': user.username or '',
                'Full Name': user.full_name or '',
                'Total Present': total_present,
                'Total Absent': total_absent,
                'Total Fines': total_fines
            })
    
    df = pd.DataFrame(records)
    filename = f"attendance_{year:04d}_{month:02d}.csv"
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False)
    
    return filepath

