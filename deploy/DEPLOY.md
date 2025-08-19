# Quick AWS Deployment Guide

## Option 1: One-Command Deployment

```bash
cd /root/compliant-one/deploy
./quick-deploy.sh
```

This will:
- Install AWS CLI if needed
- Configure AWS credentials (if needed)
- Create EC2 key pair
- Launch EC2 instance
- Deploy your application
- Provide access URL

## Option 2: Manual AWS Console Deployment

1. **Go to AWS EC2 Console**
2. **Launch Instance**:
   - AMI: Amazon Linux 2
   - Instance Type: t3.medium
   - Key Pair: Create new or use existing
   - Security Group: Allow ports 22, 80, 443

3. **User Data Script**:
   Copy content from `user-data-simple.sh` into User Data field

4. **Launch and Wait**:
   - Instance will auto-install and start the application
   - Access via public IP on port 80

## Option 3: Docker Hub Deployment

```bash
# Build and push to Docker Hub
docker build -t your-username/compliant-one .
docker push your-username/compliant-one

# Then deploy on any server:
docker run -d -p 80:8000 your-username/compliant-one
```

## Requirements

- AWS Account
- AWS CLI (auto-installed by script)
- Basic permissions for EC2, Security Groups

## Access Your App

After deployment (5-10 minutes):
- Website: `http://YOUR-EC2-PUBLIC-IP`
- SSH: `ssh -i compliant-one-key.pem ec2-user@YOUR-EC2-PUBLIC-IP`

## Troubleshooting

```bash
# Check application logs
ssh -i compliant-one-key.pem ec2-user@YOUR-IP
sudo docker-compose logs -f
```