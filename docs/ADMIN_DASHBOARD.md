# 🔧 Compliant.one Admin Dashboard

## Overview

The Admin Dashboard provides comprehensive data source management capabilities for the Compliant.one RegTech platform. It allows administrators to configure, validate, and manage various compliance data sources, upload and process files, and monitor system health.

## Features

### 📊 Data Source Management

- **Add/Remove Sources**: Configure new compliance data sources
- **Source Categories**: Identity, Sanctions, PEP, Adverse Media, Beneficial Ownership, Court Records, Regulatory
- **Source Types**: API integration, File upload, Web scraping, Database connections
- **Real-time Status**: Monitor source connectivity and data quality

### 📁 File Upload & Processing

- **Multi-format Support**: CSV, XML, PDF, DOCX, XLS, XLSX, HTML, JSON, TXT files
- **Bulk Processing**: Upload and process multiple files simultaneously  
- **Smart Extraction**: Automatic entity recognition and classification
- **Progress Tracking**: Real-time upload and processing status
- **Error Handling**: Detailed error reporting and recovery options

### 🔍 Data Processing Engine

- **Entity Recognition**: Automatic identification of:
  - Names and individuals
  - Organizations and companies
  - Locations and addresses
  - Identifiers and reference numbers
  - Email addresses and phone numbers
  - Dates and timestamps
- **Risk Scoring**: AI-powered risk assessment using keyword analysis
- **Data Normalization**: Standardize data formats across sources
- **Metadata Enrichment**: Add contextual information to extracted data

### ✅ Source Validation

- **API Testing**: Validate API endpoints and authentication
- **Data Quality Checks**: Verify data integrity and completeness
- **Connectivity Monitoring**: Real-time source availability status
- **Error Reporting**: Detailed logs for troubleshooting

### 📈 System Monitoring

- **Database Statistics**: Track total sources, files, and records
- **Processing Metrics**: Monitor file processing success rates
- **Storage Management**: View disk usage and cleanup options
- **Health Indicators**: System component status overview

## Quick Start

### 1. Setup

```bash
# Initialize the admin database
python3 database/init_admin_db.py

# Run the test script to create sample data
chmod +x test_admin.sh
./test_admin.sh
```

### 2. Launch Dashboard

```bash
# Install dependencies
pip install -r requirements.txt

# Start the dashboard
streamlit run dashboard/main.py
```

### 3. Access Admin Dashboard

1. Open your browser to the Streamlit URL (typically `http://localhost:8501`)
2. Navigate to "🔧 Admin Dashboard" in the sidebar
3. Start managing your data sources!

## File Processing

### Supported File Types

| Format | Extension | Description | Processing Method |
|--------|-----------|-------------|-------------------|
| CSV | `.csv` | Comma-separated values | Pandas DataFrame processing |
| Excel | `.xlsx`, `.xls` | Microsoft Excel files | Openpyxl/Pandas processing |
| XML | `.xml` | Extensible Markup Language | ElementTree parsing |
| JSON | `.json` | JavaScript Object Notation | Native JSON parsing |
| Word | `.docx` | Microsoft Word documents | python-docx library |
| PDF | `.pdf` | Portable Document Format | PyPDF2 text extraction |
| HTML | `.html`, `.htm` | Web pages | BeautifulSoup parsing |
| Text | `.txt` | Plain text files | Pattern-based extraction |

### Processing Workflow

1. **File Upload**: Drag and drop or select files
2. **Format Detection**: Automatic file type identification
3. **Data Extraction**: Content parsing and entity extraction
4. **Entity Classification**: Automatic categorization and risk scoring
5. **Database Storage**: Structured data storage for screening
6. **Validation**: Data quality checks and error reporting

## Data Source Configuration

### Adding API Sources

1. Go to **Data Sources** → **Add New Data Source**
2. Fill in the details:
   - **Source Name**: Unique identifier
   - **Source Type**: Select "API"
   - **Category**: Choose appropriate category
   - **API Endpoint**: Full URL to the API
   - **API Key**: Authentication credentials
   - **Description**: Brief description

3. Click **Add Data Source**
4. Use **Source Validation** to test connectivity

### Sample API Sources

The system comes pre-configured with sample entries for:

- OFAC SDN List (US Treasury sanctions)
- UN Consolidated List (UN Security Council sanctions)
- World-Check Database (Refinitiv PEP/sanctions)
- Companies House UK (Corporate registry)
- Google News API (Adverse media monitoring)

### File Upload Sources

1. Create a new source with type "File Upload"
2. Upload files through the **File Upload** section
3. Files are automatically processed and entities extracted
4. Processed data becomes available for screening

## Database Schema

### Core Tables

#### `data_sources`

- Source configuration and metadata
- API credentials and endpoints
- Status and last update timestamps

#### `uploaded_files`

- File upload tracking
- Processing status and metrics
- Error logging

#### `processed_data`

- Extracted entities and metadata
- Risk scores and classifications
- Source attribution

## Configuration

### Admin Configuration

Edit `config/admin_config.py` to customize:

- **File Processing**: Upload limits, allowed types
- **Risk Scoring**: Keywords and thresholds  
- **Entity Patterns**: Recognition patterns
- **Feature Flags**: Enable/disable features
- **Security Settings**: Authentication and permissions

### Environment Variables

```bash
# Optional: Custom database location
ADMIN_DB_PATH=/path/to/admin.db

# Optional: Upload directory
UPLOAD_DIR=/path/to/uploads

# Optional: Processing limits
MAX_FILE_SIZE_MB=100
```

## Security Considerations

### Production Deployment

1. **Authentication**: Enable user authentication
2. **HTTPS**: Use SSL/TLS encryption
3. **File Validation**: Scan uploaded files
4. **Access Control**: Limit admin access
5. **Audit Logging**: Track all admin actions

### Data Protection

- Sensitive data encryption at rest
- Secure API key storage
- Regular security updates
- Backup and recovery procedures

## Troubleshooting

### Common Issues

#### Database Connection Error

```bash
# Reinitialize database
python3 database/init_admin_db.py
```

#### File Processing Errors

- Check file format and encoding
- Verify file size limits
- Review error logs in the dashboard

#### API Source Validation Failures

- Verify API endpoint URLs
- Check authentication credentials
- Test network connectivity

### Log Files

- **Application Logs**: `logs/admin_dashboard.log`
- **Processing Logs**: Dashboard UI error messages
- **Database Logs**: SQLite error messages

## API Integration Examples

### OFAC SDN API

```python
import requests

url = "https://api.treasury.gov/ofac/sdn"
headers = {"Authorization": "Bearer YOUR_API_KEY"}
response = requests.get(url, headers=headers)
```

### World-Check API

```python
import requests

url = "https://api.worldcheck.com/v1/search"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
data = {"name": "John Doe", "type": "Individual"}
response = requests.post(url, headers=headers, json=data)
```

## Development

### Adding New File Processors

1. Create processor in `utils/data_processor.py`
2. Register in `supported_formats` dictionary
3. Add file type to configuration
4. Update documentation

### Custom Entity Classifiers

1. Extend `EntityClassifier` class
2. Add custom patterns and rules
3. Update risk scoring algorithms
4. Test with sample data

## Support

For technical support and feature requests:

- **Documentation**: See main DEPLOYMENT.md
- **Issues**: Report via platform support channels
- **Development**: Contribute to the platform codebase

---

**Compliant.one Admin Dashboard** - Streamlining compliance data management for enterprise RegTech solutions.
