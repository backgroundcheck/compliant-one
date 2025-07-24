#!/usr/bin/env python3
"""
Scraping Control Panel Admin Setup
Administrative setup and configuration for the scraping system
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from services.scraping.job_manager import (
    ScrapingJobManager, ScrapingType, JobPriority
)
from services.scraping.scheduler import ScrapingScheduler
from utils.logger import get_logger

class ScrapingAdminSetup:
    """Administrative setup for scraping control panel"""
    
    def __init__(self):
        self.logger = get_logger("scraping_admin_setup")
        self.job_manager = ScrapingJobManager()
        self.scheduler = ScrapingScheduler(self.job_manager)
    
    def print_banner(self):
        """Print setup banner"""
        print("=" * 80)
        print("🕷️  SCRAPING CONTROL PANEL - ADMIN SETUP")
        print("=" * 80)
        print("Administrative setup and configuration for web scraping system")
        print("Compliance data collection, OSINT, and intelligence gathering")
        print("=" * 80)
        print()
    
    def create_sample_jobs(self):
        """Create sample scraping jobs for demonstration"""
        print("📝 Creating Sample Scraping Jobs...")
        print("-" * 50)
        
        sample_jobs = [
            {
                'name': 'OFAC SDN List Monitor',
                'type': ScrapingType.SANCTIONS_LISTS,
                'urls': [
                    'https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN_ENHANCED.CSV',
                    'https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV'
                ],
                'priority': JobPriority.HIGH,
                'config': {
                    'delay': 2.0,
                    'max_content_length': 50000,
                    'timeout': 60,
                    'retry_attempts': 3
                },
                'schedule': '0 6 * * *',  # Daily at 6 AM
                'metadata': {
                    'description': 'Monitor OFAC SDN list for updates',
                    'data_type': 'sanctions',
                    'update_frequency': 'daily'
                }
            },
            {
                'name': 'EU Consolidated List Monitor',
                'type': ScrapingType.SANCTIONS_LISTS,
                'urls': [
                    'https://webgate.ec.europa.eu/fsd/fsf/public/files/csvFullSanctionsList_1_1/content?token='
                ],
                'priority': JobPriority.HIGH,
                'config': {
                    'delay': 1.5,
                    'max_content_length': 100000,
                    'timeout': 45,
                    'retry_attempts': 3
                },
                'schedule': '0 7 * * *',  # Daily at 7 AM
                'metadata': {
                    'description': 'Monitor EU consolidated sanctions list',
                    'data_type': 'sanctions',
                    'region': 'EU'
                }
            },
            {
                'name': 'Reuters Financial News Monitor',
                'type': ScrapingType.NEWS_MEDIA,
                'urls': [
                    'https://www.reuters.com/finance/',
                    'https://www.reuters.com/business/finance/',
                    'https://www.reuters.com/markets/'
                ],
                'priority': JobPriority.MEDIUM,
                'config': {
                    'delay': 3.0,
                    'max_content_length': 20000,
                    'timeout': 30,
                    'retry_attempts': 2
                },
                'schedule': '0 */4 * * *',  # Every 4 hours
                'metadata': {
                    'description': 'Monitor Reuters for financial news and adverse media',
                    'data_type': 'news',
                    'source': 'reuters'
                }
            },
            {
                'name': 'UK Companies House Monitor',
                'type': ScrapingType.CORPORATE_RECORDS,
                'urls': [
                    'https://find-and-update.company-information.service.gov.uk/',
                    'https://download.companieshouse.gov.uk/en_output.html'
                ],
                'priority': JobPriority.MEDIUM,
                'config': {
                    'delay': 2.5,
                    'max_content_length': 30000,
                    'timeout': 45,
                    'retry_attempts': 3
                },
                'schedule': '0 2 * * 1',  # Weekly on Monday at 2 AM
                'metadata': {
                    'description': 'Monitor UK Companies House for corporate updates',
                    'data_type': 'corporate_records',
                    'jurisdiction': 'UK'
                }
            },
            {
                'name': 'US Court Records Monitor',
                'type': ScrapingType.COURT_RECORDS,
                'urls': [
                    'https://www.pacer.gov/',
                    'https://ecf.dcd.uscourts.gov/'
                ],
                'priority': JobPriority.LOW,
                'config': {
                    'delay': 5.0,
                    'max_content_length': 15000,
                    'timeout': 60,
                    'retry_attempts': 2
                },
                'schedule': '0 1 * * *',  # Daily at 1 AM
                'metadata': {
                    'description': 'Monitor US federal court records',
                    'data_type': 'court_records',
                    'jurisdiction': 'US'
                }
            },
            {
                'name': 'World Bank PEP Database',
                'type': ScrapingType.PEP_LISTS,
                'urls': [
                    'https://www.worldbank.org/en/projects-operations/procurement/debarred-firms',
                    'https://projects.worldbank.org/en/projects-operations/procurement/debarred-firms'
                ],
                'priority': JobPriority.HIGH,
                'config': {
                    'delay': 4.0,
                    'max_content_length': 25000,
                    'timeout': 60,
                    'retry_attempts': 3
                },
                'schedule': '0 3 * * 0',  # Weekly on Sunday at 3 AM
                'metadata': {
                    'description': 'Monitor World Bank PEP and debarred entities',
                    'data_type': 'pep_lists',
                    'organization': 'world_bank'
                }
            }
        ]
        
        created_jobs = []
        
        for job_data in sample_jobs:
            try:
                job_id = self.job_manager.create_job(
                    name=job_data['name'],
                    job_type=job_data['type'],
                    target_urls=job_data['urls'],
                    priority=job_data['priority'],
                    config=job_data['config'],
                    schedule=job_data.get('schedule'),
                    metadata=job_data['metadata']
                )
                
                created_jobs.append((job_id, job_data['name']))
                print(f"✅ Created: {job_data['name']} (ID: {job_id})")
                
            except Exception as e:
                print(f"❌ Failed to create {job_data['name']}: {e}")
        
        print(f"\n📊 Summary: Created {len(created_jobs)} sample jobs")
        return created_jobs
    
    def setup_default_configuration(self):
        """Setup default system configuration"""
        print("\n⚙️ Setting Up Default Configuration...")
        print("-" * 50)
        
        config = {
            'system': {
                'max_concurrent_jobs': 5,
                'default_delay': 2.0,
                'default_timeout': 30,
                'max_retries': 3,
                'job_retention_days': 90,
                'execution_retention_days': 30
            },
            'http': {
                'user_agent': 'Compliant-One Intelligence Scraper 1.0',
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            },
            'scheduling': {
                'enabled': True,
                'check_interval': 60,
                'timezone': 'UTC'
            },
            'security': {
                'respect_robots_txt': True,
                'rate_limiting': True,
                'ip_rotation': False,
                'proxy_enabled': False
            },
            'data': {
                'output_format': 'json',
                'compress_output': True,
                'encrypt_sensitive': True,
                'backup_enabled': True
            }
        }
        
        # Save configuration
        config_dir = Path("data/scraping_config")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = config_dir / "default_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Default configuration saved to: {config_file}")
        
        # Create directories
        directories = [
            "data/scraping_output",
            "data/scraping_logs",
            "data/scraping_backups",
            "data/scraping_temp"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        
        return config
    
    def initialize_database_schema(self):
        """Initialize database schema for scraping data"""
        print("\n🗄️ Initializing Database Schema...")
        print("-" * 50)
        
        # This would typically create database tables
        # For now, we'll create JSON schemas
        
        schemas = {
            'scraping_jobs': {
                'job_id': 'string',
                'name': 'string',
                'job_type': 'string',
                'target_urls': 'array',
                'status': 'string',
                'priority': 'integer',
                'created_at': 'datetime',
                'started_at': 'datetime',
                'completed_at': 'datetime',
                'progress': 'float',
                'config': 'object',
                'schedule': 'string',
                'metadata': 'object'
            },
            'job_executions': {
                'execution_id': 'string',
                'job_id': 'string',
                'started_at': 'datetime',
                'completed_at': 'datetime',
                'status': 'string',
                'urls_processed': 'integer',
                'data_extracted': 'integer',
                'errors': 'array',
                'output_files': 'array',
                'performance_metrics': 'object'
            },
            'scraped_data': {
                'data_id': 'string',
                'execution_id': 'string',
                'source_url': 'string',
                'data_type': 'string',
                'extracted_at': 'datetime',
                'content': 'object',
                'metadata': 'object'
            }
        }
        
        schema_dir = Path("data/schemas")
        schema_dir.mkdir(parents=True, exist_ok=True)
        
        for schema_name, schema_def in schemas.items():
            schema_file = schema_dir / f"{schema_name}_schema.json"
            with open(schema_file, 'w') as f:
                json.dump(schema_def, f, indent=2)
            print(f"✅ Created schema: {schema_name}")
        
        print("✅ Database schema initialization completed")
    
    def setup_monitoring_and_alerts(self):
        """Setup monitoring and alerting system"""
        print("\n📊 Setting Up Monitoring & Alerts...")
        print("-" * 50)
        
        monitoring_config = {
            'alerts': {
                'job_failure_threshold': 3,
                'execution_timeout_minutes': 60,
                'disk_space_threshold_gb': 1,
                'memory_usage_threshold_percent': 85
            },
            'notifications': {
                'email_enabled': True,
                'slack_enabled': False,
                'webhook_enabled': False,
                'log_level': 'INFO'
            },
            'metrics': {
                'collect_performance_metrics': True,
                'track_success_rates': True,
                'monitor_resource_usage': True,
                'generate_reports': True
            },
            'retention': {
                'metrics_retention_days': 30,
                'alert_history_days': 90,
                'log_retention_days': 30
            }
        }
        
        monitoring_dir = Path("data/monitoring")
        monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        monitoring_file = monitoring_dir / "monitoring_config.json"
        with open(monitoring_file, 'w') as f:
            json.dump(monitoring_config, f, indent=2)
        
        print(f"✅ Monitoring configuration saved: {monitoring_file}")
        
        # Create alert templates
        alert_templates = {
            'job_failure': {
                'title': 'Scraping Job Failed',
                'message': 'Job {job_name} (ID: {job_id}) has failed. Error: {error_message}',
                'severity': 'high',
                'actions': ['retry_job', 'notify_admin']
            },
            'scheduler_error': {
                'title': 'Scheduler Error',
                'message': 'Scheduler encountered an error: {error_message}',
                'severity': 'medium',
                'actions': ['restart_scheduler', 'notify_admin']
            },
            'resource_warning': {
                'title': 'Resource Usage Warning',
                'message': 'System resource usage is high: {resource_type} at {usage_percent}%',
                'severity': 'medium',
                'actions': ['monitor_closely']
            }
        }
        
        alerts_file = monitoring_dir / "alert_templates.json"
        with open(alerts_file, 'w') as f:
            json.dump(alert_templates, f, indent=2)
        
        print(f"✅ Alert templates created: {alerts_file}")
    
    def create_user_documentation(self):
        """Create user documentation and guides"""
        print("\n📚 Creating User Documentation...")
        print("-" * 50)
        
        docs_dir = Path("docs/scraping")
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Admin guide
        admin_guide = """# Scraping Control Panel - Admin Guide

## Overview
The Scraping Control Panel provides comprehensive web data collection capabilities for compliance, OSINT, and intelligence gathering.

## Getting Started

### 1. Access the Control Panel
- Navigate to 🕷️ Scraping Control Panel in the main dashboard
- Ensure you have 'data_source_management' permission

### 2. Creating Jobs
- Use the "Create Job" tab to set up new scraping jobs
- Configure target URLs, scheduling, and advanced options
- Test with preview mode before full execution

### 3. Managing Jobs
- Monitor job status and progress in real-time
- Execute, pause, or cancel jobs as needed
- Review execution history and performance metrics

### 4. Scheduling
- Set up automated job execution with cron expressions
- Monitor scheduled jobs and manage their timing
- Review execution patterns and optimize schedules

## Job Types

### Sanctions Lists
- Monitor OFAC, EU, UN sanctions lists
- Automatic format detection and parsing
- Real-time updates and change detection

### News Media
- Adverse media monitoring
- Financial news collection
- Sentiment analysis integration

### Corporate Records
- Company registration data
- Beneficial ownership information
- Corporate structure monitoring

### Government Data
- Regulatory announcements
- Policy changes
- Official statements

### Court Records
- Legal proceedings
- Judgments and orders
- Compliance violations

### PEP Lists
- Politically Exposed Person databases
- Government official listings
- International organization data

## Best Practices

### 1. Rate Limiting
- Respect target site rate limits
- Use appropriate delays between requests
- Monitor for blocking or throttling

### 2. Data Quality
- Validate scraped data regularly
- Implement data quality checks
- Handle format changes gracefully

### 3. Compliance
- Respect robots.txt files
- Follow website terms of service
- Implement proper attribution

### 4. Security
- Use secure connections (HTTPS)
- Rotate user agents appropriately
- Monitor for detection patterns

## Troubleshooting

### Common Issues
1. **Job Failures**: Check target URL accessibility
2. **Slow Performance**: Adjust delay and timeout settings
3. **Data Quality**: Review parsing logic and validation
4. **Schedule Issues**: Verify cron expressions

### Error Codes
- `TIMEOUT_ERROR`: Request timeout exceeded
- `CONNECTION_ERROR`: Network connectivity issue
- `PARSE_ERROR`: Data parsing failure
- `RATE_LIMITED`: Request rate exceeded

## Monitoring & Alerts

### Key Metrics
- Job success rates
- Data extraction volumes
- Performance metrics
- Error rates

### Alert Configuration
- Set up failure notifications
- Monitor resource usage
- Track data quality metrics

## Security Considerations

### Data Protection
- Encrypt sensitive scraped data
- Implement access controls
- Regular security audits

### Ethical Scraping
- Respect website policies
- Avoid overloading servers
- Obtain necessary permissions

## Support
For technical support or feature requests, contact the platform administrators.
"""
        
        with open(docs_dir / "admin_guide.md", 'w') as f:
            f.write(admin_guide)
        
        # Quick start guide
        quick_start = """# Quick Start Guide - Scraping Control Panel

## 5-Minute Setup

### Step 1: Access Panel
1. Log in to Compliant.one dashboard
2. Navigate to 🕷️ Scraping Control Panel
3. Review the dashboard overview

### Step 2: Create Your First Job
1. Click "Create Job" tab
2. Enter job name: "Test OFAC Monitor"
3. Select job type: "sanctions_lists"
4. Add URL: `https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV`
5. Click "Create Job"

### Step 3: Execute Job
1. Go to "Manage Jobs" tab
2. Select your job
3. Click "Execute"
4. Monitor progress in real-time

### Step 4: Review Results
1. Check execution status
2. Review extracted data
3. Examine performance metrics

### Step 5: Schedule Automation
1. Go to "Scheduler" tab
2. Select your job
3. Set daily schedule: "0 6 * * *"
4. Enable automated execution

## Next Steps
- Explore advanced configuration options
- Set up monitoring and alerts
- Create additional job types
- Review best practices guide
"""
        
        with open(docs_dir / "quick_start.md", 'w') as f:
            f.write(quick_start)
        
        print(f"✅ Documentation created in: {docs_dir}")
    
    async def run_system_tests(self):
        """Run system tests to verify setup"""
        print("\n🧪 Running System Tests...")
        print("-" * 50)
        
        tests_passed = 0
        tests_total = 5
        
        # Test 1: Job Manager
        try:
            test_job_id = self.job_manager.create_job(
                name="Test Job",
                job_type=ScrapingType.CUSTOM,
                target_urls=["https://httpbin.org/get"],
                priority=JobPriority.LOW,
                config={'delay': 1.0}
            )
            
            job = self.job_manager.get_job(test_job_id)
            assert job is not None
            
            # Cleanup
            self.job_manager.delete_job(test_job_id)
            
            print("✅ Test 1: Job Manager - PASSED")
            tests_passed += 1
            
        except Exception as e:
            print(f"❌ Test 1: Job Manager - FAILED: {e}")
        
        # Test 2: Scheduler
        try:
            self.scheduler.start()
            assert self.scheduler.running
            self.scheduler.stop()
            
            print("✅ Test 2: Scheduler - PASSED")
            tests_passed += 1
            
        except Exception as e:
            print(f"❌ Test 2: Scheduler - FAILED: {e}")
        
        # Test 3: Configuration Loading
        try:
            config_file = Path("data/scraping_config/default_config.json")
            assert config_file.exists()
            
            with open(config_file) as f:
                config = json.load(f)
                assert 'system' in config
            
            print("✅ Test 3: Configuration - PASSED")
            tests_passed += 1
            
        except Exception as e:
            print(f"❌ Test 3: Configuration - FAILED: {e}")
        
        # Test 4: Directory Structure
        try:
            required_dirs = [
                "data/scraping_output",
                "data/scraping_logs",
                "data/schemas"
            ]
            
            for directory in required_dirs:
                assert Path(directory).exists()
            
            print("✅ Test 4: Directory Structure - PASSED")
            tests_passed += 1
            
        except Exception as e:
            print(f"❌ Test 4: Directory Structure - FAILED: {e}")
        
        # Test 5: Documentation
        try:
            docs_dir = Path("docs/scraping")
            assert docs_dir.exists()
            assert (docs_dir / "admin_guide.md").exists()
            assert (docs_dir / "quick_start.md").exists()
            
            print("✅ Test 5: Documentation - PASSED")
            tests_passed += 1
            
        except Exception as e:
            print(f"❌ Test 5: Documentation - FAILED: {e}")
        
        print(f"\n📊 Test Results: {tests_passed}/{tests_total} tests passed")
        
        if tests_passed == tests_total:
            print("🎉 All tests passed! System is ready for use.")
        else:
            print("⚠️  Some tests failed. Please review the setup.")
        
        return tests_passed == tests_total
    
    async def run_full_setup(self):
        """Run the complete setup process"""
        self.print_banner()
        
        print("🚀 Starting Scraping Control Panel Setup...")
        print("This will configure the complete scraping system for your platform.\n")
        
        # Step 1: Default Configuration
        config = self.setup_default_configuration()
        
        # Step 2: Database Schema
        self.initialize_database_schema()
        
        # Step 3: Sample Jobs
        sample_jobs = self.create_sample_jobs()
        
        # Step 4: Monitoring
        self.setup_monitoring_and_alerts()
        
        # Step 5: Documentation
        self.create_user_documentation()
        
        # Step 6: System Tests
        tests_passed = await self.run_system_tests()
        
        # Setup Summary
        print("\n" + "="*80)
        print("🎯 SETUP SUMMARY")
        print("="*80)
        print(f"✅ Configuration files created")
        print(f"✅ Database schema initialized")
        print(f"✅ {len(sample_jobs)} sample jobs created")
        print(f"✅ Monitoring and alerts configured")
        print(f"✅ Documentation generated")
        print(f"✅ System tests: {'PASSED' if tests_passed else 'SOME FAILED'}")
        
        print("\n🚀 Next Steps:")
        print("1. Access the Scraping Control Panel via the main dashboard")
        print("2. Review and customize the sample jobs")
        print("3. Set up scheduling for automated execution")
        print("4. Configure monitoring and alerts")
        print("5. Read the documentation in docs/scraping/")
        
        print("\n📍 Quick Access:")
        print("   Dashboard: 🕷️ Scraping Control Panel")
        print("   Permission Required: data_source_management")
        print("   Documentation: docs/scraping/admin_guide.md")
        
        print("\n🎉 Scraping Control Panel setup completed successfully!")
        print("="*80)

async def main():
    """Main setup function"""
    print("🚀 Initializing Scraping Control Panel Admin Setup...")
    
    setup = ScrapingAdminSetup()
    
    try:
        await setup.run_full_setup()
        
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
