#!/usr/bin/env python3
"""
Scraping Control Panel Demo
Demonstrates the complete web scraping functionality
"""

import asyncio
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from services.scraping.job_manager import (
    ScrapingJobManager, ScrapingType, JobPriority, JobStatus
)
from services.scraping.scheduler import ScrapingScheduler

async def demo_scraping_control_panel():
    """Demo the scraping control panel functionality"""
    print("\n" + "="*80)
    print("🕷️ SCRAPING CONTROL PANEL DEMO")
    print("="*80)
    print("Demonstrating web data collection and intelligence gathering")
    print("="*80)
    
    # Initialize managers
    print("\n🚀 Initializing Scraping System...")
    job_manager = ScrapingJobManager()
    scheduler = ScrapingScheduler(job_manager)
    
    # Show initial statistics
    stats = job_manager.get_job_statistics()
    print(f"   📊 Current Jobs: {stats['total_jobs']}")
    print(f"   🏃 Running Jobs: {stats['running_jobs']}")
    print(f"   📈 Total Executions: {stats['total_executions']}")
    
    # Create a sample job
    print(f"\n➕ Creating Sample Scraping Job...")
    
    sample_urls = [
        "https://httpbin.org/json",
        "https://httpbin.org/headers",
        "https://httpbin.org/user-agent"
    ]
    
    job_id = job_manager.create_job(
        name="Demo Data Collection",
        job_type=ScrapingType.CUSTOM,
        target_urls=sample_urls,
        priority=JobPriority.HIGH,
        config={
            'delay': 2.0,
            'max_content_length': 5000,
            'timeout': 15
        },
        metadata={
            'purpose': 'demonstration',
            'created_by': 'demo_script'
        }
    )
    
    print(f"   ✅ Created job: {job_id}")
    
    # Execute the job
    print(f"\n▶️ Executing Scraping Job...")
    async with job_manager:
        try:
            execution_id = await job_manager.execute_job(job_id)
            print(f"   🏃 Started execution: {execution_id}")
            
            # Wait for completion (with timeout)
            import time
            start_time = time.time()
            while time.time() - start_time < 30:  # 30 second timeout
                job = job_manager.get_job(job_id)
                if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                    break
                await asyncio.sleep(1)
            
            # Show results
            job = job_manager.get_job(job_id)
            print(f"   📊 Job Status: {job.status.value}")
            print(f"   📈 Progress: {job.progress:.1f}%")
            print(f"   ✅ Successful: {job.successful_extractions}")
            print(f"   ❌ Failed: {job.failed_extractions}")
            print(f"   📦 Data Extracted: {job.data_extracted}")
            
            if job.output_path:
                print(f"   📁 Output: {job.output_path}")
        
        except Exception as e:
            print(f"   ❌ Execution error: {e}")
    
    # Show scheduler capabilities
    print(f"\n📅 Scheduler Demonstration...")
    
    # Start scheduler
    scheduler.start()
    print(f"   ✅ Scheduler started")
    
    # Schedule the job
    scheduler.schedule_job(job_id, "interval", interval=5)  # Every 5 minutes
    print(f"   ⏰ Job scheduled for every 5 minutes")
    
    # Show scheduled jobs
    scheduled = scheduler.get_scheduled_jobs()
    print(f"   📋 Scheduled jobs: {len(scheduled)}")
    
    # Stop scheduler
    scheduler.stop()
    print(f"   ⏹️ Scheduler stopped")
    
    # Show execution history
    print(f"\n📈 Execution History...")
    executions = job_manager.get_execution_history(job_id)
    
    for i, execution in enumerate(executions[:3], 1):  # Show first 3
        print(f"   {i}. {execution.execution_id[:12]}... - {execution.status.value}")
        print(f"      Started: {execution.started_at[:19] if execution.started_at else 'N/A'}")
        print(f"      URLs: {execution.urls_processed}, Data: {execution.data_extracted}")
    
    # Show system capabilities
    print(f"\n🎯 System Capabilities:")
    print(f"   🕷️ Multi-source web scraping")
    print(f"   📅 Advanced job scheduling (cron, interval, daily, weekly)")
    print(f"   📊 Real-time progress monitoring")
    print(f"   📈 Performance analytics and reporting")
    print(f"   🚨 Error handling and retry mechanisms")
    print(f"   📦 Structured data extraction and storage")
    print(f"   ⚙️ Configurable delays and request settings")
    print(f"   🔄 Background execution and queue management")
    
    # Show data types supported
    print(f"\n📋 Supported Data Sources:")
    for scraping_type in ScrapingType:
        print(f"   • {scraping_type.value.replace('_', ' ').title()}")
    
    # Platform integration
    print(f"\n🔗 Platform Integration:")
    print(f"   ✅ Integrated with Compliant.one dashboard")
    print(f"   ✅ Permission-based access control")
    print(f"   ✅ Real-time monitoring and alerts")
    print(f"   ✅ Export capabilities (JSON, CSV)")
    print(f"   ✅ Admin setup and configuration")
    print(f"   ✅ Sample jobs and documentation included")
    
    print(f"\n🎉 Demo completed! Access the full interface via:")
    print(f"   Dashboard → 🕷️ Scraping Control Panel")
    print(f"   Login: admin/admin123")
    print(f"   URL: http://localhost:8502")
    
    print(f"\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(demo_scraping_control_panel())
