"""
Integration tests for the attendance bot.
Simulates multiple users sending "1" at different times.
"""
import unittest
from datetime import datetime, date, time
from unittest.mock import Mock, patch, MagicMock
import pytz

from config import TIMEZONE
from attendance import record_attendance, process_daily_attendance
from database import User, AttendanceRecord, Fine


class TestIntegration(unittest.TestCase):
    """Integration tests simulating real-world scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_date = date(2024, 1, 15)
        self.users = [
            {'telegram_id': 1001, 'username': 'user1', 'full_name': 'User One'},
            {'telegram_id': 1002, 'username': 'user2', 'full_name': 'User Two'},
            {'telegram_id': 1003, 'username': 'user3', 'full_name': 'User Three'},
        ]
    
    @patch('attendance.get_db')
    def test_multiple_users_attendance(self, mock_get_db):
        """Test multiple users sending attendance at different times."""
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        mock_get_db.return_value.__exit__.return_value = None
        
        # Mock user creation
        user_objects = []
        for i, user_data in enumerate(self.users):
            mock_user = Mock()
            mock_user.id = i + 1
            mock_user.telegram_id = user_data['telegram_id']
            mock_user.username = user_data['username']
            mock_user.full_name = user_data['full_name']
            user_objects.append(mock_user)
        
        with patch('attendance.get_or_create_user') as mock_get_user:
            def get_user_side_effect(telegram_id, **kwargs):
                return next(u for u in user_objects if u.telegram_id == telegram_id)
            
            mock_get_user.side_effect = get_user_side_effect
            
            # Mock no existing records
            mock_db.query.return_value.filter.return_value.first.return_value = None
            
            # Simulate user 1 sending "1" at 9:30 AM (on time)
            with patch('attendance.is_attendance_window_open', return_value=True):
                with patch('attendance.is_before_deadline', return_value=True):
                    success1, msg1 = record_attendance(
                        self.users[0]['telegram_id'],
                        TIMEZONE.localize(datetime(2024, 1, 15, 9, 30, 0))
                    )
                    self.assertTrue(success1)
            
            # Simulate user 2 sending "1" at 9:45 AM (on time)
            with patch('attendance.is_attendance_window_open', return_value=True):
                with patch('attendance.is_before_deadline', return_value=True):
                    success2, msg2 = record_attendance(
                        self.users[1]['telegram_id'],
                        TIMEZONE.localize(datetime(2024, 1, 15, 9, 45, 0))
                    )
                    self.assertTrue(success2)
            
            # Simulate user 3 sending "1" at 10:15 AM (late, window closed)
            with patch('attendance.is_attendance_window_open', return_value=False):
                success3, msg3 = record_attendance(
                    self.users[2]['telegram_id'],
                    TIMEZONE.localize(datetime(2024, 1, 15, 10, 15, 0))
                )
                self.assertFalse(success3)
    
    @patch('attendance.get_db')
    def test_process_daily_attendance(self, mock_get_db):
        """Test processing attendance for all members."""
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        mock_get_db.return_value.__exit__.return_value = None
        
        # Mock active users
        mock_users = []
        for i, user_data in enumerate(self.users):
            mock_user = Mock()
            mock_user.id = i + 1
            mock_user.telegram_id = user_data['telegram_id']
            mock_users.append(mock_user)
        
        mock_db.query.return_value.filter.return_value.all.return_value = mock_users
        
        # Mock no existing records (all absent)
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with patch('attendance.get_fine_amount', return_value=20.0):
            process_daily_attendance()
            
            # Verify that records and fines were created
            self.assertTrue(mock_db.add.called)
            self.assertTrue(mock_db.commit.called)


if __name__ == '__main__':
    unittest.main()

