# AWS Infrastructure Documentation

## Overview
This document describes the AWS infrastructure used for SecureApp.
Infrastructure was provisioned manually via AWS Console following
least-privilege security principles.

## EC2 Instance
| Setting | Value |
|---------|-------|
| Instance ID | i-08d6c1dfa47beb702 |
| Instance Type | t2.micro (Free Tier) |
| OS | Ubuntu Server 24.04 LTS |
| Region | ap-south-1 (Mumbai) |
| Public IP | 13.234.225.107 |
| Private IP | 10.0.1.65 |
| Subnet | webadmin-subnet (public) |

## Application Load Balancer
| Setting | Value |
|---------|-------|
| Name | secureapp-alb |
| DNS | secureapp-alb-2065264995.ap-south-1.elb.amazonaws.com |
| Scheme | Internet-facing |
| Subnets | webadmin-subnet (ap-south-1a), webadmin-subnet-1b (ap-south-1b) |
| Security Group | secureapp-alb-sg (HTTP 80, HTTPS 443) |
| Target Group | secureapp-tg (HTTP:80, health check /health) |
| Status | Active, Target Healthy |

## NAT Gateway
| Setting | Value |
|---------|-------|
| Name | secureapp-nat |
| Subnet | webadmin-subnet (public) |
| Elastic IP | 13.126.106.215 |
| Status | Available |

## RDS Database
| Setting | Value |
|---------|-------|
| Identifier | secureapp-db |
| Engine | MySQL 8.0 Community |
| Instance Class | db.t4g.micro (Free Tier) |
| Endpoint | secureapp-db.c34iggw2e8lx.ap-south-1.rds.amazonaws.com |
| Port | 3306 |
| Database Name | secureapp |
| Public Access | No (private subnet only) |

## S3 Bucket
| Setting | Value |
|---------|-------|
| Bucket Name | secureapp-backups-pranav-950639281860-ap-south-1-an |
| Region | ap-south-1 |
| Purpose | MySQL database backups + profile pictures |
| Public Access | Partially blocked (profiles/ folder public read) |

## VPC Configuration
| Setting | Value |
|---------|-------|
| VPC Name | webadmin-vpc |
| CIDR | 10.0.0.0/16 |
| Public Subnet 1 | webadmin-subnet (10.0.1.0/24) — ap-south-1a |
| Public Subnet 2 | webadmin-subnet-1b (10.0.2.0/24) — ap-south-1b |
| Private Subnet 1 | RDS-Pvt-subnet-1 (10.0.0.128/25) — ap-south-1a |
| Private Subnet 2 | RDS-Pvt-subnet-2 (10.0.3.0/25) — ap-south-1b |
| Internet Gateway | igw-082694b706a6564fd |
| NAT Gateway | secureapp-nat (Elastic IP: 13.126.106.215) |

## Security Groups
### EC2 Security Group (secureapp-sg)
| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | TCP | Anywhere | SSH |
| 80 | TCP | Anywhere | HTTP |
| 443 | TCP | Anywhere | HTTPS |
| 5000 | TCP | Anywhere | Flask dev port |

### ALB Security Group (secureapp-alb-sg)
| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 80 | TCP | 0.0.0.0/0 | HTTP from internet |
| 443 | TCP | 0.0.0.0/0 | HTTPS from internet |

### RDS Security Group (rds-ec2-1)
| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 3306 | TCP | EC2 security group only | MySQL from EC2 only |

## IAM Role
| Role | Policies | Purpose |
|------|----------|---------|
| secureapp-cloudwatch-role | CloudWatchAgentServerPolicy, AmazonS3FullAccess | CloudWatch + S3 access via EC2 role |

## CloudWatch Alarms
| Alarm Name | Metric | Threshold | Action |
|------------|--------|-----------|--------|
| SecureApp-High-CPU | CPUUtilization | > 80% | SNS email alert |
| SecureApp-High-Memory | mem_used_percent | > 80% | SNS email alert |
| SecureApp-Health-Check | HealthyHostCount | < 1 | SNS email alert |
| SecureApp-Failed-Logins | FailedLoginAttempts | > 5 in 5 min | SNS email alert |

## CloudWatch Log Groups
| Log Group | Source |
|-----------|--------|
| secureapp-nginx-access | /var/log/nginx/access.log |
| secureapp-nginx-error | /var/log/nginx/error.log |
| secureapp-app-logs | /var/log/syslog (contains FAILED_LOGIN_ATTEMPT events) |

## Software Stack on EC2
- Python 3.12 + Flask
- Gunicorn (WSGI, 3 workers, Unix socket)
- Nginx (reverse proxy, SSL, security headers)
- Docker (containerization, image: secureapp:latest)
- fail2ban (brute force protection)
- UFW (host firewall)
- AWS CloudWatch Agent (monitoring)
- AWS CLI v2

## Note on Infrastructure as Code
Infrastructure as Code using Terraform/CloudFormation
is planned for future iterations. Current infrastructure
was provisioned via AWS Console following security best practices.
