#!/usr/bin/env python3
"""
Scraping Job Manager
Manages and executes web scraping jobs for compliance data collection
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
import aiofiles
from urllib.parse import urljoin, urlparse
import hashlib
import os

from utils.logger import get_logger

class JobStatus(Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class JobPriority(Enum):
    """Job priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ScrapingType(Enum):
    """Types of scraping jobs"""
    SANCTIONS_LISTS = "sanctions_lists"
    NEWS_MEDIA = "news_media"
    CORPORATE_RECORDS = "corporate_records"
    GOVERNMENT_DATA = "government_data"
    COURT_RECORDS = "court_records"
    PEP_LISTS = "pep_lists"
    ADVERSE_MEDIA = "adverse_media"
    CUSTOM = "custom"

@dataclass
class ScrapingJob:
    """Scraping job data structure"""
    job_id: str
    name: str
    job_type: ScrapingType
    target_urls: List[str]
    status: JobStatus
    priority: JobPriority
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: float = 0.0
    total_urls: int = 0
    processed_urls: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0
    data_extracted: int = 0
    config: Dict[str, Any] = None
    schedule: Optional[str] = None  # Cron-like schedule
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    error_message: Optional[str] = None
    output_path: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.metadata is None:
            self.metadata = {}

@dataclass
class JobExecution:
    """Job execution record"""
    execution_id: str
    job_id: str
    started_at: str
    completed_at: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    urls_processed: int = 0
    data_extracted: int = 0
    errors: List[str] = None
    output_files: List[str] = None
    performance_metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.output_files is None:
            self.output_files = []
        if self.performance_metrics is None:
            self.performance_metrics = {}

class ScrapingJobManager:
    """Manages scraping jobs and executions"""
    
    def __init__(self, data_dir: str = "data"):
        self.logger = get_logger("scraping_job_manager")
        self.data_dir = Path(data_dir)
        self.jobs_file = self.data_dir / "scraping_jobs.json"
        self.executions_file = self.data_dir / "job_executions.json"
        self.output_dir = self.data_dir / "scraping_output"
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Job storage
        self.jobs: Dict[str, ScrapingJob] = {}
        self.executions: Dict[str, JobExecution] = {}
        self.running_jobs: Dict[str, asyncio.Task] = {}
        
        # Load existing jobs
        self._load_jobs()
        self._load_executions()
        
        # Initialize session
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Compliant-One Scraper 1.0'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _generate_job_id(self) -> str:
        """Generate unique job ID"""
        timestamp = str(int(time.time()))
        return f"JOB_{timestamp}_{hashlib.md5(timestamp.encode()).hexdigest()[:8]}"
    
    def _generate_execution_id(self) -> str:
        """Generate unique execution ID"""
        timestamp = str(int(time.time()))
        return f"EXEC_{timestamp}_{hashlib.md5(timestamp.encode()).hexdigest()[:8]}"
    
    def _load_jobs(self):
        """Load jobs from storage"""
        try:
            if self.jobs_file.exists():
                with open(self.jobs_file, 'r') as f:
                    data = json.load(f)
                    for job_data in data:
                        job = ScrapingJob(**job_data)
                        # Convert enum strings back to enums
                        job.job_type = ScrapingType(job_data['job_type'])
                        job.status = JobStatus(job_data['status'])
                        job.priority = JobPriority(job_data['priority'])
                        self.jobs[job.job_id] = job
                
                self.logger.info(f"Loaded {len(self.jobs)} scraping jobs")
        except Exception as e:
            self.logger.error(f"Error loading jobs: {e}")
    
    def _load_executions(self):
        """Load executions from storage"""
        try:
            if self.executions_file.exists():
                with open(self.executions_file, 'r') as f:
                    data = json.load(f)
                    for exec_data in data:
                        execution = JobExecution(**exec_data)
                        execution.status = JobStatus(exec_data['status'])
                        self.executions[execution.execution_id] = execution
                
                self.logger.info(f"Loaded {len(self.executions)} job executions")
        except Exception as e:
            self.logger.error(f"Error loading executions: {e}")
    
    def _save_jobs(self):
        """Save jobs to storage"""
        try:
            job_data = []
            for job in self.jobs.values():
                data = asdict(job)
                # Convert enums to strings
                data['job_type'] = job.job_type.value
                data['status'] = job.status.value
                data['priority'] = job.priority.value
                job_data.append(data)
            
            with open(self.jobs_file, 'w') as f:
                json.dump(job_data, f, indent=2)
            
            self.logger.debug(f"Saved {len(job_data)} jobs")
        except Exception as e:
            self.logger.error(f"Error saving jobs: {e}")
    
    def _save_executions(self):
        """Save executions to storage"""
        try:
            exec_data = []
            for execution in self.executions.values():
                data = asdict(execution)
                data['status'] = execution.status.value
                exec_data.append(data)
            
            with open(self.executions_file, 'w') as f:
                json.dump(exec_data, f, indent=2)
            
            self.logger.debug(f"Saved {len(exec_data)} executions")
        except Exception as e:
            self.logger.error(f"Error saving executions: {e}")
    
    def create_job(
        self,
        name: str,
        job_type: ScrapingType,
        target_urls: List[str],
        priority: JobPriority = JobPriority.MEDIUM,
        config: Optional[Dict[str, Any]] = None,
        schedule: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new scraping job"""
        
        job_id = self._generate_job_id()
        
        job = ScrapingJob(
            job_id=job_id,
            name=name,
            job_type=job_type,
            target_urls=target_urls,
            status=JobStatus.PENDING,
            priority=priority,
            created_at=datetime.now().isoformat(),
            total_urls=len(target_urls),
            config=config or {},
            schedule=schedule,
            metadata=metadata or {}
        )
        
        self.jobs[job_id] = job
        self._save_jobs()
        
        self.logger.info(f"Created job {job_id}: {name} ({job_type.value})")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[ScrapingJob]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        job_type: Optional[ScrapingType] = None,
        priority: Optional[JobPriority] = None
    ) -> List[ScrapingJob]:
        """List jobs with optional filtering"""
        
        jobs = list(self.jobs.values())
        
        if status:
            jobs = [job for job in jobs if job.status == status]
        
        if job_type:
            jobs = [job for job in jobs if job.job_type == job_type]
        
        if priority:
            jobs = [job for job in jobs if job.priority == priority]
        
        # Sort by priority and creation time
        jobs.sort(key=lambda x: (x.priority.value, x.created_at), reverse=True)
        
        return jobs
    
    def update_job_status(self, job_id: str, status: JobStatus, error_message: Optional[str] = None):
        """Update job status"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.status = status
            
            if status == JobStatus.RUNNING and not job.started_at:
                job.started_at = datetime.now().isoformat()
            elif status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                job.completed_at = datetime.now().isoformat()
                if error_message:
                    job.error_message = error_message
            
            self._save_jobs()
            self.logger.info(f"Updated job {job_id} status to {status.value}")
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job"""
        if job_id in self.jobs:
            # Cancel if running
            if job_id in self.running_jobs:
                self.cancel_job(job_id)
            
            del self.jobs[job_id]
            self._save_jobs()
            
            self.logger.info(f"Deleted job {job_id}")
            return True
        
        return False
    
    async def execute_job(self, job_id: str) -> str:
        """Execute a scraping job"""
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        if job.status == JobStatus.RUNNING:
            raise ValueError(f"Job {job_id} is already running")
        
        execution_id = self._generate_execution_id()
        
        execution = JobExecution(
            execution_id=execution_id,
            job_id=job_id,
            started_at=datetime.now().isoformat(),
            status=JobStatus.RUNNING
        )
        
        self.executions[execution_id] = execution
        self._save_executions()
        
        # Update job status
        self.update_job_status(job_id, JobStatus.RUNNING)
        
        # Create and start task
        task = asyncio.create_task(self._run_job(job, execution))
        self.running_jobs[job_id] = task
        
        self.logger.info(f"Started execution {execution_id} for job {job_id}")
        return execution_id
    
    async def _run_job(self, job: ScrapingJob, execution: JobExecution):
        """Run the actual scraping job"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            output_dir = self.output_dir / job.job_id / execution.execution_id
            output_dir.mkdir(parents=True, exist_ok=True)
            
            job.output_path = str(output_dir)
            
            # Process URLs
            for i, url in enumerate(job.target_urls):
                if job.status == JobStatus.CANCELLED:
                    break
                
                try:
                    # Scrape URL
                    data = await self._scrape_url(url, job.config)
                    
                    if data:
                        # Save data
                        filename = f"data_{i+1}_{hashlib.md5(url.encode()).hexdigest()[:8]}.json"
                        output_file = output_dir / filename
                        
                        async with aiofiles.open(output_file, 'w') as f:
                            await f.write(json.dumps(data, indent=2))
                        
                        execution.output_files.append(str(output_file))
                        execution.data_extracted += len(data) if isinstance(data, list) else 1
                        job.successful_extractions += 1
                        job.data_extracted += len(data) if isinstance(data, list) else 1
                    
                    job.processed_urls += 1
                    execution.urls_processed += 1
                    
                except Exception as e:
                    self.logger.error(f"Error scraping {url}: {e}")
                    execution.errors.append(f"{url}: {str(e)}")
                    job.failed_extractions += 1
                
                # Update progress
                job.progress = (job.processed_urls / job.total_urls) * 100
                
                # Save progress
                self._save_jobs()
                self._save_executions()
                
                # Delay between requests
                delay = job.config.get('delay', 1.0)
                await asyncio.sleep(delay)
            
            # Complete execution
            if job.status != JobStatus.CANCELLED:
                execution.status = JobStatus.COMPLETED
                execution.completed_at = datetime.now().isoformat()
                self.update_job_status(job.job_id, JobStatus.COMPLETED)
            
            # Calculate performance metrics
            if execution.started_at:
                start_time = datetime.fromisoformat(execution.started_at)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                execution.performance_metrics = {
                    'duration_seconds': duration,
                    'urls_per_second': execution.urls_processed / duration if duration > 0 else 0,
                    'success_rate': (job.successful_extractions / job.total_urls) * 100 if job.total_urls > 0 else 0
                }
        
        except Exception as e:
            self.logger.error(f"Job execution failed: {e}")
            execution.status = JobStatus.FAILED
            execution.errors.append(f"Execution failed: {str(e)}")
            self.update_job_status(job.job_id, JobStatus.FAILED, str(e))
        
        finally:
            # Cleanup
            if job.job_id in self.running_jobs:
                del self.running_jobs[job.job_id]
            
            execution.completed_at = datetime.now().isoformat()
            self._save_jobs()
            self._save_executions()
    
    async def _scrape_url(self, url: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Scrape a single URL"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Basic data extraction (can be enhanced with specific parsers)
                    return {
                        'url': url,
                        'status_code': response.status,
                        'content_length': len(content),
                        'scraped_at': datetime.now().isoformat(),
                        'headers': dict(response.headers),
                        'content': content[:config.get('max_content_length', 10000)]  # Limit content
                    }
        
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        if job_id in self.running_jobs:
            task = self.running_jobs[job_id]
            task.cancel()
            self.update_job_status(job_id, JobStatus.CANCELLED)
            return True
        
        return False
    
    def get_job_statistics(self) -> Dict[str, Any]:
        """Get job statistics"""
        total_jobs = len(self.jobs)
        
        status_counts = {}
        type_counts = {}
        priority_counts = {}
        
        for job in self.jobs.values():
            status_counts[job.status.value] = status_counts.get(job.status.value, 0) + 1
            type_counts[job.job_type.value] = type_counts.get(job.job_type.value, 0) + 1
            priority_counts[job.priority.value] = priority_counts.get(job.priority.value, 0) + 1
        
        recent_executions = sorted(
            self.executions.values(),
            key=lambda x: x.started_at,
            reverse=True
        )[:10]
        
        return {
            'total_jobs': total_jobs,
            'running_jobs': len(self.running_jobs),
            'status_breakdown': status_counts,
            'type_breakdown': type_counts,
            'priority_breakdown': priority_counts,
            'total_executions': len(self.executions),
            'recent_executions': [asdict(exec) for exec in recent_executions]
        }
    
    def get_execution_history(self, job_id: Optional[str] = None) -> List[JobExecution]:
        """Get execution history"""
        executions = list(self.executions.values())
        
        if job_id:
            executions = [exec for exec in executions if exec.job_id == job_id]
        
        executions.sort(key=lambda x: x.started_at, reverse=True)
        return executions
