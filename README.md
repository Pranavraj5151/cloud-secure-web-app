# 🔐 SecureApp — Cloud-Based Secure Task Manager

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-green?logo=flask)
![AWS](https://img.shields.io/badge/AWS-EC2%20%7C%20RDS%20%7C%20S3-orange?logo=amazonaws)
![MySQL](https://img.shields.io/badge/Database-MySQL%208.0-blue?logo=mysql)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue?logo=docker)
![Nginx](https://img.shields.io/badge/Nginx-Reverse%20Proxy-green?logo=nginx)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-black?logo=githubactions)

A secure, scalable and production-ready task management web application
built and deployed on AWS using DevSecOps best practices.

---

## 🌐 Live Application
**URL:** http://13.234.225.107

---

## 🚀 Features
- ✅ User Registration and Login with bcrypt password hashing
- ✅ Role-Based Access Control (User and Admin)
- ✅ Full Task Management — Create, Read, Update, Delete
- ✅ Task priorities (High, Medium, Low) and deadlines
- ✅ Overdue task detection
- ✅ Admin dashboard with user management and statistics
- ✅ Rate limiting and brute force protection
- ✅ Security headers (X-Frame-Options, CSP, HSTS)
- ✅ Docker containerization
- ✅ Automated CI/CD pipeline with GitHub Actions
- ✅ AWS RDS MySQL production database
- ✅ S3 automated backups
- ✅ CloudWatch monitoring

---

## 🏗️ Architecture
Internet → AWS Security Group → EC2 Ubuntu 24.04
│
Nginx (80/443)
│
Gunicorn (WSGI)
│
Flask Application
│
AWS RDS MySQL

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 + Flask |
| Database | AWS RDS MySQL 8.0 |
| Web Server | Nginx + Gunicorn |
| Cloud | AWS EC2, RDS, S3, CloudWatch |
| Security | bcrypt, JWT, fail2ban, UFW |
| DevOps | Docker, GitHub Actions CI/CD |
| Monitoring | AWS CloudWatch |

---

## 🔐 Security Implementation

| Feature | Implementation |
|---------|---------------|
| Password Hashing | bcrypt via Flask-Bcrypt |
| Rate Limiting | Flask-Limiter (10 req/min) |
| SQL Injection Prevention | SQLAlchemy ORM |
| XSS Protection | Jinja2 auto-escaping |
| Security Headers | Flask-Talisman + Nginx |
| Brute Force Protection | fail2ban |
| Firewall | UFW + AWS Security Groups |
| SSH Hardening | Key-based auth only |
| Database Security | RDS in private subnet |
| HTTPS | Self-signed SSL certificate |

---

## ⚙️ CI/CD Pipeline
Push to main branch
│
├── TEST — Python deps + Bandit security scan
├── BUILD — Docker image build verification
└── DEPLOY — SSH to EC2 → git pull → restart services

---

## 🚀 Local Setup

```bash
git clone https://github.com/Pranavraj5151/cloud-secure-web-app.git
cd cloud-secure-web-app/src
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Visit `http://localhost:5000`

---

## 🐳 Docker

```bash
cd src
docker build -t secureapp .
docker run -p 5000:5000 secureapp
```

---

## 📁 Project Structure
cloud-secure-web-app/
├── src/                    # Flask application
│   ├── app/
│   │   ├── init.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── templates/
│   │   └── static/css/
│   ├── config.py
│   ├── run.py
│   ├── Dockerfile
│   └── requirements.txt
├── docs/                   # Architecture documentation
├── infra/                  # AWS infrastructure docs
├── scripts/                # Backup scripts
└── .github/workflows/      # CI/CD pipeline

---

## 👨‍💻 Author
**Pranav Raj**
BCA — Mar Augusthinose College, Ramapuram
FYUGP Summer Internship — IPSR Solutions Ltd