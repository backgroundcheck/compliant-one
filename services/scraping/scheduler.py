#!/usr/bin/env python3
"""
Scraping Scheduler
Manages scheduled scraping jobs and automated execution
"""

import asyncio
import schedule
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import croniter

from utils.logger import get_logger
from .job_manager import ScrapingJobManager, JobStatus

class ScrapingScheduler:
    """Manages scheduled execution of scraping jobs"""
    
    def __init__(self, job_manager: ScrapingJobManager):
        self.logger = get_logger("scraping_scheduler")
        self.job_manager = job_manager
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        
        # Schedule storage
        self.scheduled_jobs: Dict[str, Dict] = {}
    
    def start(self):
        """Start the scheduler"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            self.logger.info("Scraping scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.running:
            self.running = False
            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=5)
            self.logger.info("Scraping scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                self._check_cron_jobs()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(60)
    
    def _check_cron_jobs(self):
        """Check for cron-scheduled jobs that need to run"""
        now = datetime.now()
        
        for job in self.job_manager.list_jobs():
            if job.schedule and job.status != JobStatus.RUNNING:
                try:
                    # Parse cron expression
                    cron = croniter.croniter(job.schedule, now)
                    next_run = cron.get_next(datetime)
                    
                    # Check if job should run now
                    if job.last_run:
                        last_run = datetime.fromisoformat(job.last_run)
                        if now >= next_run and (now - last_run).total_seconds() > 60:
                            asyncio.run(self._execute_scheduled_job(job.job_id))
                    else:
                        # First run
                        if now >= next_run:
                            asyncio.run(self._execute_scheduled_job(job.job_id))
                
                except Exception as e:
                    self.logger.error(f"Error checking schedule for job {job.job_id}: {e}")
    
    async def _execute_scheduled_job(self, job_id: str):
        """Execute a scheduled job"""
        try:
            job = self.job_manager.get_job(job_id)
            if job:
                job.last_run = datetime.now().isoformat()
                execution_id = await self.job_manager.execute_job(job_id)
                self.logger.info(f"Executed scheduled job {job_id}, execution: {execution_id}")
        except Exception as e:
            self.logger.error(f"Error executing scheduled job {job_id}: {e}")
    
    def schedule_job(self, job_id: str, schedule_type: str, **kwargs):
        """Schedule a job for regular execution"""
        job = self.job_manager.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        if schedule_type == "interval":
            # Schedule at intervals
            interval = kwargs.get('interval', 60)  # minutes
            schedule.every(interval).minutes.do(self._schedule_job_execution, job_id)
        
        elif schedule_type == "daily":
            # Schedule daily at specific time
            time_str = kwargs.get('time', '00:00')
            schedule.every().day.at(time_str).do(self._schedule_job_execution, job_id)
        
        elif schedule_type == "weekly":
            # Schedule weekly
            day = kwargs.get('day', 'monday')
            time_str = kwargs.get('time', '00:00')
            getattr(schedule.every(), day).at(time_str).do(self._schedule_job_execution, job_id)
        
        elif schedule_type == "cron":
            # Cron expression
            cron_expr = kwargs.get('expression')
            if cron_expr:
                job.schedule = cron_expr
                self.job_manager._save_jobs()
        
        self.scheduled_jobs[job_id] = {
            'type': schedule_type,
            'created_at': datetime.now().isoformat(),
            **kwargs
        }
        
        self.logger.info(f"Scheduled job {job_id} with {schedule_type} schedule")
    
    def _schedule_job_execution(self, job_id: str):
        """Execute job from scheduler"""
        asyncio.run(self._execute_scheduled_job(job_id))
    
    def unschedule_job(self, job_id: str):
        """Remove job from schedule"""
        # Clear schedule library jobs
        schedule.clear(job_id)
        
        # Clear cron schedule
        job = self.job_manager.get_job(job_id)
        if job:
            job.schedule = None
            self.job_manager._save_jobs()
        
        # Remove from scheduled jobs
        if job_id in self.scheduled_jobs:
            del self.scheduled_jobs[job_id]
        
        self.logger.info(f"Unscheduled job {job_id}")
    
    def get_scheduled_jobs(self) -> Dict[str, Dict]:
        """Get all scheduled jobs"""
        return self.scheduled_jobs.copy()
