#!/bin/bash
# Quick AWS Deployment Script

set -e

echo "🚀 Starting Quick AWS Deployment..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ Installing AWS CLI..."
    # Install unzip first
    sudo apt-get update && sudo apt-get install -y unzip || sudo yum install -y unzip
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    rm -rf aws awscliv2.zip
fi

# Configure AWS (if not already configured)
if ! aws sts get-caller-identity &> /dev/null; then
    echo "🔑 Please configure AWS credentials:"
    aws configure
fi

# Create key pair if it doesn't exist
KEY_NAME="compliant-one-key"
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME &> /dev/null; then
    echo "🔐 Creating EC2 key pair..."
    aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text > ${KEY_NAME}.pem
    chmod 400 ${KEY_NAME}.pem
    echo "✅ Key saved as ${KEY_NAME}.pem"
fi

AWS_REGION=${AWS_REGION:-$(aws configure get region || echo "us-east-1")}
echo "🌎 Region: $AWS_REGION"

# Resolve latest Amazon Linux 2023 AMI via SSM for the selected region
AMI_ID=$(aws ssm get-parameters --names "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64" --region "$AWS_REGION" --query 'Parameters[0].Value' --output text)
echo "🖼️ AMI: $AMI_ID"

# Ensure security group exists and capture ID
SG_ID=$(aws ec2 describe-security-groups --group-names compliant-one-sg --region "$AWS_REGION" --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || echo "")
if [ -z "$SG_ID" ] || [ "$SG_ID" = "None" ]; then
    SG_ID=$(aws ec2 create-security-group --group-name compliant-one-sg --description "Compliant-One Security Group" --region "$AWS_REGION" --query 'GroupId' --output text)
fi
echo "🛡️  Security Group: $SG_ID"

# Launch EC2 instance
echo "🖥️  Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
        --image-id "$AMI_ID" \
        --count 1 \
        --instance-type t3.medium \
        --key-name $KEY_NAME \
        --security-group-ids "$SG_ID" \
        --user-data file://user-data-simple.sh \
        --region "$AWS_REGION" \
        --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=CompliantOne-Server}]' \
        --query 'Instances[0].InstanceId' --output text)

# Configure security group
aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 --region "$AWS_REGION" 2>/dev/null || true

aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0 --region "$AWS_REGION" 2>/dev/null || true

aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 --region "$AWS_REGION" 2>/dev/null || true

echo "⏳ Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region "$AWS_REGION"

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID --region "$AWS_REGION" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "✅ Deployment completed!"
echo "🌐 Your app will be available at: http://$PUBLIC_IP"
echo "🔑 SSH access: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
echo "⏳ Please wait 5-10 minutes for the application to start"

# Save deployment info
cat > deployment-info.txt << EOF
Compliant-One Quick Deployment
=============================
Instance ID: $INSTANCE_ID
Public IP: $PUBLIC_IP
SSH Command: ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP
Website: http://$PUBLIC_IP
Deployed: $(date)
EOF

echo "📄 Deployment info saved to deployment-info.txt"