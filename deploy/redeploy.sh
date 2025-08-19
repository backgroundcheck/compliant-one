#!/bin/bash
# Redeploy with correct AMI

set -e

echo "🚀 Redeploying with correct AMI..."

# Get latest AMI ID
AMI_ID=$(aws ec2 describe-images --owners amazon --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' --output text)
echo "✅ Using AMI: $AMI_ID"

# Launch new instance
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --count 1 \
    --instance-type t3.medium \
    --key-name compliant-one-key \
    --security-group-ids $(aws ec2 describe-security-groups --group-names compliant-one-sg --query 'SecurityGroups[0].GroupId' --output text) \
    --user-data file://user-data-simple.sh \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=CompliantOne-Server-New}]' \
    --query 'Instances[0].InstanceId' --output text)

echo "⏳ Waiting for instance..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get IP
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "✅ New deployment ready!"
echo "🌐 Website: http://$PUBLIC_IP"
echo "🔑 SSH: ssh -i compliant-one-key.pem ec2-user@$PUBLIC_IP"