# Rays Madrasah SaaS - Build & Deployment Guide

This guide provides a comprehensive, step-by-step walkthrough for building and deploying the **Rays Madrasah Management System** as a production-ready SaaS application.

---

## 🚀 Phase 1: Server Preparation

Before starting, ensure your Linux server (Ubuntu/Debian recommended) is up to date and has the necessary dependencies.

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Required Packages
```bash
sudo apt install -y python3-pip python3-venv nginx mysql-server libmysqlclient-dev pkg-config git curl
```

### 3. Secure MySQL Installation
```bash
sudo mysql_secure_installation
```

---

## 📂 Phase 2: Project Setup

### 1. Create Application Directory
```bash
sudo mkdir -p /var/www/RaysTech
sudo chown -R $USER:$USER /var/www/RaysTech
cd /var/www/RaysTech
```

### 2. Clone the Repository
```bash
git clone <your-repository-url> madrasah_mgmt
cd madrasah_mgmt
```

### 3. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn pymysql
```

---

## ⚙️ Phase 3: Configuration

### 1. Setup Environment Variables
Create a `.env` file in the root directory:
```bash
cp .env.example .env
nano .env
```

**Key Variables to Set:**
- `SECRET_KEY`: A long random string.
- `DATABASE_URL`: `mysql+pymysql://user:password@localhost/madrasah_db`
- `AI_API_KEY`: Your OpenAI/Gemini API key.
- `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD`: For notifications and backups.

### 2. Create the Database
```bash
sudo mysql -u root -p
```
```sql
CREATE DATABASE madrasah_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'madrasah_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON madrasah_db.* TO 'madrasah_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## 🗄️ Phase 4: Database & Permissions

### 1. Initialize Migrations
```bash
flask db upgrade
```

### 2. Seed Permissions & Admin
Run the seeding scripts to ensure the system has the necessary roles:
```bash
python3 scripts/seed_permissions.py
```

---

## 🌐 Phase 5: Production Deployment (Nginx & Gunicorn)

### 1. Create Systemd Service
Create `/etc/systemd/system/madrasah.service`:
```ini
[Unit]
Description=Gunicorn instance to serve Madrasah App
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/RaysTech/madrasah_mgmt
Environment="PATH=/var/www/RaysTech/madrasah_mgmt/venv/bin"
ExecStart=/var/www/RaysTech/madrasah_mgmt/venv/bin/gunicorn --workers 3 --bind unix:madrasah.sock -m 007 run:app

[Install]
WantedBy=multi-user.target
```

### 2. Configure Nginx
Create `/etc/nginx/sites-available/madrasah`:
```nginx
server {
    listen 80;
    server_name yourdomain.com; # Or sub.yourdomain.com

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/RaysTech/madrasah_mgmt/madrasah.sock;
    }

    location /static {
        alias /var/www/RaysTech/madrasah_mgmt/app/static;
        expires 30d;
    }
}
```

### 3. Enable and Start Services
```bash
sudo ln -s /etc/nginx/sites-available/madrasah /etc/nginx/sites-enabled
sudo systemctl start madrasah
sudo systemctl enable madrasah
sudo systemctl restart nginx
```

---

## 🔒 Phase 6: SSL Configuration

Secure your SaaS with HTTPS using Certbot:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

---

## 🏢 Phase 7: Scaling for SaaS (Multi-Tenancy)

To host multiple Madrasahs (clients), you have two primary options:

### Option A: Multiple Instances (Recommended for Privacy)
Each client gets their own folder, database, and systemd service.
1. Duplicate the folder: `cp -r madrasah_mgmt madrasah_client2`.
2. Create a new database for `client2`.
3. Update `.env` in `madrasah_client2`.
4. Create a new systemd service (e.g., `madrasah_client2.service`) with a different `.sock` file.
5. Add a new Nginx `server` block or `location` block for the new client.

### Option B: Path-Based Routing (Single IP)
As seen in your configuration, you can use paths:
```nginx
location /madrasha {
    include proxy_params;
    proxy_pass http://unix:/var/www/RaysTech/madrasah_mgmt/madrasah.sock;
}

location /college {
    include proxy_params;
    proxy_pass http://unix:/var/www/RaysTech/college_mgmt/college.sock;
}
```

---

## 🛠️ Maintenance Utilities
Active scripts available in `scripts/`:
- **Backup**: `bash scripts/backup_database.sh`
- **Security Audit**: `python3 scripts/security_audit.py`
- **Translations**: `python3 scripts/check_translations.py`
