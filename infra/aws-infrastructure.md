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
| Key Pair | secureapp-key |

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
| Purpose | MySQL database backups |
| Public Access | Blocked |

## VPC Configuration
| Setting | Value |
|---------|-------|
| VPC Name | webadmin-vpc |
| CIDR | 10.0.0.0/16 |
| Subnet 1 | webadmin-subnet (10.0.1.0/24) — ap-south-1a |
| Subnet 2 | webadmin-subnet-1b (10.0.2.0/24) — ap-south-1b |

## DB Subnet Groups
| Name | Created By | Status |
|------|-----------|--------|
| secureapp-db-subnet-group | Manually created | Complete |
| rds-ec2-db-subnet-group-1 | Auto-created by AWS when connecting EC2 to RDS | Complete |

RDS uses rds-ec2-db-subnet-group-1 (auto-created). Both are in webadmin-vpc.

## Security Groups
### EC2 Security Group (secureapp-sg)
| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | TCP | Anywhere | SSH |
| 80 | TCP | Anywhere | HTTP |
| 443 | TCP | Anywhere | HTTPS |

### RDS Security Group (rds-ec2-1)
Auto-created by AWS when EC2 was connected to RDS during setup.
| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 3306 | TCP | EC2 security group only | MySQL from EC2 only |

## IAM Role
| Role | Policies Attached | Purpose |
|------|------------------|---------|
| secureapp-cloudwatch-role | CloudWatchAgentServerPolicy, AmazonS3FullAccess | CloudWatch metrics + S3 backup access |

Note: No separate IAM user was created. S3 and CloudWatch access is provided
via the IAM role attached directly to the EC2 instance — this is AWS best practice
as it avoids storing access keys on the server.

## Software Stack on EC2
- Python 3.12 + Flask
- Gunicorn (WSGI production server)
- Nginx (reverse proxy + SSL)
- Docker (containerization)
- fail2ban (brute force protection)
- UFW (host firewall)
- AWS CloudWatch Agent (monitoring)
- AWS CLI v2 (2.34.61)

## Note on Infrastructure as Code
Infrastructure as Code using Terraform/CloudFormation
is planned for future iterations. Current infrastructure
was provisioned via AWS Console following security best practices.
