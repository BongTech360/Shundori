"""
Unit tests for report generation.
"""
import unittest
from datetime import date
from unittest.mock import Mock, patch, MagicMock

from reports import generate_daily_report, format_daily_report_message, get_fine_amount
from database import User, AttendanceRecord, Fine


class TestReports(unittest.TestCase):
    """Test report generation functionality."""
    
    @patch('reports.get_db')
    def test_generate_daily_report(self, mock_get_db):
        """Test daily report generation."""
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        mock_get_db.return_value.__exit__.return_value = None
        
        # Mock users
        mock_user1 = Mock()
        mock_user1.id = 1
        mock_user1.telegram_id = 12345
        mock_user1.username = "user1"
        mock_user1.full_name = "User One"
        
        mock_user2 = Mock()
        mock_user2.id = 2
        mock_user2.telegram_id = 67890
        mock_user2.username = "user2"
        mock_user2.full_name = "User Two"
        
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_user1, mock_user2]
        
        # Mock attendance records
        mock_record = Mock()
        mock_record.status = 'present'
        mock_record.timestamp = None
        
        def mock_query_filter_first(user_id=None, date=None):
            if user_id == 1:
                return mock_record
            return None
        
        mock_db.query.return_value.filter.return_value.first.side_effect = mock_query_filter_first
        
        # Mock fine query
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with patch('reports.get_fine_amount', return_value=20.0):
            report = generate_daily_report(date(2024, 1, 1))
            
            self.assertEqual(report['total_members'], 2)
            self.assertEqual(len(report['present']), 1)
            self.assertEqual(len(report['absent']), 1)
    
    def test_format_daily_report_message(self):
        """Test report message formatting."""
        report = {
            'date': date(2024, 1, 1),
            'total_members': 2,
            'present': [
                {
                    'user': Mock(telegram_id=12345, username="user1", full_name="User One"),
                    'timestamp': None
                }
            ],
            'absent': [
                {
                    'user': Mock(telegram_id=67890, username="user2", full_name="User Two"),
                    'fine': 20.0
                }
            ],
            'running_fines': {}
        }
        
        message = format_daily_report_message(report)
        
        self.assertIn("Daily Attendance Report", message)
        self.assertIn("Total Members: 2", message)
        self.assertIn("Present Members", message)
        self.assertIn("Absent/Late Members", message)


if __name__ == '__main__':
    unittest.main()

