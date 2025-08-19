#!/bin/bash
# Domain Setup Script for Compliant-One

DOMAIN_NAME="$1"
EC2_IP="13.229.202.102"

if [ -z "$DOMAIN_NAME" ]; then
    echo "Usage: ./setup-domain.sh yourdomain.com"
    exit 1
fi

echo "🌐 Setting up domain: $DOMAIN_NAME"

# Create hosted zone
HOSTED_ZONE_ID=$(aws route53 create-hosted-zone \
    --name $DOMAIN_NAME \
    --caller-reference $(date +%s) \
    --query 'HostedZone.Id' --output text)

echo "✅ Created hosted zone: $HOSTED_ZONE_ID"

# Create A record
aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "'$DOMAIN_NAME'",
                "Type": "A",
                "TTL": 300,
                "ResourceRecords": [{"Value": "'$EC2_IP'"}]
            }
        }]
    }'

# Create www record
aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "www.'$DOMAIN_NAME'",
                "Type": "A",
                "TTL": 300,
                "ResourceRecords": [{"Value": "'$EC2_IP'"}]
            }
        }]
    }'

# Get nameservers
NAMESERVERS=$(aws route53 get-hosted-zone \
    --id $HOSTED_ZONE_ID \
    --query 'DelegationSet.NameServers' --output text)

echo "✅ Domain setup complete!"
echo "📋 Update your domain registrar with these nameservers:"
echo "$NAMESERVERS"
echo ""
echo "🌐 Your site will be available at:"
echo "   http://$DOMAIN_NAME"
echo "   http://www.$DOMAIN_NAME"