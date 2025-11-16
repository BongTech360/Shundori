"""
Unit tests for attendance tracking.
"""
import unittest
from datetime import datetime, date, time
from unittest.mock import Mock, patch, MagicMock
import pytz

from attendance import record_attendance, force_mark_attendance, get_or_create_user
from utils import is_attendance_window_open, is_before_deadline
from database import User, AttendanceRecord, Fine
from config import TIMEZONE


class TestAttendance(unittest.TestCase):
    """Test attendance tracking functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_telegram_id = 12345
        self.test_username = "testuser"
        self.test_full_name = "Test User"
    
    @patch('attendance.get_db')
    def test_record_attendance_success(self, mock_get_db):
        """Test successful attendance recording."""
        # Mock database session
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        mock_get_db.return_value.__exit__.return_value = None
        
        # Mock user query
        mock_user = Mock()
        mock_user.id = 1
        mock_user.telegram_id = self.test_telegram_id
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock get_or_create_user
        with patch('attendance.get_or_create_user') as mock_get_user:
            mock_get_user.return_value = mock_user
            
            # Mock window status
            with patch('attendance.is_attendance_window_open', return_value=True):
                with patch('attendance.is_before_deadline', return_value=True):
                    success, message = record_attendance(self.test_telegram_id)
                    
                    self.assertTrue(success)
                    self.assertIn("recorded", message.lower())
    
    @patch('attendance.get_db')
    def test_record_attendance_window_closed(self, mock_get_db):
        """Test attendance recording when window is closed."""
        with patch('attendance.is_attendance_window_open', return_value=False):
            success, message = record_attendance(self.test_telegram_id)
            
            self.assertFalse(success)
            self.assertIn("closed", message.lower())
    
    @patch('attendance.get_db')
    def test_record_attendance_already_recorded(self, mock_get_db):
        """Test attendance recording when already recorded."""
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        mock_get_db.return_value.__exit__.return_value = None
        
        # Mock existing record
        mock_record = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_record
        
        with patch('attendance.get_or_create_user') as mock_get_user:
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user
            
            with patch('attendance.is_attendance_window_open', return_value=True):
                success, message = record_attendance(self.test_telegram_id)
                
                self.assertFalse(success)
                self.assertIn("already", message.lower())


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_is_before_deadline(self):
        """Test deadline checking."""
        # Create a timestamp before 10:00 AM
        before_deadline = TIMEZONE.localize(datetime(2024, 1, 1, 9, 30, 0))
        self.assertTrue(is_before_deadline(before_deadline))
        
        # Create a timestamp after 10:00 AM
        after_deadline = TIMEZONE.localize(datetime(2024, 1, 1, 10, 30, 0))
        self.assertFalse(is_before_deadline(after_deadline))
        
        # Create a timestamp exactly at 10:00 AM
        at_deadline = TIMEZONE.localize(datetime(2024, 1, 1, 10, 0, 0))
        self.assertFalse(is_before_deadline(at_deadline))


if __name__ == '__main__':
    unittest.main()

