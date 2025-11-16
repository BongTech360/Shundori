/**
 * Report generation and CSV export functionality (Node.js)
 */
const { pool } = require('./database');
const { getPhnomPenhDate, config } = require('./config');
const { getFineAmount } = require('./attendance');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const fs = require('fs');
const path = require('path');

function formatUserName(user) {
  if (user.full_name) {
    return user.full_name;
  } else if (user.username) {
    return `@${user.username}`;
  } else {
    return `User ${user.telegram_id}`;
  }
}

async function generateDailyReport(reportDate = null) {
  if (!reportDate) {
    reportDate = getPhnomPenhDate();
  }

  const client = await pool.connect();
  try {
    // Get all active users
    const usersResult = await client.query('SELECT * FROM users WHERE is_active = TRUE');
    const users = usersResult.rows;

    const presentUsers = [];
    const absentUsers = [];
    const fineAmount = await getFineAmount();

    for (const user of users) {
      // Check attendance record for the date
      const recordResult = await client.query(
        'SELECT * FROM attendance_records WHERE user_id = $1 AND date = $2',
        [user.id, reportDate]
      );

      const record = recordResult.rows[0];

      if (record && record.status === 'present') {
        presentUsers.push({
          user: user,
          timestamp: record.timestamp
        });
      } else {
        // Check if fine was already recorded
        const fineResult = await client.query(
          'SELECT * FROM fines WHERE user_id = $1 AND date = $2',
          [user.id, reportDate]
        );

        const fine = fineResult.rows[0];
        absentUsers.push({
          user: user,
          fine: fine ? fine.amount : fineAmount
        });
      }
    }

    // Calculate running fines
    const runningFines = {};
    for (const user of users) {
      const finesResult = await client.query(
        'SELECT * FROM fines WHERE user_id = $1',
        [user.id]
      );
      runningFines[user.id] = finesResult.rows.reduce((sum, f) => sum + f.amount, 0);
    }

    return {
      date: reportDate,
      total_members: users.length,
      present: presentUsers,
      absent: absentUsers,
      running_fines: runningFines,
      all_users: users
    };
  } finally {
    client.release();
  }
}

function formatDailyReportMessage(report, includeRunningFines = false) {
  const dateStr = report.date;
  let message = `📊 Daily Attendance Report - ${dateStr}\n\n`;
  message += `👥 Total Members: ${report.total_members}\n\n`;

  // Present members
  message += '✅ Present Members:\n';
  if (report.present.length > 0) {
    for (const item of report.present) {
      const userName = formatUserName(item.user);
      const timestamp = item.timestamp
        ? new Date(item.timestamp).toLocaleTimeString('en-US', { hour12: false, timeZone: 'Asia/Phnom_Penh' })
        : 'N/A';
      message += `  • ${userName} (${timestamp})\n`;
    }
  } else {
    message += '  None\n';
  }

  message += '\n';

  // Absent/Late members
  message += '❌ Absent/Late Members:\n';
  if (report.absent.length > 0) {
    for (const item of report.absent) {
      const userName = formatUserName(item.user);
      const fine = item.fine;
      message += `  • ${userName} - Fine: $${fine.toFixed(2)}\n`;
    }
  } else {
    message += '  None\n';
  }

  if (includeRunningFines) {
    message += '\n💰 Running Fines:\n';
    for (const [userId, total] of Object.entries(report.running_fines)) {
      if (total > 0) {
        const user = report.all_users.find(u => u.id === parseInt(userId));
        if (user) {
          const userName = formatUserName(user);
          message += `  • ${userName}: $${total.toFixed(2)}\n`;
        }
      }
    }
  }

  return message;
}

async function exportDailyCSV(reportDate = null, outputDir = 'exports') {
  if (!reportDate) {
    reportDate = getPhnomPenhDate();
  }

  // Create exports directory
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const client = await pool.connect();
  try {
    const usersResult = await client.query('SELECT * FROM users WHERE is_active = TRUE');
    const users = usersResult.rows;
    const fineAmount = await getFineAmount();

    const records = [];
    for (const user of users) {
      const recordResult = await client.query(
        'SELECT * FROM attendance_records WHERE user_id = $1 AND date = $2',
        [user.id, reportDate]
      );

      const fineResult = await client.query(
        'SELECT * FROM fines WHERE user_id = $1 AND date = $2',
        [user.id, reportDate]
      );

      const record = recordResult.rows[0];
      const fine = fineResult.rows[0];

      records.push({
        Date: reportDate,
        'Telegram ID': user.telegram_id,
        Username: user.username || '',
        'Full Name': user.full_name || '',
        Status: record ? record.status : 'absent',
        Timestamp: record && record.timestamp
          ? new Date(record.timestamp).toISOString()
          : '',
        'Fine Amount': fine ? fine.amount : (record && record.status === 'present' ? 0 : fineAmount)
      });
    }

    const filename = `attendance_${reportDate.replace(/-/g, '')}.csv`;
    const filepath = path.join(outputDir, filename);

    const csvWriter = createCsvWriter({
      path: filepath,
      header: [
        { id: 'Date', title: 'Date' },
        { id: 'Telegram ID', title: 'Telegram ID' },
        { id: 'Username', title: 'Username' },
        { id: 'Full Name', title: 'Full Name' },
        { id: 'Status', title: 'Status' },
        { id: 'Timestamp', title: 'Timestamp' },
        { id: 'Fine Amount', title: 'Fine Amount' }
      ]
    });

    await csvWriter.writeRecords(records);
    return filepath;
  } finally {
    client.release();
  }
}

async function exportMonthlyCSV(year, month, outputDir = 'exports') {
  const { pool } = require('./database');
  const client = await pool.connect();

  try {
    // Create exports directory
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const startDate = `${year}-${month.toString().padStart(2, '0')}-01`;
    const lastDay = new Date(year, month, 0).getDate();
    const endDate = `${year}-${month.toString().padStart(2, '0')}-${lastDay}`;

    const usersResult = await client.query('SELECT * FROM users WHERE is_active = TRUE');
    const users = usersResult.rows;
    const fineAmount = await getFineAmount();

    const records = [];
    for (const user of users) {
      // Get all attendance records for the month
      const attendanceResult = await client.query(
        'SELECT * FROM attendance_records WHERE user_id = $1 AND date >= $2 AND date <= $3',
        [user.id, startDate, endDate]
      );

      // Get all fines for the month
      const finesResult = await client.query(
        'SELECT * FROM fines WHERE user_id = $1 AND date >= $2 AND date <= $3',
        [user.id, startDate, endDate]
      );

      // Create a set of dates with attendance
      const presentDates = new Set();
      attendanceResult.rows.forEach(r => {
        if (r.status === 'present') {
          presentDates.add(r.date.toISOString().split('T')[0]);
        }
      });

      // Calculate totals
      const totalPresent = presentDates.size;
      const totalDays = lastDay;
      const totalAbsent = totalDays - totalPresent;
      const totalFines = finesResult.rows.reduce((sum, f) => sum + f.amount, 0);

      records.push({
        'Telegram ID': user.telegram_id,
        Username: user.username || '',
        'Full Name': user.full_name || '',
        'Total Present': totalPresent,
        'Total Absent': totalAbsent,
        'Total Fines': totalFines
      });
    }

    const filename = `attendance_${year}_${month.toString().padStart(2, '0')}.csv`;
    const filepath = path.join(outputDir, filename);

    const csvWriter = createCsvWriter({
      path: filepath,
      header: [
        { id: 'Telegram ID', title: 'Telegram ID' },
        { id: 'Username', title: 'Username' },
        { id: 'Full Name', title: 'Full Name' },
        { id: 'Total Present', title: 'Total Present' },
        { id: 'Total Absent', title: 'Total Absent' },
        { id: 'Total Fines', title: 'Total Fines' }
      ]
    });

    await csvWriter.writeRecords(records);
    return filepath;
  } finally {
    client.release();
  }
}

module.exports = {
  generateDailyReport,
  formatDailyReportMessage,
  exportDailyCSV,
  exportMonthlyCSV,
  formatUserName
};

