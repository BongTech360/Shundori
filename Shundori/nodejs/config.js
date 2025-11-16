/**
 * Configuration management
 */
require('dotenv').config();
const moment = require('moment-timezone');

const config = {
  BOT_TOKEN: process.env.BOT_TOKEN,
  ADMIN_ID: parseInt(process.env.ADMIN_ID || '0'),
  DATABASE_URL: process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/attendance_bot',
  TIMEZONE: 'Asia/Phnom_Penh',
  DEFAULT_FINE_AMOUNT: parseFloat(process.env.DEFAULT_FINE_AMOUNT || '20'),
  ATTENDANCE_WINDOW_START: process.env.ATTENDANCE_WINDOW_START || '09:00',
  ATTENDANCE_WINDOW_END: process.env.ATTENDANCE_WINDOW_END || '10:00',
  REPORT_TIME: process.env.REPORT_TIME || '10:05'
};

function parseTime(timeStr) {
  const [hour, minute] = timeStr.split(':').map(Number);
  return { hour, minute };
}

function getPhnomPenhNow() {
  return moment.tz(config.TIMEZONE);
}

function getPhnomPenhDate() {
  return getPhnomPenhNow().format('YYYY-MM-DD');
}

function isBeforeDeadline(timestamp = null) {
  const now = timestamp ? moment.tz(timestamp, config.TIMEZONE) : getPhnomPenhNow();
  const deadline = now.clone().hour(10).minute(0).second(0).millisecond(0);
  return now.isBefore(deadline);
}

function isAttendanceWindowOpen() {
  // Check scheduler flag first (primary source)
  let schedulerFlag = null;
  try {
    const { getAttendanceWindowStatus } = require('./scheduler');
    schedulerFlag = getAttendanceWindowStatus();
  } catch (e) {
    // Scheduler not available yet
  }

  // Also check actual time as validation/fallback
  const now = getPhnomPenhNow();
  const [startHour, startMinute] = config.ATTENDANCE_WINDOW_START.split(':').map(Number);
  const [endHour, endMinute] = config.ATTENDANCE_WINDOW_END.split(':').map(Number);
  
  const windowStart = now.clone().hour(startHour).minute(startMinute).second(0);
  const windowEnd = now.clone().hour(endHour).minute(endMinute).second(0);
  
  const timeCheck = now.isSameOrAfter(windowStart) && now.isBefore(windowEnd);

  // If scheduler flag is available, use it; otherwise use time check
  if (schedulerFlag !== null) {
    return schedulerFlag && timeCheck;
  } else {
    return timeCheck;
  }
}

module.exports = {
  config,
  parseTime,
  getPhnomPenhNow,
  getPhnomPenhDate,
  isBeforeDeadline,
  isAttendanceWindowOpen
};

