# 🕷️ Scraping Control Panel - Quick Access Guide

## Overview

The Scraping Control Panel is a comprehensive web data collection and intelligence gathering system integrated into your Compliant.one platform. It provides automated scraping capabilities for compliance data sources, OSINT collection, and regulatory monitoring.

## Quick Access

- **Dashboard URL:** [http://localhost:8502](http://localhost:8502)
- **Login:** admin/admin123
- **Navigation:** Main Dashboard → 🕷️ Scraping Control Panel
- **Permission Required:** data_source_management

## Key Features

### 📊 Dashboard

- Real-time job monitoring
- Performance metrics and statistics
- System status and health monitoring
- Recent execution history

### ➕ Create Job

- Support for 8 data source types
- Configurable scraping parameters
- Advanced scheduling options
- Batch URL processing

### 📋 Manage Jobs

- Job lifecycle management
- Real-time progress tracking
- Error monitoring and debugging
- Execution history and analytics

### 📅 Scheduler

- Cron-based scheduling
- Interval scheduling (minutes/hours)
- Daily/weekly recurring jobs
- Automated execution management

### 📈 Reports

- Performance analytics
- Success rate tracking
- Data extraction metrics
- Export capabilities (JSON/CSV)

### ⚙️ Settings

- Global configuration
- Data retention policies
- HTTP request settings
- System maintenance tools

## Data Source Types

1. **Sanctions Lists** - OFAC, EU, UN sanctions data
2. **News Media** - Financial news and adverse media monitoring
3. **Corporate Records** - Company registration and filing data
4. **Government Data** - Regulatory and public sector information
5. **Court Records** - Legal proceedings and judgments
6. **PEP Lists** - Politically Exposed Persons databases
7. **Adverse Media** - Negative news and risk intelligence
8. **Custom** - Flexible scraping for any web source

## Sample Jobs Created

The admin setup has created 6 sample jobs:

1. **OFAC SDN List Monitor** - Daily sanctions list updates
2. **EU Consolidated List Monitor** - EU sanctions monitoring
3. **Reuters Financial News** - Financial news collection
4. **UK Companies House** - Corporate registry monitoring
5. **US Court Records** - Legal proceedings tracking
6. **World Bank PEP Database** - PEP list monitoring

## Job Configuration Options

### Basic Settings

- **Job Name:** Descriptive identifier
- **Job Type:** Data source category
- **Priority:** LOW/MEDIUM/HIGH/CRITICAL
- **Target URLs:** List of URLs to scrape

### Advanced Configuration

- **Delay:** Time between requests (anti-bot protection)
- **Timeout:** Request timeout duration
- **Retry Attempts:** Error recovery attempts
- **Content Limit:** Maximum content size to extract

### Scheduling Options

- **Interval:** Run every X minutes/hours
- **Daily:** Run at specific time each day
- **Weekly:** Run on specific day/time each week
- **Cron:** Custom cron expressions for complex scheduling

## Job Management

### Job Statuses

- **PENDING:** Job created, ready to execute
- **RUNNING:** Currently executing
- **COMPLETED:** Successfully finished
- **FAILED:** Execution failed
- **CANCELLED:** Manually stopped
- **PAUSED:** Temporarily suspended

### Job Actions

- **Execute:** Start job execution
- **Cancel:** Stop running job
- **Delete:** Remove job permanently
- **View Details:** See comprehensive job information
- **Schedule:** Set up automated execution

## Monitoring & Analytics

### Key Metrics

- **Total Jobs:** All jobs in the system
- **Running Jobs:** Currently executing jobs
- **Success Rate:** Percentage of successful executions
- **Data Points:** Total data items extracted

### Performance Tracking

- **Execution Timeline:** Jobs over time
- **URL Processing:** URLs scraped per execution
- **Data Extraction:** Data points collected
- **Error Analysis:** Failure patterns and causes

## Data Storage

### Output Structure

```plaintext
data/scraping_output/
├── {JOB_ID}/
│   └── {EXECUTION_ID}/
│       ├── data_1_abc123.json
│       ├── data_2_def456.json
│       └── ...
```

### Data Format

Each scraped URL produces a JSON file containing:

- Source URL
- HTTP status and headers
- Content timestamp
- Extracted content
- Metadata

## Security & Compliance

### Access Control

- Permission-based access (data_source_management)
- User authentication required
- Audit logging for all operations

### Data Protection

- Configurable data retention policies
- Automatic cleanup of old executions
- Secure storage of scraped content

### Rate Limiting

- Configurable delays between requests
- Timeout protection
- Retry mechanisms for failed requests

## Integration

### Platform Integration

- Seamless integration with Compliant.one dashboard
- Shared authentication and permissions
- Consistent UI/UX with other platform features

### API Access

- Job management via Python API
- Programmatic job creation and execution
- Scheduler automation

### Export Capabilities

- JSON statistics export
- CSV execution history
- Performance metrics download

## Troubleshooting

### Common Issues

1. **Job Fails to Start:** Check permissions and URL accessibility
2. **No Data Extracted:** Verify URL responses and content limits
3. **Scheduler Not Working:** Ensure scheduler service is running
4. **High Error Rates:** Check network connectivity and rate limits

### Log Locations

- **Job Logs:** data/scraping_logs/
- **System Logs:** Application logger output
- **Error Details:** Available in job execution details

## Next Steps

1. **Review Sample Jobs:** Examine pre-created jobs for configuration examples
2. **Create Custom Jobs:** Set up jobs for your specific data sources
3. **Configure Scheduling:** Automate regular data collection
4. **Monitor Performance:** Use analytics to optimize job settings
5. **Set Up Alerts:** Configure notifications for job failures

## Support

For technical support or feature requests:

- Check documentation in docs/scraping/
- Review job execution logs for errors
- Use the dashboard settings for system maintenance
- Monitor system status in the main dashboard

---

**Created:** July 24, 2025  
**Version:** 1.0  
**Last Updated:** Setup completion
