# PDF Collaborator - Production Deployment Guide

## 🚀 Production Readiness Features

This application has been configured with the following production-ready features:

### ✅ **Implemented Features**
- Database-only mode (MOCK_DOCUMENTS disabled in production)
- Production security settings (HTTPS, secure cookies, CSRF protection)
- Health check endpoint for monitoring (`/health`)
- Structured logging with file output
- User authentication & authorization
- Document isolation & access control
- Email integration with Brevo SMTP

## 📋 **Pre-Deployment Checklist**

### **1. Environment Configuration**
Create a production `.env` file with these required variables:

```bash
# Environment
FLASK_ENV=production
FLASK_DEBUG=False

# Security
FLASK_SECRET_KEY=your-super-secure-secret-key-here

# Database (Supabase)
user=your_supabase_user
password=your_supabase_password
host=your_supabase_host
port=5432
dbname=postgres

# Google OAuth
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
OAUTH_REDIRECT_URI=https://yourdomain.com/auth/google/callback

# Email (Brevo)
SMTP_SERVER=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USERNAME=your_brevo_username
SMTP_PASSWORD=your_brevo_api_key
FROM_EMAIL=your_from_email@domain.com

# Optional
UPLOAD_FOLDER=/path/to/production/uploads
```

### **2. Database Setup**
Ensure your Supabase database has all required tables:

```sql
-- Run this to create tables if they don't exist
-- The application will auto-create tables on first run
```

### **3. Security Checklist**
- [ ] Generate strong `FLASK_SECRET_KEY` (32+ random characters)
- [ ] Configure HTTPS/SSL certificate
- [ ] Set up firewall rules
- [ ] Enable database connection encryption
- [ ] Configure secure headers

## 🚀 **Deployment Options**

### **Option 1: Docker Deployment**

1. **Create Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

2. **Build and run:**
```bash
docker build -t pdf-collaborator .
docker run -p 5000:5000 --env-file .env pdf-collaborator
```

### **Option 2: Platform Deployment**

#### **Heroku**
```bash
# Install Heroku CLI, then:
heroku create your-app-name
heroku config:set FLASK_ENV=production
heroku config:set FLASK_SECRET_KEY=your-secret-key
# ... set all other env variables
git push heroku main
```

#### **Railway**
```bash
railway login
railway init
railway add
# Configure environment variables in Railway dashboard
railway deploy
```

#### **DigitalOcean App Platform**
1. Connect GitHub repository
2. Configure environment variables
3. Set build command: `pip install -r requirements.txt`
4. Set run command: `gunicorn --bind 0.0.0.0:$PORT app:app`

### **Option 3: VPS/Server Deployment**

1. **Install dependencies:**
```bash
sudo apt update
sudo apt install python3 python3-pip nginx
pip3 install -r requirements.txt
pip3 install gunicorn
```

2. **Create systemd service:**
```ini
# /etc/systemd/system/pdf-collaborator.service
[Unit]
Description=PDF Collaborator Web Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/pdf-collaborator
Environment=PATH=/var/www/pdf-collaborator/venv/bin
ExecStart=/var/www/pdf-collaborator/venv/bin/gunicorn --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

3. **Configure Nginx:**
```nginx
# /etc/nginx/sites-available/pdf-collaborator
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
}
```

## 📊 **Monitoring & Maintenance**

### **Health Checks**
The application provides a health check endpoint:
```
GET /health
```

Response (healthy):
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "version": "1.0.0",
  "environment": "production",
  "services": {
    "database": "connected",
    "email": "configured"
  }
}
```

### **Logging**
Production logs are written to:
- **stdout** (for container deployments)
- **app.log** file (for server deployments)

Log format: `%(asctime)s %(levelname)s %(name)s: %(message)s`

### **Database Maintenance**
- **Backups**: Set up automated daily backups
- **Monitoring**: Monitor connection pool and query performance
- **Cleanup**: Implement document retention policies

## 🔧 **Performance Optimization**

### **Recommended Production Settings**
```python
# Add to gunicorn command
gunicorn --bind 0.0.0.0:5000 \
  --workers 4 \
  --worker-class gevent \
  --timeout 120 \
  --keep-alive 5 \
  app:app
```

### **Caching**
Consider adding Redis for:
- Session storage
- Rate limiting
- Temporary data caching

### **File Storage**
For production, move file uploads to cloud storage:
- **AWS S3**
- **Google Cloud Storage**
- **DigitalOcean Spaces**

## 🚨 **Security Considerations**

### **Required Security Headers**
Add these to your reverse proxy:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### **Rate Limiting**
Implement rate limiting for:
- Login attempts
- PDF uploads
- Email sending

### **Data Protection**
- Encrypt sensitive data at rest
- Use HTTPS for all connections
- Implement proper session management
- Regular security audits

## 📞 **Support & Troubleshooting**

### **Common Issues**

1. **Database Connection Failed**
   - Check environment variables
   - Verify network connectivity
   - Confirm database credentials

2. **Email Not Sending**
   - Verify SMTP configuration
   - Check Brevo API limits
   - Review email logs

3. **File Upload Issues**
   - Check disk space
   - Verify upload folder permissions
   - Monitor file size limits

### **Performance Monitoring**
Monitor these metrics:
- Response time
- Database query performance
- Memory usage
- Error rates
- Email delivery rates

---

## 🎉 **Ready for Production!**

Your PDF Collaborator application is now production-ready with:
- ✅ Secure configuration
- ✅ Database isolation
- ✅ Health monitoring
- ✅ Structured logging
- ✅ User authentication
- ✅ Document access control

Deploy with confidence! 🚀