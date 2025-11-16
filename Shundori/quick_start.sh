#!/bin/bash

# Quick Start Script - Get Bot Running for Telegram Group

echo "🤖 Telegram Attendance Bot - Quick Start"
echo "=========================================="
echo ""

# Check if ADMIN_ID is set
if grep -q "your_telegram_user_id_here" .env 2>/dev/null || ! grep -q "ADMIN_ID=" .env 2>/dev/null; then
    echo "📱 Step 1: Get Your Admin ID"
    echo "----------------------------"
    echo ""
    echo "1. Open Telegram"
    echo "2. Search for @userinfobot"
    echo "3. Start a chat (it will reply automatically)"
    echo "4. Copy your ID number (looks like: Id: 123456789)"
    echo ""
    read -p "Enter your ADMIN_ID: " ADMIN_ID
    
    # Update .env file
    if [ -f .env ]; then
        if grep -q "ADMIN_ID=" .env; then
            sed -i '' "s/ADMIN_ID=.*/ADMIN_ID=${ADMIN_ID}/" .env
        else
            echo "ADMIN_ID=${ADMIN_ID}" >> .env
        fi
        echo ""
        echo "✅ ADMIN_ID updated in .env file"
    fi
else
    echo "✅ ADMIN_ID already set"
    source .env
    ADMIN_ID=$ADMIN_ID
fi

echo ""
echo "🤖 Your Bot Token: 8221249139:AAFKdgbFIoSUa5loMzrN-tJOd_BFsdFXSYA"
echo "👤 Your Admin ID: ${ADMIN_ID}"
echo ""

# Check deployment method
echo "📋 Choose how to run the bot:"
echo ""
echo "1) Deploy to Railway (Cloud - Recommended - Always Running)"
echo "2) Deploy to Render (Cloud - Free Tier)"
echo "3) Run locally with Docker (Requires Docker Desktop)"
echo "4) Run locally with Python (Requires PostgreSQL)"
echo ""
read -p "Choose option (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚂 Deploying to Railway..."
        echo ""
        echo "📝 Steps:"
        echo "1. Go to https://railway.app and sign up"
        echo "2. Create new project"
        echo "3. Add PostgreSQL database"
        echo "4. Deploy from GitHub or upload files"
        echo "5. Set environment variables (see DEPLOY_RAILWAY.md)"
        echo ""
        echo "📖 See DEPLOY_RAILWAY.md for detailed instructions"
        echo ""
        echo "Environment variables to set:"
        echo "  BOT_TOKEN=8221249139:AAFKdgbFIoSUa5loMzrN-tJOd_BFsdFXSYA"
        echo "  ADMIN_ID=${ADMIN_ID}"
        echo "  DATABASE_URL=\${{Postgres.DATABASE_URL}}"
        echo "  TZ=Asia/Phnom_Penh"
        echo "  DEFAULT_FINE_AMOUNT=20"
        echo "  ATTENDANCE_WINDOW_START=09:00"
        echo "  ATTENDANCE_WINDOW_END=10:00"
        echo "  REPORT_TIME=10:05"
        ;;
    2)
        echo ""
        echo "🎨 Deploying to Render..."
        echo ""
        echo "📝 Steps:"
        echo "1. Go to https://render.com and sign up"
        echo "2. Create PostgreSQL database"
        echo "3. Create Web Service"
        echo "4. Connect GitHub or upload files"
        echo "5. Set environment variables"
        echo ""
        echo "📖 See DEPLOY_TO_CLOUD.md for detailed instructions"
        ;;
    3)
        echo ""
        echo "🐳 Setting up with Docker..."
        echo ""
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker not found!"
            echo "   Install Docker Desktop: https://www.docker.com/products/docker-desktop"
            exit 1
        fi
        
        echo "Starting Docker containers..."
        docker-compose up -d --build
        
        echo ""
        echo "✅ Bot is starting..."
        echo ""
        echo "View logs: docker-compose logs -f bot"
        echo "Stop bot: docker-compose down"
        ;;
    4)
        echo ""
        echo "🐍 Setting up with Python..."
        echo ""
        
        # Check PostgreSQL
        if ! command -v psql &> /dev/null; then
            echo "⚠️  PostgreSQL not found"
            echo ""
            echo "Install PostgreSQL:"
            echo "  brew install postgresql@15"
            echo "  brew services start postgresql@15"
            echo ""
            read -p "Press Enter after installing PostgreSQL..."
        fi
        
        # Setup virtual environment
        if [ ! -d "venv" ]; then
            echo "Creating virtual environment..."
            python3 -m venv venv
        fi
        
        source venv/bin/activate
        
        echo "Installing dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
        
        echo ""
        echo "Initializing database..."
        python migrations/init_db.py
        
        echo ""
        echo "✅ Setup complete!"
        echo ""
        echo "Starting bot..."
        echo ""
        python bot.py
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "📱 Next Steps:"
echo "=============="
echo ""
echo "1. Add bot to your Telegram group:"
echo "   - Open your Telegram group"
echo "   - Click group name → Add Members"
echo "   - Search for your bot (username from @BotFather)"
echo "   - Add the bot"
echo ""
echo "2. Test the bot:"
echo "   - Send /start in the group"
echo "   - Send /report (as admin)"
echo ""
echo "3. Wait for attendance window:"
echo "   - Bot opens window at 09:00 AM (Asia/Phnom_Penh)"
echo "   - Members send '1' to record attendance"
echo "   - Daily report at 10:05 AM"
echo ""
echo "📖 See ADD_TO_GROUP.md for detailed group setup instructions"

