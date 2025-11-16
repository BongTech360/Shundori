# 🚀 Start Here - Get Your Bot Running in Telegram Group

## Quick Setup (5 minutes)

### Step 1: Get Your Admin ID

1. **Open Telegram**
2. **Message @userinfobot**
3. **Copy your ID** (the number, e.g., `123456789`)

### Step 2: Run Quick Start Script

```bash
cd /Users/macos/Desktop/Shundori
./quick_start.sh
```

The script will:
- Ask for your ADMIN_ID
- Let you choose deployment method
- Guide you through setup

---

## Or Choose Your Method Manually

### Option 1: Cloud Deployment (Recommended) ☁️

**Best for:** 24/7 operation, no need to keep computer on

**Railway (Easiest):**
- See `DEPLOY_RAILWAY.md`
- Free tier available
- Built-in PostgreSQL

**Render:**
- See `DEPLOY_TO_CLOUD.md`
- Free tier available
- Easy setup

### Option 2: Local Deployment 💻

**Best for:** Testing, development

**Docker:**
```bash
docker-compose up -d
```

**Python:**
```bash
./setup_direct.sh
./run_bot.sh
```

---

## Add Bot to Your Telegram Group

1. **Open your Telegram group**
2. **Click group name** → **"Add Members"**
3. **Search for your bot** (username from @BotFather)
4. **Add the bot**
5. **Optional:** Make bot admin in group settings

---

## Test the Bot

1. **In group, send:** `/start`
2. **As admin, send:** `/report`
3. **During 09:00-10:00 AM:** Send `1` to record attendance

---

## Your Bot Details

- **Bot Token:** `8221249139:AAFKdgbFIoSUa5loMzrN-tJOd_BFsdFXSYA` ✅
- **Admin ID:** Get from @userinfobot ⚠️

---

## Need Help?

- **Quick Start:** Run `./quick_start.sh`
- **Add to Group:** See `ADD_TO_GROUP.md`
- **Cloud Deploy:** See `DEPLOY_RAILWAY.md`
- **All Options:** See `DEPLOY_TO_CLOUD.md`

---

**🎯 Goal:** Get bot running → Add to group → Test → Done!

