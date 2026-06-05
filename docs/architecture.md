\# SecureApp — System Architecture



\## Architecture Overview

Internet

│

▼

AWS Security Group (secureapp-sg)

Ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)

│

▼

EC2 Instance — Ubuntu 24.04 (t2.micro)

IP: 13.234.225.107

Region: ap-south-1 (Mumbai)

│

├── Nginx (Port 80/443)

│   ├── HTTP → HTTPS redirect

│   ├── SSL/TLS termination

│   ├── Security headers

│   └── Reverse proxy to Gunicorn

│

├── Gunicorn (Unix socket)

│   └── Flask Application

│           ├── User authentication (bcrypt)

│           ├── JWT tokens

│           ├── Rate limiting

│           └── SQLAlchemy ORM

│

└── AWS RDS MySQL (secureapp-db)

Endpoint: secureapp-db.c34iggw2e8lx.ap-south-1.rds.amazonaws.com

Port: 3306

Private subnet only — not publicly accessible



\## AWS Services Used



| Service | Purpose |

|---------|---------|

| EC2 (t2.micro) | Web/App server |

| RDS MySQL (db.t4g.micro) | Production database |

| S3 (secureapp-backups-pranav-950639281860-ap-south-1-an) | Database backups |

| CloudWatch | Monitoring and logging |

| VPC (webadmin-vpc) | Network isolation |

| Security Groups | Firewall rules |



\## Network Architecture

VPC: webadmin-vpc (10.0.0.0/16)

│

├── Public Subnet: webadmin-subnet (10.0.1.0/24) — ap-south-1a

│   └── EC2 Instance (web server)

│

└── Private Subnets (RDS):

├── webadmin-subnet (10.0.1.0/24) — ap-south-1a

└── webadmin-subnet-1b (10.0.2.0/24) — ap-south-1b

└── RDS MySQL (database)



\## Security Layers



1\. AWS Security Groups — network firewall

2\. UFW — host firewall (ports 22, 80, 443)

3\. fail2ban — SSH brute force protection

4\. Nginx — security headers, HTTPS

5\. Flask-Talisman — HTTP security headers

6\. Flask-Limiter — API rate limiting

7\. bcrypt — password hashing

8\. SQLAlchemy ORM — SQL injection prevention

9\. RDS in private subnet — database not exposed to internet



\## CI/CD Pipeline

Developer pushes to GitHub (main branch)

│

▼

GitHub Actions triggered automatically

│

├── Job 1: TEST

│   ├── Install Python dependencies

│   └── Run Bandit security scan

│

├── Job 2: BUILD

│   └── Build Docker image (verify containerization works)

│

└── Job 3: DEPLOY

└── SSH to EC2

├── git pull latest code

├── pip install new dependencies

└── restart Gunicorn + Nginx

