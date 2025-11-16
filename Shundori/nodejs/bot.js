/**
 * Main Telegram bot implementation (Node.js/Telegraf)
 */
const { Telegraf } = require('telegraf');
const { config, getPhnomPenhDate } = require('./config');
const { initDB } = require('./database');
const { recordAttendance, forceMarkAttendance, getOrCreateUser } = require('./attendance');
const { generateDailyReport, formatDailyReportMessage, exportDailyCSV, exportMonthlyCSV, getFineAmount } = require('./reports');
const { setupScheduler, setGroupChatId, getAttendanceWindowStatus } = require('./scheduler');

// Initialize bot
const bot = new Telegraf(config.BOT_TOKEN);

// Store group chat ID
let groupChatId = null;

// Admin check
function isAdmin(userId) {
  return userId === config.ADMIN_ID;
}

// Start command
bot.command('start', (ctx) => {
  ctx.reply(
    "Hello! I'm the attendance bot. " +
    "Send '1' in the group chat between 09:00 and 10:00 AM to record your attendance."
  );
});

// Handle attendance message ("1")
bot.hears(/^1$/, async (ctx) => {
  // Only process in group chats
  if (ctx.chat.type !== 'group' && ctx.chat.type !== 'supergroup') {
    return;
  }

  // Store group chat ID
  if (!groupChatId) {
    groupChatId = ctx.chat.id;
    setGroupChatId(groupChatId);
  }

  // Check if window is open
  if (!getAttendanceWindowStatus()) {
    await ctx.reply('⏰ Attendance window is closed. Please send \'1\' between 09:00 and 10:00 AM.');
    return;
  }

  const user = ctx.from;
  const telegramId = user.id;
  const username = user.username;
  const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.first_name;

  // Record attendance
  try {
    const result = await recordAttendance(telegramId, ctx.message.date * 1000, username, fullName);

    if (result.success) {
      // Send greeting in private chat
      try {
        await ctx.telegram.sendMessage(
          telegramId,
          `Good morning, ${fullName}! ${result.message}`
        );
      } catch (error) {
        console.warn(`Could not send private message to ${telegramId}:`, error.message);
        // Still record attendance, notify admin
        if (isAdmin(config.ADMIN_ID)) {
          try {
            await ctx.telegram.sendMessage(
              config.ADMIN_ID,
              `⚠️ Could not send greeting to ${fullName} (ID: ${telegramId}). Attendance still recorded.`
            );
          } catch (e) {
            // Ignore
          }
        }
      }
    } else {
      await ctx.reply(result.message);
    }
  } catch (error) {
    console.error('Error recording attendance:', error);
    await ctx.reply('❌ An error occurred while recording attendance. Please try again.');
  }
});

// Report command
bot.command('report', async (ctx) => {
  if (!isAdmin(ctx.from.id)) {
    await ctx.reply('❌ You are not authorized to use this command.');
    return;
  }

  let reportDate = getPhnomPenhDate();
  if (ctx.message.text.split(' ').length > 1) {
    const dateStr = ctx.message.text.split(' ')[1];
    const dateMatch = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (!dateMatch) {
      await ctx.reply('❌ Invalid date format. Use YYYY-MM-DD');
      return;
    }
    reportDate = dateStr;
  }

  try {
    const report = await generateDailyReport(reportDate);
    const message = formatDailyReportMessage(report, true);
    await ctx.reply(message);
  } catch (error) {
    console.error('Error generating report:', error);
    await ctx.reply('❌ Error generating report.');
  }
});

// Monthly command
bot.command('monthly', async (ctx) => {
  if (!isAdmin(ctx.from.id)) {
    await ctx.reply('❌ You are not authorized to use this command.');
    return;
  }

  const args = ctx.message.text.split(' ');
  if (args.length < 2) {
    await ctx.reply('❌ Please provide month in YYYY-MM format.');
    return;
  }

  const dateMatch = args[1].match(/^(\d{4})-(\d{2})$/);
  if (!dateMatch) {
    await ctx.reply('❌ Invalid date format. Use YYYY-MM');
    return;
  }

  const [year, month] = args[1].split('-').map(Number);

  try {
    const filepath = await exportMonthlyCSV(year, month);
    await ctx.replyWithDocument(
      { source: filepath, filename: `attendance_${year}_${month.toString().padStart(2, '0')}.csv` },
      { caption: `Monthly report for ${year}-${month.toString().padStart(2, '0')}` }
    );
  } catch (error) {
    console.error('Error generating monthly report:', error);
    await ctx.reply(`❌ Error generating report: ${error.message}`);
  }
});

// Setfine command
bot.command('setfine', async (ctx) => {
  if (!isAdmin(ctx.from.id)) {
    await ctx.reply('❌ You are not authorized to use this command.');
    return;
  }

  const args = ctx.message.text.split(' ');
  if (args.length < 2) {
    await ctx.reply('❌ Please provide fine amount. Usage: /setfine <amount>');
    return;
  }

  const amount = parseFloat(args[1]);
  if (isNaN(amount) || amount < 0) {
    await ctx.reply('❌ Invalid amount. Please provide a positive number.');
    return;
  }

  const { pool } = require('./database');
  const client = await pool.connect();
  try {
    await client.query(
      'INSERT INTO settings (key, value) VALUES ($1, $2) ON CONFLICT (key) DO UPDATE SET value = $2',
      ['fine_amount', amount.toString()]
    );
    await ctx.reply(`✅ Fine amount set to $${amount.toFixed(2)}`);
  } catch (error) {
    console.error('Error setting fine:', error);
    await ctx.reply('❌ Error setting fine amount.');
  } finally {
    client.release();
  }
});

// Set-window command
bot.command('set-window', async (ctx) => {
  if (!isAdmin(ctx.from.id)) {
    await ctx.reply('❌ You are not authorized to use this command.');
    return;
  }

  const args = ctx.message.text.split(' ');
  if (args.length < 3) {
    await ctx.reply('❌ Usage: /set-window <HH:MM> <HH:MM>');
    return;
  }

  const timeRegex = /^(\d{2}):(\d{2})$/;
  if (!timeRegex.test(args[1]) || !timeRegex.test(args[2])) {
    await ctx.reply('❌ Invalid time format. Use HH:MM');
    return;
  }

  const { pool } = require('./database');
  const client = await pool.connect();
  try {
    await client.query(
      'INSERT INTO settings (key, value) VALUES ($1, $2) ON CONFLICT (key) DO UPDATE SET value = $2',
      ['window_start', args[1]]
    );
    await client.query(
      'INSERT INTO settings (key, value) VALUES ($1, $2) ON CONFLICT (key) DO UPDATE SET value = $2',
      ['window_end', args[2]]
    );
    await ctx.reply(`✅ Attendance window set to ${args[1]} - ${args[2]}`);
  } catch (error) {
    console.error('Error setting window:', error);
    await ctx.reply('❌ Error setting attendance window.');
  } finally {
    client.release();
  }
});

// Force-mark command
bot.command('force-mark', async (ctx) => {
  if (!isAdmin(ctx.from.id)) {
    await ctx.reply('❌ You are not authorized to use this command.');
    return;
  }

  const args = ctx.message.text.split(' ');
  if (args.length < 3) {
    await ctx.reply('❌ Usage: /force-mark <user_id> present|absent');
    return;
  }

  const userId = parseInt(args[1]);
  const status = args[2].toLowerCase();

  if (isNaN(userId) || (status !== 'present' && status !== 'absent')) {
    await ctx.reply('❌ Invalid arguments. Usage: /force-mark <user_id> present|absent');
    return;
  }

  try {
    const success = await forceMarkAttendance(userId, status);
    if (success) {
      await ctx.reply(`✅ Attendance marked as ${status} for user ${userId}`);
    } else {
      await ctx.reply(`❌ User ${userId} not found`);
    }
  } catch (error) {
    console.error('Error force marking:', error);
    await ctx.reply('❌ Error marking attendance.');
  }
});

// Export command
bot.command('export', async (ctx) => {
  if (!isAdmin(ctx.from.id)) {
    await ctx.reply('❌ You are not authorized to use this command.');
    return;
  }

  let exportDate = getPhnomPenhDate();
  if (ctx.message.text.split(' ').length > 1) {
    const dateStr = ctx.message.text.split(' ')[1];
    const dateMatch = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (!dateMatch) {
      await ctx.reply('❌ Invalid date format. Use YYYY-MM-DD');
      return;
    }
    exportDate = dateStr;
  }

  try {
    const filepath = await exportDailyCSV(exportDate);
    await ctx.replyWithDocument(
      { source: filepath, filename: `attendance_${exportDate.replace(/-/g, '')}.csv` },
      { caption: `Daily attendance report for ${exportDate}` }
    );
  } catch (error) {
    console.error('Error exporting CSV:', error);
    await ctx.reply(`❌ Error exporting CSV: ${error.message}`);
  }
});

// Error handling
bot.catch((err, ctx) => {
  console.error(`Error for ${ctx.updateType}:`, err);
});

// Initialize and start
async function main() {
  if (!config.BOT_TOKEN) {
    throw new Error('BOT_TOKEN environment variable is not set');
  }

  if (!config.ADMIN_ID) {
    throw new Error('ADMIN_ID environment variable is not set');
  }

  // Initialize database
  await initDB();

  // Setup scheduler
  setupScheduler(bot, () => groupChatId);

  console.log('Bot initialized successfully');
  console.log('Starting bot...');

  // Start bot
  bot.launch();

  // Enable graceful stop
  process.once('SIGINT', () => bot.stop('SIGINT'));
  process.once('SIGTERM', () => bot.stop('SIGTERM'));
}

// Run bot
main().catch((error) => {
  console.error('Failed to start bot:', error);
  process.exit(1);
});

