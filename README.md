\# Cloud-Based Secure Web Application (DevSecOps)



A secure, scalable and highly available task management web application deployed on AWS with DevSecOps best practices.



\## Tech Stack

\- \*\*Backend:\*\* Python Flask

\- \*\*Database:\*\* MySQL (AWS RDS)

\- \*\*Server:\*\* Ubuntu EC2 + Nginx

\- \*\*Security:\*\* bcrypt, JWT, rate limiting, HTTPS

\- \*\*DevOps:\*\* Docker, GitHub Actions CI/CD

\- \*\*Monitoring:\*\* AWS CloudWatch



\## Features

\- User registration and login with bcrypt password hashing

\- Role-based access control (User and Admin)

\- Task management with priorities and deadlines

\- Admin dashboard with user management

\- Overdue task detection

\- Rate limiting and brute force protection



\## Setup Instructions



\### 1. Clone the repository

git clone https://github.com/YOUR\_USERNAME/cloud-secure-web-app.git



\### 2. Create virtual environment

python -m venv venv

venv\\Scripts\\activate



\### 3. Install dependencies

pip install -r src/requirements.txt



\### 4. Run the application

cd src

python run.py



\## Project Structure

\- `src/` - Flask application source code

\- `docs/` - Architecture diagrams and documentation

\- `infra/` - AWS infrastructure configuration

\- `scripts/` - Backup and deployment scripts

