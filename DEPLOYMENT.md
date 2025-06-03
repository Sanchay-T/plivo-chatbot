# DigitalOcean Deployment Guide

## Prerequisites

1. **DigitalOcean Account** with a droplet (Ubuntu 20.04+ recommended)
2. **Domain name** (optional but recommended) pointing to your droplet
3. **API Keys** for:
   - Plivo (Auth ID & Token)
   - OpenAI
   - Deepgram
   - Cartesia

## Step-by-Step Deployment

### 1. Create DigitalOcean Droplet

**Recommended Specifications:**
- **OS**: Ubuntu 22.04 LTS
- **Size**: Basic droplet, 2GB RAM, 1 vCPU ($12/month)
- **Region**: Choose closest to your target audience
- **Additional Options**: 
  - Enable monitoring
  - Add SSH key for secure access

### 2. Initial Server Setup

```bash
# Connect to your droplet
ssh root@your_droplet_ip

# Create a new user (optional but recommended)
adduser plivo
usermod -aG sudo plivo
su - plivo
```

### 3. Deploy the Application

```bash
# Download and run the deployment script
curl -fsSL https://raw.githubusercontent.com/Sanchay-T/plivo-chatbot/main/deploy.sh -o deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### 4. Configure Environment Variables

```bash
# Edit the environment file
nano .env

# Fill in your actual values:
PLIVO_AUTH_ID=your_actual_plivo_auth_id
PLIVO_AUTH_TOKEN=your_actual_plivo_auth_token
OPENAI_API_KEY=your_actual_openai_api_key
DEEPGRAM_API_KEY=your_actual_deepgram_api_key
CARTESIA_API_KEY=your_actual_cartesia_api_key
SERVER_URL=your-domain.com  # or your droplet IP
```

### 5. Start the Application

```bash
# Start the application
docker-compose up -d

# Check if it's running
docker-compose ps
docker-compose logs -f
```

### 6. Configure Domain (Optional)

If you have a domain name:

```bash
# Install Nginx
sudo apt install nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/plivo-chatbot
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/plivo-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL Certificate (Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## Production Checklist

### Security
- [ ] Firewall configured (ports 22, 80, 443, 8765)
- [ ] SSH key authentication enabled
- [ ] Regular security updates scheduled
- [ ] Environment variables secured

### Monitoring
- [ ] Application logs monitored
- [ ] Health checks configured
- [ ] Backup strategy in place
- [ ] Monitoring alerts set up

### Performance
- [ ] Resource usage monitored
- [ ] Auto-restart on failure configured
- [ ] Load balancing (if needed)

## Useful Commands

```bash
# View application logs
docker-compose logs -f

# Restart the application
docker-compose restart

# Stop the application
docker-compose down

# Update the application
git pull origin main
docker-compose build --no-cache
docker-compose up -d

# Check system resources
htop
df -h
free -h

# Check open ports
sudo netstat -tlnp
```

## Troubleshooting

### Common Issues

1. **Port 8765 already in use**
   ```bash
   sudo lsof -i :8765
   sudo kill -9 <PID>
   ```

2. **Docker permission denied**
   ```bash
   sudo usermod -aG docker $USER
   # Log out and log back in
   ```

3. **Environment variables not loaded**
   ```bash
   # Check if .env file exists and has correct values
   cat .env
   docker-compose down && docker-compose up -d
   ```

4. **WebSocket connection issues**
   - Ensure SERVER_URL in .env matches your actual domain/IP
   - Check firewall settings
   - Verify Nginx WebSocket proxy configuration

### Logs Location
- Application logs: `docker-compose logs`
- Nginx logs: `/var/log/nginx/`
- System logs: `journalctl -u docker`

## Scaling Considerations

For high-traffic scenarios:
- Use DigitalOcean Load Balancer
- Multiple droplets with shared database
- Redis for session management
- CDN for static assets

## Support

If you encounter issues:
1. Check the logs first
2. Verify all environment variables
3. Ensure all required ports are open
4. Check DigitalOcean droplet resources 