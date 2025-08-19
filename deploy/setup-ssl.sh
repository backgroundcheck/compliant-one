#!/bin/bash
# SSL Setup with Let's Encrypt

DOMAIN="$1"
EC2_IP="13.229.202.102"

if [ -z "$DOMAIN" ]; then
    echo "Usage: ./setup-ssl.sh yourdomain.com"
    exit 1
fi

echo "🔒 Setting up SSL for: $DOMAIN"

# SSH to EC2 and setup SSL
ssh -i compliant-one-key.pem ec2-user@$EC2_IP << EOF
sudo yum install -y certbot python3-certbot-nginx
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
sudo systemctl enable certbot-renew.timer
EOF

echo "✅ SSL certificate installed!"
echo "🌐 Your site is now available at: https://$DOMAIN"