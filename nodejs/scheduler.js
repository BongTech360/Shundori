/**
 * Scheduler for attendance window and daily reports (Node.js)
 */
const cron = require('node-cron');
const { config, parseTime, getPhnomPenhDate } = require('./config');
const { processDailyAttendance } = require('./attendance');
const { generateDailyReport, formatDailyReportMessage } = require('./reports');

// Global flag for attendance window
let attendanceWindowOpen = false;

// Store bot instance and group chat ID getter
let botInstance = null;
let getGroupChatId = null;

function setBotInstance(bot, getChatIdFn) {
  botInstance = bot;
  getGroupChatId = getChatIdFn;
}

function getAttendanceWindowStatus() {
  return attendanceWindowOpen;
}

function setAttendanceWindowStatus(status) {
  attendanceWindowOpen = status;
  console.log(`Attendance window ${status ? 'opened' : 'closed'}`);
}

async function openAttendanceWindow() {
  setAttendanceWindowStatus(true);
  console.log('Attendance window opened at 09:00 AM');

  const chatId = getGroupChatId ? getGroupChatId() : null;
  if (chatId && botInstance) {
    try {
      await botInstance.telegram.sendMessage(
        chatId,
        '✅ Attendance window is now open! Send \'1\' to record your attendance.'
      );
    } catch (error) {
      console.error('Failed to send window open message:', error);
    }
  }
}

async function closeAttendanceWindow() {
  setAttendanceWindowStatus(false);
  console.log('Attendance window closed at 10:00 AM');

  // Process attendance for all members
  try {
    await processDailyAttendance();
  } catch (error) {
    console.error('Error processing daily attendance:', error);
  }

  const chatId = getGroupChatId ? getGroupChatId() : null;
  if (chatId && botInstance) {
    try {
      await botInstance.telegram.sendMessage(
        chatId,
        '⏰ Attendance window is now closed. Processing attendance...'
      );
    } catch (error) {
      console.error('Failed to send window close message:', error);
    }
  }
}

async function sendDailyReport() {
  console.log('Generating daily report');

  const chatId = getGroupChatId ? getGroupChatId() : null;
  if (!chatId || !botInstance) {
    console.warn('Group chat ID or bot instance not set, cannot send daily report');
    return;
  }

  try {
    const report = await generateDailyReport();
    const message = formatDailyReportMessage(report, false);

    await botInstance.telegram.sendMessage(chatId, message);
    console.log('Daily report sent successfully');
  } catch (error) {
    console.error('Failed to send daily report:', error);
  }
}

function setupScheduler(bot, getChatIdFn) {
  setBotInstance(bot, getChatIdFn);

  // Get times from config
  const windowStart = parseTime(config.ATTENDANCE_WINDOW_START);
  const windowEnd = parseTime(config.ATTENDANCE_WINDOW_END);
  const reportTime = parseTime(config.REPORT_TIME);

  // Schedule window opening (09:00 AM Phnom Penh time)
  // node-cron with timezone support
  const startCron = `${windowStart.minute} ${windowStart.hour} * * *`;
  cron.schedule(startCron, openAttendanceWindow, {
    timezone: 'Asia/Phnom_Penh'
  });

  // Schedule window closing (10:00 AM Phnom Penh time)
  const endCron = `${windowEnd.minute} ${windowEnd.hour} * * *`;
  cron.schedule(endCron, closeAttendanceWindow, {
    timezone: 'Asia/Phnom_Penh'
  });

  // Schedule daily report (10:05 AM Phnom Penh time)
  const reportCron = `${reportTime.minute} ${reportTime.hour} * * *`;
  cron.schedule(reportCron, sendDailyReport, {
    timezone: 'Asia/Phnom_Penh'
  });

  console.log('Scheduler started');
  console.log(`Window: ${config.ATTENDANCE_WINDOW_START} - ${config.ATTENDANCE_WINDOW_END}`);
  console.log(`Report time: ${config.REPORT_TIME}`);
}

module.exports = {
  setupScheduler,
  getAttendanceWindowStatus,
  setAttendanceWindowStatus,
  setGroupChatId: (chatId) => {
    // This is a simple setter, but we use a getter function instead
  }
};

