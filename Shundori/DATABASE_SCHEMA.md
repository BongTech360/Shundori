# Database Schema Documentation

This document describes the database schema for the Telegram Attendance Bot.

## Overview

The bot uses PostgreSQL with the following tables:
- `users` - Telegram user information
- `attendance_records` - Daily attendance tracking
- `fines` - Fine records for late/absent members
- `settings` - Bot configuration

## Schema Definition

### Users Table

Stores Telegram user information.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    username VARCHAR(255),
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_telegram_id ON users(telegram_id);
```

**Columns:**
- `id` - Primary key (auto-increment)
- `telegram_id` - Unique Telegram user ID
- `username` - Telegram username (nullable)
- `full_name` - User's full name (nullable)
- `created_at` - Account creation timestamp
- `is_active` - Whether user is active (default: true)

### Attendance Records Table

Stores daily attendance records.

```sql
CREATE TABLE attendance_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,  -- 'present', 'absent', 'late'
    timestamp TIMESTAMP,  -- When "1" was sent (NULL for absent)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_attendance_user_date ON attendance_records(user_id, date);
CREATE INDEX idx_attendance_date ON attendance_records(date);
```

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to users table
- `date` - Date of attendance record
- `status` - Status: 'present', 'absent', or 'late'
- `timestamp` - When attendance was recorded (NULL for absent)
- `created_at` - Record creation timestamp

**Status Values:**
- `present` - User sent "1" before 10:00 AM
- `late` - User sent "1" after 10:00 AM but within window
- `absent` - User did not send "1" (marked at 10:00 AM)

### Fines Table

Stores fine records for late/absent members.

```sql
CREATE TABLE fines (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    amount FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fines_user_date ON fines(user_id, date);
CREATE INDEX idx_fines_date ON fines(date);
```

**Columns:**
- `id` - Primary key
- `user_id` - Foreign key to users table
- `date` - Date of fine
- `amount` - Fine amount (default: $20)
- `created_at` - Record creation timestamp

### Settings Table

Stores bot configuration.

```sql
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_settings_key ON settings(key);
```

**Columns:**
- `id` - Primary key
- `key` - Setting key (e.g., 'fine_amount', 'window_start', 'window_end')
- `value` - Setting value (stored as string)
- `updated_at` - Last update timestamp

**Common Settings:**
- `fine_amount` - Default fine amount (e.g., "20")
- `window_start` - Attendance window start time (e.g., "09:00")
- `window_end` - Attendance window end time (e.g., "10:00")

## Relationships

```
users (1) ──< (many) attendance_records
users (1) ──< (many) fines
```

- One user can have many attendance records (one per day)
- One user can have many fines (one per day when absent/late)

## Sample Queries

### Get all users with their attendance for a date
```sql
SELECT 
    u.telegram_id,
    u.full_name,
    ar.status,
    ar.timestamp,
    COALESCE(f.amount, 0) as fine_amount
FROM users u
LEFT JOIN attendance_records ar ON u.id = ar.user_id AND ar.date = '2024-01-15'
LEFT JOIN fines f ON u.id = f.user_id AND f.date = '2024-01-15'
WHERE u.is_active = TRUE;
```

### Get monthly summary for a user
```sql
SELECT 
    DATE_TRUNC('month', ar.date) as month,
    COUNT(CASE WHEN ar.status = 'present' THEN 1 END) as present_days,
    COUNT(CASE WHEN ar.status IN ('absent', 'late') THEN 1 END) as absent_days,
    SUM(f.amount) as total_fines
FROM users u
LEFT JOIN attendance_records ar ON u.id = ar.user_id
LEFT JOIN fines f ON u.id = f.user_id AND f.date = ar.date
WHERE u.telegram_id = 12345
    AND ar.date >= '2024-01-01'
    AND ar.date < '2024-02-01'
GROUP BY DATE_TRUNC('month', ar.date);
```

### Get running fines per user
```sql
SELECT 
    u.telegram_id,
    u.full_name,
    SUM(f.amount) as total_fines
FROM users u
LEFT JOIN fines f ON u.id = f.user_id
WHERE u.is_active = TRUE
GROUP BY u.id, u.telegram_id, u.full_name
HAVING SUM(f.amount) > 0
ORDER BY total_fines DESC;
```

## Data Migration

### Initial Setup

The database tables are created automatically when the bot starts (Python) or via `initDB()` (Node.js).

### Manual Creation

If you need to create tables manually:

```sql
-- Run all CREATE TABLE statements above
-- Then run CREATE INDEX statements
```

### Backup

```bash
# Backup database
pg_dump attendance_bot > backup_$(date +%Y%m%d).sql

# Restore
psql attendance_bot < backup_20240115.sql
```

## Data Integrity

- Foreign key constraints ensure referential integrity
- Unique constraints prevent duplicate records
- Indexes improve query performance
- CASCADE deletes ensure cleanup when users are removed

## Performance Considerations

- Indexes on frequently queried columns (telegram_id, date, user_id)
- Composite indexes for common query patterns
- Consider partitioning attendance_records by date for large datasets
- Regular VACUUM and ANALYZE for optimal performance

## Future Enhancements

Potential schema additions:
- `groups` table for multi-group support
- `attendance_exceptions` for holidays/vacations
- `fine_history` for fine amount changes
- `notifications` for user notifications log

