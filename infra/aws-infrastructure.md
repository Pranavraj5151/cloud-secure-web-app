# AWS Infrastructure Documentation

## Overview
This document describes the AWS infrastructure used for SecureApp.
Infrastructure was provisioned manually via AWS Console following
least-privilege security principles.

## EC2 Instances

### Application Server
| Setting | Value |
|---------|-------|
| Name | secureapp-server |
| Instance ID | i-08d6c1dfa47beb702 |
| Instance Type | t2.micro (Free Tier) |
| OS | Ubuntu Server 24.04 LTS |
| Region | ap-south-1 (Mumbai) |
| Public IP | 13.234.225.107 |
| Private IP | 10.0.1.65 |
| Subnet | webadmin-subnet (public) |

### Bastion Host
| Setting | Value |
|---------|-------|
| Name | bastion-host |
| Instance Type | t3.micro (Free Tier) |
| OS | Ubuntu Server 24.04 LTS |
| Public IP | 13.233.128.69 |
| Subnet | webadmin-subnet (public) |
| Security Group | bastion-sg (SSH 22 from anywhere) |
| Purpose | Jump host for secure SSH access to application server |

CI/CD deployment (GitHub Actions) connects to the application server's
private IP (10.0.1.65) via the bastion host using ProxyCommand-based
SSH tunnelling, demonstrating a bastion access pattern in the
deployment pipeline.

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
| Connectivity | Public |
| Status | Available |

## Private Subnet & Routing (Migration-Ready Infrastructure)
| Setting | Value |
|---------|-------|
| Subnet Name | secureapp-private |
| CIDR | 10.0.10.0/24 |
| Availability Zone | ap-south-1a |
| Route Table | secureapp-private-rt |
| Route | 0.0.0.0/0 → secureapp-nat (NAT Gateway) |

A dedicated private subnet and route table have been provisioned,
routing outbound traffic through the NAT Gateway. This infrastructure
supports deploying application instances without direct internet
exposure, accessible only via the ALB and the bastion host.

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
| DB Subnet Group | secureapp-db-subnet-group |
| Option Group | default:mysql-8-0 |

### DB Subnet Group
The RDS instance is associated with a dedicated DB Subnet Group
(`secureapp-db-subnet-group`) spanning two private subnets across
availability zones, ensuring the database tier remains isolated
from public internet access at all times.

### Option Group
RDS uses the default MySQL 8.0 option group (`default:mysql-8-0`),
providing the standard engine feature set without enabling
unnecessary database options, minimising the attack surface at
the database engine level.

## S3 Bucket
| Setting | Value |
|---------|-------|
| Bucket Name | secureapp-backups-pranav-950639281860-ap-south-1-an |
| Region | ap-south-1 |
| Purpose | MySQL database backups + profile pictures |
| Versioning | Enabled |
| Lifecycle Policy | Transition backups/ to Standard-IA after 30 days |
| Public Access | Partially blocked (profiles/ folder public read only) |

## VPC Configuration
| Setting | Value |
|---------|-------|
| VPC Name | webadmin-vpc |
| CIDR | 10.0.0.0/16 |
| Internet Gateway | igw-082694b706a6564fd (Attached) |
| Public Subnet 1 | webadmin-subnet (10.0.1.0/24) — ap-south-1a |
| Public Subnet 2 | webadmin-subnet-1b (10.0.2.0/24) — ap-south-1b |
| Private Subnet (RDS) 1 | RDS-Pvt-subnet-1 (10.0.0.128/25) — ap-south-1a |
| Private Subnet (RDS) 2 | RDS-Pvt-subnet-2 (10.0.3.0/25) — ap-south-1b |
| Private Subnet (App) | secureapp-private (10.0.10.0/24) — ap-south-1a |
| NAT Gateway | secureapp-nat (Elastic IP: 13.126.106.215) |

### Internet Gateway
The Internet Gateway (`igw-082694b706a6564fd`) is attached to
`webadmin-vpc` and provides the entry/exit point for internet-bound
traffic for resources in the public subnets — specifically the ALB,
the application EC2 instance, NAT Gateway, and the bastion host.

### Route Tables
| Route Table | Associated Subnets | Routes |
|-------------|---------------------|--------|
| rtb-03b140ed6fd8ae3b4 | webadmin-subnet, webadmin-subnet-1b | 10.0.0.0/16 → local, 0.0.0.0/0 → Internet Gateway |
| secureapp-private-rt | secureapp-private | 10.0.0.0/16 → local, 0.0.0.0/0 → NAT Gateway |

The public route table directs internet-bound traffic through the
Internet Gateway, while the private route table directs outbound
traffic for the private application subnet through the NAT Gateway,
keeping that tier isolated from direct inbound internet access.

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

### Bastion Security Group (bastion-sg)
| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | TCP | Anywhere | SSH jump access |

### RDS Security Group (rds-ec2-1)
| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 3306 | TCP | EC2 security group only | MySQL from EC2 only |

## DNS — Route 53
A Route 53 hosted zone has been configured to provide DNS
management capability for the application, supporting future
domain-based routing to the Application Load Balancer.

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
| SecureApp-Disk-Space | disk_used_percent | > 85% | SNS email alert |

All alarms notify via SNS topic `secureapp-alerts`.

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

## CI/CD Deployment Path
GitHub Actions deploys to the application server's private IP
(10.0.1.65) through the bastion host (13.233.128.69) using
SSH ProxyCommand tunnelling, ensuring deployment traffic follows
the same secure access pattern as administrative SSH access.
