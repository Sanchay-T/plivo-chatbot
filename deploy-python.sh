#!/bin/bash

# DigitalOcean Python Deployment Script for Plivo Chatbot
# Run this script on your DigitalOcean droplet

set -e

echo "🚀 Starting Python deployment of Plivo Chatbot..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and required system packages
echo "🐍 Installing Python and system dependencies..."
sudo apt install -y python3 python3-pip python3-venv git nginx curl htop

# Install ffmpeg for audio processing
echo "🎵 Installing ffmpeg for audio processing..."
sudo apt install -y ffmpeg

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

# Create virtual environment
echo "🔧 Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "⚙️ Setting up environment file..."
    cp production.env.example .env
    echo "❗ Please edit .env file with your actual credentials before continuing"
    echo "❗ Run: nano .env"
    echo "❗ After editing .env, run this script again to continue setup"
    exit 1
fi

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/plivo-chatbot.service > /dev/null <<EOF
[Unit]
Description=Plivo AI Chatbot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/.venv/bin
ExecStart=$(pwd)/.venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
echo "🚀 Enabling and starting the service..."
sudo systemctl daemon-reload
sudo systemctl enable plivo-chatbot
sudo systemctl start plivo-chatbot

# Setup Nginx reverse proxy
echo "🌐 Setting up Nginx reverse proxy..."
sudo tee /etc/nginx/sites-available/plivo-chatbot > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8765;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /ws {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/plivo-chatbot /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Setup firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8765/tcp
sudo ufw --force enable

# Check service status
echo "📊 Checking service status..."
sudo systemctl status plivo-chatbot --no-pager

echo "✅ Deployment complete!"
echo "🌐 Your application should be available at: http://$(curl -s ifconfig.me)"
echo "📝 Check logs with: sudo journalctl -u plivo-chatbot -f"
echo "🔄 Restart with: sudo systemctl restart plivo-chatbot"
echo "🛑 Stop with: sudo systemctl stop plivo-chatbot"
echo "📊 Service status: sudo systemctl status plivo-chatbot" 