#!/bin/bash

# Deployment script for Telegram Attendance Bot

echo "🚀 Telegram Attendance Bot Deployment"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo ""
    echo "📝 Setting up .env file..."
    echo ""
    
    # Get BOT_TOKEN
    echo "1️⃣  Get your BOT_TOKEN:"
    echo "   - Open Telegram and message @BotFather"
    echo "   - Send /newbot and follow instructions"
    echo "   - Copy the token you receive"
    echo ""
    read -p "   Enter your BOT_TOKEN: " BOT_TOKEN
    
    # Get ADMIN_ID
    echo ""
    echo "2️⃣  Get your ADMIN_ID:"
    echo "   - Open Telegram and message @userinfobot"
    echo "   - It will reply with your user ID"
    echo "   - Copy the ID number"
    echo ""
    read -p "   Enter your ADMIN_ID: " ADMIN_ID
    
    # Create .env file
    cat > .env << EOF
# Telegram Bot Configuration
BOT_TOKEN=${BOT_TOKEN}
ADMIN_ID=${ADMIN_ID}

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/attendance_bot

# Timezone
TZ=Asia/Phnom_Penh

# Fine Configuration (default)
DEFAULT_FINE_AMOUNT=20

# Attendance Window (default)
ATTENDANCE_WINDOW_START=09:00
ATTENDANCE_WINDOW_END=10:00

# Report Time
REPORT_TIME=10:05
EOF
    
    echo ""
    echo "✅ .env file created!"
    echo ""
else
    echo "✅ .env file found"
    source .env
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "   Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed!"
    echo "   Please install Docker Compose"
    exit 1
fi

echo ""
echo "🐳 Starting Docker containers..."
echo ""

# Stop any existing containers
docker-compose down 2>/dev/null

# Build and start
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Bot is running!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Add your bot to your Telegram group"
    echo "   2. Make the bot an admin in the group (optional but recommended)"
    echo "   3. Send /start in the group to test"
    echo "   4. Wait for 09:00 AM (Asia/Phnom_Penh) for attendance window to open"
    echo ""
    echo "📊 View logs:"
    echo "   docker-compose logs -f bot"
    echo ""
    echo "🛑 Stop bot:"
    echo "   docker-compose down"
    echo ""
else
    echo ""
    echo "❌ Failed to start containers. Check logs:"
    echo "   docker-compose logs"
    exit 1
fi

