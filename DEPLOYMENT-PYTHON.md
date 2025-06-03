# DigitalOcean Python Deployment Guide

This guide shows how to deploy the Plivo Chatbot using the same Python approach you use locally - no Docker required!

## Prerequisites

1. **DigitalOcean Account** with a droplet (Ubuntu 20.04+ recommended)
2. **Domain name** (optional but recommended) pointing to your droplet
3. **API Keys** for:
   - Plivo (Auth ID & Token)
   - OpenAI
   - Deepgram
   - Cartesia

## Quick Deployment

### 1. Create DigitalOcean Droplet

**Recommended Specifications:**
- **OS**: Ubuntu 22.04 LTS
- **Size**: Basic droplet, 2GB RAM, 1 vCPU ($12/month)
- **Region**: Choose closest to your target audience
- **Additional Options**: 
  - Enable monitoring
  - Add SSH key for secure access

### 2. One-Command Deployment

```bash
# Connect to your droplet
ssh root@your_droplet_ip

# Download and run the Python deployment script
curl -fsSL https://raw.githubusercontent.com/Sanchay-T/plivo-chatbot/main/deploy-python.sh -o deploy-python.sh
chmod +x deploy-python.sh
./deploy-python.sh
```

The script will:
- Install Python 3, pip, venv, nginx, ffmpeg
- Clone your repository
- Create a virtual environment (just like locally)
- Install all dependencies from requirements.txt
- Create a systemd service to run your server
- Setup nginx as reverse proxy
- Configure firewall

### 3. Configure Environment Variables

When the script pauses, edit your environment file:

```bash
nano .env

# Fill in your actual values:
PLIVO_AUTH_ID=your_actual_plivo_auth_id
PLIVO_AUTH_TOKEN=your_actual_plivo_auth_token
OPENAI_API_KEY=your_actual_openai_api_key
DEEPGRAM_API_KEY=your_actual_deepgram_api_key
CARTESIA_API_KEY=your_actual_cartesia_api_key
SERVER_URL=your-domain.com  # or your droplet IP
```

Then run the script again:
```bash
./deploy-python.sh
```

## How It Works

Your application runs exactly like locally:
- **Virtual Environment**: `.venv/bin/python server.py`
- **Same Dependencies**: From your `requirements.txt`
- **Same Code**: Direct from your GitHub repo
- **Systemd Service**: Keeps it running and auto-restarts

## Management Commands

```bash
# Check if your app is running
sudo systemctl status plivo-chatbot

# View live logs (like your local terminal)
sudo journalctl -u plivo-chatbot -f

# Restart the application
sudo systemctl restart plivo-chatbot

# Stop the application
sudo systemctl stop plivo-chatbot

# Start the application
sudo systemctl start plivo-chatbot

# Update your application
cd plivo-chatbot
git pull origin main
pip install -r requirements.txt  # if dependencies changed
sudo systemctl restart plivo-chatbot
```

## Local vs Production Comparison

| Aspect | Local | Production |
|--------|-------|------------|
| **Start Command** | `python server.py` | `systemctl start plivo-chatbot` |
| **Environment** | `.venv` | `.venv` (same) |
| **Dependencies** | `pip install -r requirements.txt` | `pip install -r requirements.txt` (same) |
| **Logs** | Terminal output | `journalctl -u plivo-chatbot -f` |
| **Access** | `localhost:8765` | `your-domain.com` or `droplet-ip` |
| **Auto-restart** | Manual | Automatic (systemd) |

## Troubleshooting

### Check Service Status
```bash
sudo systemctl status plivo-chatbot
```

### View Logs
```bash
# Live logs (like your local terminal)
sudo journalctl -u plivo-chatbot -f

# Recent logs
sudo journalctl -u plivo-chatbot -n 50
```

### Common Issues

1. **Port 8765 already in use**
   ```bash
   sudo lsof -i :8765
   sudo systemctl stop plivo-chatbot
   ```

2. **Environment variables not loaded**
   ```bash
   # Check if .env file exists and has correct values
   cat .env
   sudo systemctl restart plivo-chatbot
   ```

3. **Python dependencies missing**
   ```bash
   cd plivo-chatbot
   source .venv/bin/activate
   pip install -r requirements.txt
   sudo systemctl restart plivo-chatbot
   ```

4. **WebSocket connection issues**
   - Ensure SERVER_URL in .env matches your actual domain/IP
   - Check firewall: `sudo ufw status`
   - Check nginx: `sudo nginx -t`

### Manual Setup (if script fails)

```bash
# 1. Install dependencies
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git nginx ffmpeg

# 2. Clone repository
git clone https://github.com/Sanchay-T/plivo-chatbot.git
cd plivo-chatbot

# 3. Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Setup environment
cp production.env.example .env
nano .env  # Edit with your values

# 5. Test locally first
python server.py  # Should work just like on your local machine

# 6. Setup systemd service (see deploy-python.sh for service file)
```

## SSL Certificate (Optional)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate (if you have a domain)
sudo certbot --nginx -d your-domain.com
```

## Monitoring

```bash
# Check system resources
htop

# Check disk space
df -h

# Check memory usage
free -h

# Check network connections
sudo netstat -tlnp | grep 8765
```

This approach gives you the exact same experience as running locally, but with production reliability! 