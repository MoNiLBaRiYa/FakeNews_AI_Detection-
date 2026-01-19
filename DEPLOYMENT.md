# Deployment Guide

This guide covers various deployment options for the Fake News Detection System.

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Checklist](#production-checklist)

## Local Development

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
copy .env.example .env
# Edit .env with your configuration

# Start MongoDB
net start MongoDB

# Run application
cd Backend
python app.py
```

Visit: http://localhost:5000

## Docker Deployment

### Prerequisites
- Docker Desktop installed
- Docker Compose installed

### Build and Run
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Access Application
- Application: http://localhost:5000
- MongoDB: localhost:27017

### Docker Commands
```bash
# Rebuild after code changes
docker-compose up -d --build

# View running containers
docker ps

# Execute commands in container
docker exec -it fakenews_app bash

# View MongoDB data
docker exec -it fakenews_mongodb mongosh
```

## Cloud Deployment

### Heroku

1. **Install Heroku CLI**
```bash
npm install -g heroku
```

2. **Login and Create App**
```bash
heroku login
heroku create your-app-name
```

3. **Add MongoDB**
```bash
heroku addons:create mongolab:sandbox
```

4. **Set Environment Variables**
```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
heroku config:set NEWSAPI_KEY=your-key
heroku config:set NEWSDATA_KEY=your-key
```

5. **Create Procfile**
```
web: gunicorn Backend.app:app
```

6. **Deploy**
```bash
git push heroku main
heroku open
```

### AWS EC2

1. **Launch EC2 Instance**
- Ubuntu 22.04 LTS
- t2.micro (free tier)
- Open ports: 22, 80, 443, 5000

2. **Connect and Setup**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv mongodb -y

# Clone repository
git clone your-repo-url
cd your-repo

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit configuration
```

3. **Setup Nginx**
```bash
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/fakenews
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/fakenews /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **Setup Systemd Service**
```bash
sudo nano /etc/systemd/system/fakenews.service
```

```ini
[Unit]
Description=Fake News Detection App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/your-repo
Environment="PATH=/home/ubuntu/your-repo/venv/bin"
ExecStart=/home/ubuntu/your-repo/venv/bin/python Backend/app.py

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl daemon-reload
sudo systemctl start fakenews
sudo systemctl enable fakenews
sudo systemctl status fakenews
```

5. **Setup SSL (Optional)**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### Google Cloud Platform

1. **Install gcloud CLI**
```bash
curl https://sdk.cloud.google.com | bash
gcloud init
```

2. **Create app.yaml**
```yaml
runtime: python311
entrypoint: gunicorn -b :$PORT Backend.app:app

env_variables:
  FLASK_ENV: "production"
  SECRET_KEY: "your-secret-key"
  MONGODB_URI: "your-mongodb-uri"
  NEWSAPI_KEY: "your-key"
  NEWSDATA_KEY: "your-key"

automatic_scaling:
  min_instances: 1
  max_instances: 10
```

3. **Deploy**
```bash
gcloud app deploy
gcloud app browse
```

### DigitalOcean

1. **Create Droplet**
- Ubuntu 22.04
- Basic plan ($6/month)

2. **Follow AWS EC2 steps** (similar process)

3. **Or use App Platform**
- Connect GitHub repository
- Configure environment variables
- Deploy automatically

## Production Checklist

### Security
- [ ] Change SECRET_KEY to strong random value
- [ ] Enable HTTPS/SSL
- [ ] Set SESSION_COOKIE_SECURE=True
- [ ] Configure firewall (UFW/Security Groups)
- [ ] Disable debug mode (FLASK_ENV=production)
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Regular security updates

### Performance
- [ ] Use production WSGI server (Gunicorn/uWSGI)
- [ ] Enable caching
- [ ] Configure CDN for static files
- [ ] Optimize database indexes
- [ ] Monitor resource usage
- [ ] Set up load balancing (if needed)

### Monitoring
- [ ] Setup logging (Sentry, LogDNA)
- [ ] Configure uptime monitoring
- [ ] Setup error tracking
- [ ] Monitor API rate limits
- [ ] Database backup strategy

### Database
- [ ] Use MongoDB Atlas (managed)
- [ ] Configure backups
- [ ] Set up replication
- [ ] Monitor performance
- [ ] Secure with authentication

### API Keys
- [ ] Get production API keys
- [ ] Monitor usage limits
- [ ] Setup billing alerts
- [ ] Consider caching API responses

### Testing
- [ ] Run all tests
- [ ] Load testing
- [ ] Security scanning
- [ ] Cross-browser testing
- [ ] Mobile responsiveness

### Documentation
- [ ] Update README
- [ ] API documentation
- [ ] Deployment notes
- [ ] Troubleshooting guide

## Environment Variables

Required for production:

```bash
# Flask
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<strong-random-key>

# Database
MONGODB_URI=<your-mongodb-uri>
DATABASE_NAME=user_auth_db

# API Keys
NEWSAPI_KEY=<your-key>
NEWSDATA_KEY=<your-key>

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Rate Limiting
RATELIMIT_ENABLED=True
RATELIMIT_DEFAULT=100 per hour
```

## Monitoring Commands

```bash
# Check application logs
tail -f app.log

# Monitor system resources
htop

# Check MongoDB status
sudo systemctl status mongodb

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Check application status
sudo systemctl status fakenews
```

## Backup Strategy

### Database Backup
```bash
# Manual backup
mongodump --uri="mongodb://localhost:27017/user_auth_db" --out=/backup/

# Automated backup (cron)
0 2 * * * mongodump --uri="mongodb://localhost:27017/user_auth_db" --out=/backup/$(date +\%Y\%m\%d)
```

### Application Backup
```bash
# Backup code and configuration
tar -czf backup-$(date +%Y%m%d).tar.gz /path/to/app
```

## Troubleshooting

### Application won't start
```bash
# Check logs
tail -f app.log

# Check Python errors
python Backend/app.py

# Verify dependencies
pip list
```

### MongoDB connection issues
```bash
# Check MongoDB status
sudo systemctl status mongodb

# Test connection
mongosh

# Check firewall
sudo ufw status
```

### High memory usage
```bash
# Monitor processes
htop

# Restart application
sudo systemctl restart fakenews

# Check for memory leaks
```

## Scaling

### Horizontal Scaling
- Use load balancer (Nginx, HAProxy)
- Deploy multiple app instances
- Use Redis for session storage
- Implement message queue (Celery)

### Vertical Scaling
- Upgrade server resources
- Optimize database queries
- Enable caching
- Use CDN for static files

## Support

For deployment issues:
1. Check logs first
2. Review documentation
3. Search GitHub issues
4. Open new issue with details

---

**Note**: Always test deployment in staging environment before production!
