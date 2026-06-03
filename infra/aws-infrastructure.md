\# AWS Infrastructure Documentation



\## Overview

This document describes the AWS infrastructure used for SecureApp.

Infrastructure was provisioned manually via AWS Console following

least-privilege security principles.



\## EC2 Instance

| Setting | Value |

|---------|-------|

| Instance ID | i-08d6c1dfa47beb702 |

| Instance Type | t2.micro (Free Tier) |

| OS | Ubuntu Server 24.04 LTS |

| Region | ap-south-1 (Mumbai) |

| Public IP | 13.234.225.107 |

| Key Pair | secureapp-key |



\## RDS Database

| Setting | Value |

|---------|-------|

| Identifier | secureapp-db |

| Engine | MySQL 8.0 |

| Instance Class | db.t4g.micro (Free Tier) |

| Endpoint | secureapp-db.c34iggw2e8lx.ap-south-1.rds.amazonaws.com |

| Port | 3306 |

| Database Name | secureapp |

| Public Access | No (private subnet only) |



\## S3 Bucket

| Setting | Value |

|---------|-------|

| Bucket Name | secureapp-backups-pranav |

| Region | ap-south-1 |

| Purpose | Database backups |

| Public Access | Blocked |



\## VPC Configuration

| Setting | Value |

|---------|-------|

| VPC Name | webadmin-vpc |

| CIDR | 10.0.0.0/16 |

| Subnet 1 | webadmin-subnet (10.0.1.0/24) ap-south-1a |

| Subnet 2 | webadmin-subnet-1b (10.0.2.0/24) ap-south-1b |



\## Security Groups

\### secureapp-sg (EC2)

| Port | Protocol | Source | Purpose |

|------|----------|--------|---------|

| 22 | TCP | Anywhere | SSH |

| 80 | TCP | Anywhere | HTTP |

| 443 | TCP | Anywhere | HTTPS |



\### secureapp-rds-sg (RDS)

| Port | Protocol | Source | Purpose |

|------|----------|--------|---------|

| 3306 | TCP | secureapp-sg | MySQL from EC2 only |



\## IAM Roles

| Role | Policy | Purpose |

|------|--------|---------|

| secureapp-cloudwatch-role | CloudWatchAgentServerPolicy | CloudWatch metrics |



\## Software Stack on EC2

\- Python 3.12 + Flask

\- Gunicorn (WSGI production server)

\- Nginx (reverse proxy + SSL)

\- Docker (containerization)

\- fail2ban (brute force protection)

\- UFW (host firewall)

\- AWS CloudWatch Agent (monitoring)



\## Note on Infrastructure as Code

Infrastructure as Code using Terraform/CloudFormation

is planned for future iterations. Current infrastructure

was provisioned via AWS Console following security best practices.

