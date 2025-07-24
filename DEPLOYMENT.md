# Compliant.one Platform - Enterprise RegTech Solution

## 🎯 Quick Start Guide

### Prerequisites
- Python 3.8+ installed
- MongoDB 4.4+ (Community or Atlas)
- Git (for cloning)
- 4GB+ RAM recommended

### One-Command Setup
```bash
chmod +x setup_complete.sh
./setup_complete.sh
```

This will automatically:
- Set up Python virtual environment
- Install all dependencies
- Initialize MongoDB
- Create admin user
- Start the platform

### Manual Setup

#### 1. Environment Setup
```bash
# Clone and setup
git clone <repository-url>
cd compliant-one

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 2. MongoDB Configuration

**Option A: Local MongoDB**
```bash
# Install MongoDB (Ubuntu/Debian)
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

**Option B: MongoDB Atlas (Cloud)**
1. Create account at https://cloud.mongodb.com
2. Create new cluster
3. Get connection string
4. Update `config/settings.py` with your connection string

#### 3. Database Initialization
```bash
# Run setup script
python -c "
from core.auth import MongoDBConnection
conn = MongoDBConnection()
print('MongoDB connected successfully!')
"

# Create admin user
python -c "
from core.auth import UserManager
um = UserManager()
um.create_user('admin', 'admin@company.com', 'SecurePass123!', 'admin')
print('Admin user created!')
"
```

#### 4. Start Platform
```bash
# Launch dashboard
streamlit run dashboard/main.py --server.port 8501 --server.address 0.0.0.0
```

Access at: http://localhost:8501

## 📁 Folder Organization (Recently Merged)

The platform now consolidates two previous Compliant.one projects:

### 📊 Current Structure
```
compliant-one/                    # Main unified platform
├── core/                        # Authentication & platform logic
├── dashboard/                   # Streamlit web interface
├── services/                    # Compliance services
│   ├── document_processing/     # PDF processing scripts (migrated)
│   ├── compliance/             # Anti-bribery modules (migrated)
│   ├── web_crawler/           # Web crawling with crawl4ai
│   └── [other services]/
├── data/
│   ├── pdfs/                   # 6,014 migrated PDF files
│   │   └── downloaded_pdfs/    # Regulatory documents
│   └── legacy_data/           # Migrated databases
├── integrations/              # OSINT tools (migrated)
│   └── ethics-eye-osint-guard/
├── legacy/                    # Legacy app preserved
│   ├── legacy_app.py         # Original Streamlit app
│   └── legacy_README.md      # Original documentation
└── [other directories]/
```

### 🔄 Merge Summary
- ✅ **6,014 PDF files** moved from `/root/compliant.one`
- ✅ **Document processing scripts** integrated
- ✅ **Anti-bribery compliance modules** preserved
- ✅ **OSINT tools** moved to integrations
- ✅ **Legacy app** backed up for reference
- ✅ **Original folder** backed up to `/root/compliant.one.backup`

## 🔐 Authentication System

### User Roles & Permissions

| Role | Permissions |
|------|-------------|
| **admin** | Full system access, user management, all data sources |
| **analyst** | Read/write data sources, generate reports |
| **viewer** | Read-only access to reports and data |

### Default Credentials
- **Username**: admin
- **Password**: SecurePass123!
- **Email**: admin@company.com

⚠️ **IMPORTANT**: Change default password immediately after first login!

### User Management
Access User Management from the admin dashboard to:
- Create new users
- Assign roles
- Reset passwords
- Deactivate accounts

## 📊 Data Source Management

### Supported File Formats
- **CSV**: Customer data, transaction logs
- **XML**: Regulatory submissions, API responses
- **JSON**: API data, configuration files
- **PDF**: Reports, documentation (6,014+ files available)
- **DOCX**: Policies, procedures
- **XLSX/XLS**: Spreadsheets, financial data
- **HTML**: Web scraped data
- **TXT**: Logs, plain text data

### Adding Data Sources

1. **Login** to admin dashboard
2. **Navigate** to "Data Source Management"
3. **Click** "Add New Source"
4. **Configure**:
   - Source name and description
   - Upload file or enter API endpoint
   - Set validation rules
   - Define update frequency

### 🕷️ Web Crawler Integration

The platform now includes advanced web crawling capabilities using **crawl4ai**:

#### Features:
- **Multiple extraction strategies**: default, financial, regulatory, sanctions, news
- **Bulk URL processing**: Crawl multiple URLs concurrently
- **Entity extraction**: Automatic identification of persons, organizations, locations
- **Risk scoring**: AI-powered risk assessment
- **OSINT collection**: Open source intelligence gathering

#### Usage:
1. Navigate to "Web Crawler" in admin dashboard
2. Initialize crawler
3. Enter target URLs
4. Select extraction strategy
5. View extracted entities and risk scores

### API Integration
```python
# Example: Connect external API
{
    "name": "OFAC Sanctions API",
    "type": "api",
    "endpoint": "https://api.sanctions.gov/v1/search",
    "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
    },
    "update_frequency": "daily"
}
```

## 🏗️ Architecture Overview

### Core Components

```
compliant-one/
├── core/                   # Core platform logic
│   ├── auth.py            # MongoDB authentication system
│   ├── platform.py       # Main platform engine
│   └── mock_services.py   # Development services
├── dashboard/             # Streamlit web interface
│   ├── main.py           # Main dashboard
│   ├── admin.py          # Admin interface
│   └── auth_interface.py # Authentication UI
├── services/             # Compliance services
│   ├── kyc/             # Know Your Customer
│   ├── sanctions/       # Sanctions screening
│   ├── beneficial_ownership/ # BO verification
│   ├── osint/          # Open source intelligence
│   ├── monitoring/     # Transaction monitoring
│   ├── web_crawler/    # Web crawling service
│   ├── document_processing/ # PDF processing (migrated)
│   └── compliance/     # Anti-bribery modules (migrated)
└── utils/               # Utilities
    ├── data_processor.py # File processing engine
    └── logger.py        # Logging system
```

### Database Schema

**MongoDB Collections:**
- `users`: User accounts and authentication
- `sessions`: Active user sessions
- `audit_logs`: System audit trail

**SQLite Tables:**
- `data_sources`: Configured data sources
- `validation_rules`: Data validation logic
- `processing_logs`: File processing history

**Legacy Data:**
- `documents.db`: 6,014+ PDF documents (migrated)
- Document metadata and indexes

## 🚀 Production Deployment

### Docker Deployment
```bash
# Build container
docker build -t compliant-one .

# Run with MongoDB
docker-compose up -d
```

### Environment Variables
```bash
# Required for production
export MONGODB_URI="mongodb://localhost:27017/compliant_one"
export JWT_SECRET_KEY="your-super-secret-jwt-key-here"
export STREAMLIT_SERVER_PORT="8501"
export LOG_LEVEL="INFO"
```

### Security Checklist
- [ ] Change default admin password
- [ ] Configure secure JWT secret key
- [ ] Enable MongoDB authentication
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Regular security updates

### Performance Tuning
```python
# MongoDB optimization
{
    "maxPoolSize": 50,
    "minPoolSize": 5,
    "maxIdleTimeMS": 30000,
    "serverSelectionTimeoutMS": 5000
}
```

## 📈 Monitoring & Maintenance

### Health Checks
```bash
# Platform health
curl http://localhost:8501/health

# MongoDB health
mongo --eval "db.adminCommand('ping')"
```

### Log Locations
- **Application**: `logs/platform.log`
- **MongoDB**: `/var/log/mongodb/mongod.log`
- **System**: `logs/system.log`

### Backup Strategy
```bash
# MongoDB backup
mongodump --db compliant_one --out ./backups/$(date +%Y%m%d)

# File backup (including 6,014 PDFs)
tar -czf backups/files_$(date +%Y%m%d).tar.gz data/ logs/
```

## 🛠️ Troubleshooting

### Common Issues

**MongoDB Connection Failed**
```bash
# Check MongoDB status
sudo systemctl status mongod

# Check connection string
python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
print('Connected:', client.admin.command('ismaster'))
"
```

**Authentication Errors**
```bash
# Reset admin password
python -c "
from core.auth import UserManager
um = UserManager()
um.reset_password('admin', 'NewSecurePass123!')
print('Password reset successfully!')
"
```

**File Processing Errors**
- Check file format compatibility
- Verify file size limits
- Review processing logs in dashboard

### Support
- **Documentation**: `/docs/`
- **Logs**: `/logs/`
- **Merge Summary**: `MERGE_SUMMARY.md`
- **Issues**: Check platform logs for detailed error messages

## 📚 API Reference

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/profile` - User profile
- `PUT /auth/password` - Change password

### Data Management
- `GET /api/sources` - List data sources
- `POST /api/sources` - Add new source
- `PUT /api/sources/{id}` - Update source
- `DELETE /api/sources/{id}` - Remove source

### Web Crawler
- `POST /api/crawler/crawl` - Crawl single URL
- `POST /api/crawler/bulk` - Crawl multiple URLs
- `GET /api/crawler/results` - Get crawling results

### Document Processing
- `POST /api/documents/upload` - Upload documents
- `GET /api/documents/search` - Search PDF documents
- `GET /api/documents/extract` - Extract document entities

### Compliance Services
- `POST /api/kyc/verify` - KYC verification
- `POST /api/sanctions/screen` - Sanctions screening
- `POST /api/osint/search` - OSINT lookup
- `GET /api/reports/generate` - Generate compliance report

---

**Built with ❤️ for RegTech compliance**
