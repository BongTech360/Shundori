/**
 * Attendance tracking logic
 */
const { pool } = require('./database');
const { getPhnomPenhNow, getPhnomPenhDate, isBeforeDeadline, isAttendanceWindowOpen, config } = require('./config');

async function getOrCreateUser(telegramId, username = null, fullName = null) {
  const client = await pool.connect();
  try {
    let result = await client.query(
      'SELECT * FROM users WHERE telegram_id = $1',
      [telegramId]
    );

    if (result.rows.length === 0) {
      result = await client.query(
        'INSERT INTO users (telegram_id, username, full_name) VALUES ($1, $2, $3) RETURNING *',
        [telegramId, username, fullName]
      );
    } else {
      // Update user info if provided
      if (username || fullName) {
        result = await client.query(
          'UPDATE users SET username = COALESCE($2, username), full_name = COALESCE($3, full_name) WHERE telegram_id = $1 RETURNING *',
          [telegramId, username, fullName]
        );
      }
    }
    return result.rows[0];
  } finally {
    client.release();
  }
}

async function getFineAmount() {
  const client = await pool.connect();
  try {
    const result = await client.query(
      'SELECT value FROM settings WHERE key = $1',
      ['fine_amount']
    );
    if (result.rows.length > 0) {
      return parseFloat(result.rows[0].value);
    }
    return config.DEFAULT_FINE_AMOUNT;
  } finally {
    client.release();
  }
}

async function recordAttendance(telegramId, timestamp = null, username = null, fullName = null) {
  if (!timestamp) {
    timestamp = getPhnomPenhNow().toDate();
  } else if (typeof timestamp === 'number') {
    // Convert Unix timestamp (milliseconds) to Date
    timestamp = new Date(timestamp);
  }

  // Check if window is open
  if (!isAttendanceWindowOpen()) {
    return { success: false, message: 'Attendance window is closed. Please send \'1\' between 09:00 and 10:00 AM.' };
  }

  const currentDate = getPhnomPenhDate();
  const client = await pool.connect();

  try {
    await client.query('BEGIN');

    // Get or create user
    const user = await getOrCreateUser(telegramId, username, fullName);

    // Check if already recorded for today
    const existing = await client.query(
      'SELECT * FROM attendance_records WHERE user_id = $1 AND date = $2',
      [user.id, currentDate]
    );

    if (existing.rows.length > 0) {
      await client.query('ROLLBACK');
      return { success: false, message: 'You have already recorded your attendance for today.' };
    }

    // Check if before deadline
    const isOnTime = isBeforeDeadline(timestamp);
    const status = isOnTime ? 'present' : 'late';

    // Create attendance record
    await client.query(
      'INSERT INTO attendance_records (user_id, date, status, timestamp) VALUES ($1, $2, $3, $4)',
      [user.id, currentDate, status, timestamp]
    );

    // If late, create fine
    if (!isOnTime) {
      const fineAmount = await getFineAmount();
      await client.query(
        'INSERT INTO fines (user_id, date, amount) VALUES ($1, $2, $3)',
        [user.id, currentDate, fineAmount]
      );
    }

    await client.query('COMMIT');

    if (isOnTime) {
      return { success: true, message: 'Good morning! Attendance recorded.' };
    } else {
      return { success: true, message: 'Attendance recorded, but you were late. A fine has been applied.' };
    }
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

async function processDailyAttendance() {
  const currentDate = getPhnomPenhDate();
  const fineAmount = await getFineAmount();
  const client = await pool.connect();

  try {
    await client.query('BEGIN');

    // Get all active users
    const users = await client.query('SELECT * FROM users WHERE is_active = TRUE');

    for (const user of users.rows) {
      // Check if user has attendance record for today
      const record = await client.query(
        'SELECT * FROM attendance_records WHERE user_id = $1 AND date = $2',
        [user.id, currentDate]
      );

      if (record.rows.length === 0) {
        // Mark as absent
        await client.query(
          'INSERT INTO attendance_records (user_id, date, status, timestamp) VALUES ($1, $2, $3, NULL)',
          [user.id, currentDate, 'absent']
        );

        // Apply fine
        await client.query(
          'INSERT INTO fines (user_id, date, amount) VALUES ($1, $2, $3)',
          [user.id, currentDate, fineAmount]
        );
      }
    }

    await client.query('COMMIT');
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

async function forceMarkAttendance(telegramId, status, targetDate = null) {
  if (!targetDate) {
    targetDate = getPhnomPenhDate();
  }

  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const userResult = await client.query('SELECT * FROM users WHERE telegram_id = $1', [telegramId]);
    if (userResult.rows.length === 0) {
      await client.query('ROLLBACK');
      return false;
    }

    const user = userResult.rows[0];

    // Remove existing record and fine
    await client.query('DELETE FROM attendance_records WHERE user_id = $1 AND date = $2', [user.id, targetDate]);
    await client.query('DELETE FROM fines WHERE user_id = $1 AND date = $2', [user.id, targetDate]);

    // Create new record
    if (status === 'present') {
      await client.query(
        'INSERT INTO attendance_records (user_id, date, status, timestamp) VALUES ($1, $2, $3, $4)',
        [user.id, targetDate, 'present', getPhnomPenhNow().toDate()]
      );
    } else if (status === 'absent') {
      await client.query(
        'INSERT INTO attendance_records (user_id, date, status, timestamp) VALUES ($1, $2, $3, NULL)',
        [user.id, targetDate, 'absent']
      );

      // Apply fine
      const fineAmount = await getFineAmount();
      await client.query(
        'INSERT INTO fines (user_id, date, amount) VALUES ($1, $2, $3)',
        [user.id, targetDate, fineAmount]
      );
    }

    await client.query('COMMIT');
    return true;
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

module.exports = {
  getOrCreateUser,
  recordAttendance,
  processDailyAttendance,
  forceMarkAttendance,
  getFineAmount
};

