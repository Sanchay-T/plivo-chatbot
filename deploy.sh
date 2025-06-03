#!/bin/bash

# DigitalOcean Deployment Script for Plivo Chatbot
# Run this script on your DigitalOcean droplet

set -e

echo "🚀 Starting deployment of Plivo Chatbot..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Clone or pull latest code
if [ ! -d "plivo-chatbot" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/Sanchay-T/plivo-chatbot.git
    cd plivo-chatbot
else
    echo "📥 Pulling latest changes..."
    cd plivo-chatbot
    git pull origin main
fi

# Setup environment file
if [ ! -f ".env" ]; then
    echo "⚙️ Setting up environment file..."
    cp production.env.example .env
    echo "❗ Please edit .env file with your actual credentials before continuing"
    echo "❗ Run: nano .env"
    exit 1
fi

# Build and start the application
echo "🏗️ Building and starting the application..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Setup firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 8765/tcp
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo "✅ Deployment complete!"
echo "🌐 Your application should be available at: http://$(curl -s ifconfig.me):8765"
echo "📝 Check logs with: docker-compose logs -f"
echo "🔄 Restart with: docker-compose restart"
echo "🛑 Stop with: docker-compose down" 