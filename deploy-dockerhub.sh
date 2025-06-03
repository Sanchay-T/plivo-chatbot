#!/bin/bash

# DigitalOcean Docker Hub Deployment Script for Plivo Chatbot
# Uses pre-built image from Docker Hub for instant deployment

set -e

echo "🚀 Starting Docker Hub deployment of Plivo Chatbot..."

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
    echo "⚠️  Please log out and log back in for Docker permissions to take effect"
    echo "⚠️  Then run this script again"
    exit 1
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create project directory
echo "📁 Creating project directory..."
mkdir -p plivo-chatbot
cd plivo-chatbot

# Download production docker-compose file
echo "📥 Downloading production configuration..."
curl -fsSL https://raw.githubusercontent.com/Sanchay-T/plivo-chatbot/main/docker-compose.prod.yml -o docker-compose.yml

# Download environment template
curl -fsSL https://raw.githubusercontent.com/Sanchay-T/plivo-chatbot/main/production.env.example -o production.env.example

# Setup environment file
if [ ! -f ".env" ]; then
    echo "⚙️ Setting up environment file..."
    cp production.env.example .env
    echo "❗ Please edit .env file with your actual credentials before continuing"
    echo "❗ Run: nano .env"
    echo "❗ After editing .env, run this script again to continue setup"
    exit 1
fi

# Create data directory
mkdir -p data

# Pull and start the application (no build needed!)
echo "🏗️ Pulling Docker image from Docker Hub..."
docker-compose pull

echo "🚀 Starting the application..."
docker-compose up -d

# Setup firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8765/tcp
sudo ufw --force enable

# Check service status
echo "📊 Checking service status..."
docker-compose ps

echo "✅ Deployment complete!"
echo "🌐 Your application should be available at: http://$(curl -s ifconfig.me):8765"
echo "📝 Check logs with: docker-compose logs -f"
echo "🔄 Restart with: docker-compose restart"
echo "🛑 Stop with: docker-compose down"
echo "🔄 Update with: docker-compose pull && docker-compose up -d" 