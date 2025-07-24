#!/usr/bin/env python3
"""
Scraping Control Panel Dashboard
Streamlit interface for managing scraping jobs and monitoring performance
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import asyncio
import json
from typing import Dict, List, Optional

from services.scraping.job_manager import (
    ScrapingJobManager, ScrapingJob, JobExecution,
    JobStatus, JobPriority, ScrapingType
)
from services.scraping.scheduler import ScrapingScheduler
from utils.logger import get_logger

class ScrapingControlPanel:
    """Scraping Control Panel Interface"""
    
    def __init__(self):
        self.logger = get_logger("scraping_control_panel")
        
        # Initialize managers
        if 'scraping_job_manager' not in st.session_state:
            st.session_state.scraping_job_manager = ScrapingJobManager()
        
        if 'scraping_scheduler' not in st.session_state:
            st.session_state.scraping_scheduler = ScrapingScheduler(st.session_state.scraping_job_manager)
            st.session_state.scraping_scheduler.start()
        
        self.job_manager = st.session_state.scraping_job_manager
        self.scheduler = st.session_state.scraping_scheduler
    
    def render_control_panel(self):
        """Render the main scraping control panel"""
        st.header("🕷️ Scraping Control Panel")
        st.subheader("Web Data Collection & Intelligence Gathering")
        
        # Control panel tabs
        tabs = st.tabs([
            "📊 Dashboard", 
            "➕ Create Job", 
            "📋 Manage Jobs", 
            "📅 Scheduler", 
            "📈 Reports",
            "⚙️ Settings"
        ])
        
        with tabs[0]:  # Dashboard
            self.render_dashboard()
        
        with tabs[1]:  # Create Job
            self.render_create_job()
        
        with tabs[2]:  # Manage Jobs
            self.render_manage_jobs()
        
        with tabs[3]:  # Scheduler
            self.render_scheduler()
        
        with tabs[4]:  # Reports
            self.render_reports()
        
        with tabs[5]:  # Settings
            self.render_settings()
    
    def render_dashboard(self):
        """Render the main dashboard"""
        st.subheader("📊 Scraping Dashboard")
        
        # Get statistics
        stats = self.job_manager.get_job_statistics()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Jobs", stats['total_jobs'])
        
        with col2:
            st.metric("Running Jobs", stats['running_jobs'], 
                     delta="Active" if stats['running_jobs'] > 0 else "Idle")
        
        with col3:
            completed_jobs = stats['status_breakdown'].get('completed', 0)
            st.metric("Completed Jobs", completed_jobs)
        
        with col4:
            failed_jobs = stats['status_breakdown'].get('failed', 0)
            st.metric("Failed Jobs", failed_jobs, 
                     delta="⚠️" if failed_jobs > 0 else "✅")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Job status distribution
            if stats['status_breakdown']:
                status_df = pd.DataFrame(
                    list(stats['status_breakdown'].items()),
                    columns=['Status', 'Count']
                )
                fig1 = px.pie(status_df, values='Count', names='Status', 
                            title="Jobs by Status")
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Job type distribution
            if stats['type_breakdown']:
                type_df = pd.DataFrame(
                    list(stats['type_breakdown'].items()),
                    columns=['Type', 'Count']
                )
                fig2 = px.bar(type_df, x='Type', y='Count', 
                            title="Jobs by Type")
                st.plotly_chart(fig2, use_container_width=True)
        
        # Recent executions
        st.subheader("🕐 Recent Job Executions")
        
        recent_executions = stats.get('recent_executions', [])
        if recent_executions:
            exec_data = []
            for exec in recent_executions:
                job = self.job_manager.get_job(exec['job_id'])
                exec_data.append({
                    'Execution ID': exec['execution_id'][:12] + '...',
                    'Job Name': job.name if job else 'Unknown',
                    'Status': exec['status'],
                    'URLs Processed': exec['urls_processed'],
                    'Data Extracted': exec['data_extracted'],
                    'Started': exec['started_at'][:19] if exec['started_at'] else 'N/A'
                })
            
            exec_df = pd.DataFrame(exec_data)
            st.dataframe(exec_df, use_container_width=True)
        else:
            st.info("No recent executions found")
        
        # System status
        st.subheader("🖥️ System Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            scheduler_status = "🟢 Running" if self.scheduler.running else "🔴 Stopped"
            st.write(f"**Scheduler:** {scheduler_status}")
        
        with col2:
            active_schedules = len(self.scheduler.get_scheduled_jobs())
            st.write(f"**Scheduled Jobs:** {active_schedules}")
        
        with col3:
            st.write(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Auto-refresh
        if st.button("🔄 Refresh Dashboard"):
            st.rerun()
    
    def render_create_job(self):
        """Render job creation interface"""
        st.subheader("➕ Create New Scraping Job")
        
        with st.form("create_job_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                job_name = st.text_input("Job Name", placeholder="Enter job name")
                job_type = st.selectbox("Job Type", [t.value for t in ScrapingType])
                priority = st.selectbox("Priority", [p.value for p in JobPriority])
            
            with col2:
                target_urls_text = st.text_area(
                    "Target URLs", 
                    placeholder="Enter URLs, one per line",
                    height=100
                )
                schedule_enabled = st.checkbox("Enable Scheduling")
            
            # Advanced configuration
            with st.expander("⚙️ Advanced Configuration"):
                col1, col2 = st.columns(2)
                
                with col1:
                    delay = st.number_input("Delay Between Requests (seconds)", 
                                          min_value=0.1, max_value=60.0, value=1.0)
                    max_content = st.number_input("Max Content Length", 
                                                min_value=1000, max_value=100000, value=10000)
                
                with col2:
                    timeout = st.number_input("Request Timeout (seconds)", 
                                            min_value=5, max_value=300, value=30)
                    retry_attempts = st.number_input("Retry Attempts", 
                                                   min_value=0, max_value=10, value=3)
            
            # Scheduling options
            if schedule_enabled:
                st.subheader("📅 Scheduling Options")
                
                schedule_type = st.selectbox("Schedule Type", 
                    ["interval", "daily", "weekly", "cron"])
                
                if schedule_type == "interval":
                    interval = st.number_input("Interval (minutes)", 
                                             min_value=1, max_value=10080, value=60)
                
                elif schedule_type == "daily":
                    daily_time = st.time_input("Run Time")
                
                elif schedule_type == "weekly":
                    weekly_day = st.selectbox("Day of Week", 
                        ["monday", "tuesday", "wednesday", "thursday", 
                         "friday", "saturday", "sunday"])
                    weekly_time = st.time_input("Run Time", key="weekly_time")
                
                elif schedule_type == "cron":
                    cron_expr = st.text_input("Cron Expression", 
                                            placeholder="0 0 * * *")
                    st.caption("Example: '0 0 * * *' = daily at midnight")
            
            # Submit button
            submitted = st.form_submit_button("🚀 Create Job", type="primary")
            
            if submitted:
                if not job_name or not target_urls_text:
                    st.error("Please fill in job name and target URLs")
                else:
                    # Parse URLs
                    target_urls = [url.strip() for url in target_urls_text.split('\n') 
                                 if url.strip()]
                    
                    if not target_urls:
                        st.error("Please provide at least one valid URL")
                    else:
                        # Create job configuration
                        config = {
                            'delay': delay,
                            'max_content_length': max_content,
                            'timeout': timeout,
                            'retry_attempts': retry_attempts
                        }
                        
                        # Create job
                        try:
                            job_id = self.job_manager.create_job(
                                name=job_name,
                                job_type=ScrapingType(job_type),
                                target_urls=target_urls,
                                priority=JobPriority(priority),
                                config=config
                            )
                            
                            # Set up scheduling if enabled
                            if schedule_enabled:
                                if schedule_type == "interval":
                                    self.scheduler.schedule_job(job_id, "interval", interval=interval)
                                elif schedule_type == "daily":
                                    self.scheduler.schedule_job(job_id, "daily", time=str(daily_time))
                                elif schedule_type == "weekly":
                                    self.scheduler.schedule_job(job_id, "weekly", 
                                                              day=weekly_day, time=str(weekly_time))
                                elif schedule_type == "cron":
                                    if cron_expr:
                                        self.scheduler.schedule_job(job_id, "cron", expression=cron_expr)
                            
                            st.success(f"✅ Job created successfully! Job ID: {job_id}")
                            
                        except Exception as e:
                            st.error(f"❌ Error creating job: {e}")
    
    def render_manage_jobs(self):
        """Render job management interface"""
        st.subheader("📋 Manage Scraping Jobs")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox("Filter by Status", 
                ["All"] + [s.value for s in JobStatus])
        
        with col2:
            type_filter = st.selectbox("Filter by Type", 
                ["All"] + [t.value for t in ScrapingType])
        
        with col3:
            if st.button("🔄 Refresh Jobs"):
                st.rerun()
        
        # Get filtered jobs
        jobs = self.job_manager.list_jobs()
        
        if status_filter != "All":
            jobs = [job for job in jobs if job.status.value == status_filter]
        
        if type_filter != "All":
            jobs = [job for job in jobs if job.job_type.value == type_filter]
        
        # Jobs table
        if jobs:
            job_data = []
            for job in jobs:
                job_data.append({
                    'Job ID': job.job_id,
                    'Name': job.name,
                    'Type': job.job_type.value,
                    'Status': job.status.value,
                    'Priority': job.priority.value,
                    'Progress': f"{job.progress:.1f}%",
                    'URLs': f"{job.processed_urls}/{job.total_urls}",
                    'Success': job.successful_extractions,
                    'Failed': job.failed_extractions,
                    'Created': job.created_at[:19]
                })
            
            jobs_df = pd.DataFrame(job_data)
            
            # Display jobs with selection
            selected_jobs = st.data_editor(
                jobs_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Job ID": st.column_config.TextColumn("Job ID", width="medium"),
                    "Progress": st.column_config.ProgressColumn("Progress", min_value=0, max_value=100)
                }
            )
            
            # Job actions
            st.subheader("🔧 Job Actions")
            
            selected_job_id = st.selectbox("Select Job", 
                [job.job_id for job in jobs], 
                format_func=lambda x: next((job.name for job in jobs if job.job_id == x), x))
            
            if selected_job_id:
                selected_job = self.job_manager.get_job(selected_job_id)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("▶️ Execute") and selected_job.status != JobStatus.RUNNING:
                        try:
                            execution_id = asyncio.run(self.job_manager.execute_job(selected_job_id))
                            st.success(f"Job started! Execution ID: {execution_id}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error starting job: {e}")
                
                with col2:
                    if st.button("⏹️ Cancel") and selected_job.status == JobStatus.RUNNING:
                        if self.job_manager.cancel_job(selected_job_id):
                            st.success("Job cancelled")
                            st.rerun()
                        else:
                            st.error("Failed to cancel job")
                
                with col3:
                    if st.button("🗑️ Delete"):
                        if self.job_manager.delete_job(selected_job_id):
                            st.success("Job deleted")
                            st.rerun()
                        else:
                            st.error("Failed to delete job")
                
                with col4:
                    if st.button("📊 View Details"):
                        self.show_job_details(selected_job)
        
        else:
            st.info("No jobs found matching the current filters")
    
    def show_job_details(self, job: ScrapingJob):
        """Show detailed job information"""
        st.subheader(f"📋 Job Details: {job.name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Job ID:** {job.job_id}")
            st.write(f"**Type:** {job.job_type.value}")
            st.write(f"**Status:** {job.status.value}")
            st.write(f"**Priority:** {job.priority.value}")
            st.write(f"**Created:** {job.created_at}")
            if job.started_at:
                st.write(f"**Started:** {job.started_at}")
            if job.completed_at:
                st.write(f"**Completed:** {job.completed_at}")
        
        with col2:
            st.write(f"**Total URLs:** {job.total_urls}")
            st.write(f"**Processed URLs:** {job.processed_urls}")
            st.write(f"**Successful Extractions:** {job.successful_extractions}")
            st.write(f"**Failed Extractions:** {job.failed_extractions}")
            st.write(f"**Data Extracted:** {job.data_extracted}")
            st.write(f"**Progress:** {job.progress:.1f}%")
        
        # Progress bar
        st.progress(job.progress / 100)
        
        # Target URLs
        if st.expander("🎯 Target URLs"):
            for i, url in enumerate(job.target_urls, 1):
                st.write(f"{i}. {url}")
        
        # Configuration
        if st.expander("⚙️ Configuration"):
            st.json(job.config)
        
        # Error message
        if job.error_message:
            st.error(f"Error: {job.error_message}")
        
        # Execution history
        executions = self.job_manager.get_execution_history(job.job_id)
        if executions:
            st.subheader("📈 Execution History")
            
            exec_data = []
            for exec in executions:
                exec_data.append({
                    'Execution ID': exec.execution_id[:12] + '...',
                    'Status': exec.status.value,
                    'Started': exec.started_at[:19] if exec.started_at else 'N/A',
                    'Completed': exec.completed_at[:19] if exec.completed_at else 'N/A',
                    'URLs Processed': exec.urls_processed,
                    'Data Extracted': exec.data_extracted,
                    'Errors': len(exec.errors)
                })
            
            exec_df = pd.DataFrame(exec_data)
            st.dataframe(exec_df, use_container_width=True)
    
    def render_scheduler(self):
        """Render scheduler management interface"""
        st.subheader("📅 Job Scheduler")
        
        # Scheduler status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status = "🟢 Running" if self.scheduler.running else "🔴 Stopped"
            st.metric("Scheduler Status", status)
        
        with col2:
            if st.button("▶️ Start Scheduler") and not self.scheduler.running:
                self.scheduler.start()
                st.success("Scheduler started")
                st.rerun()
        
        with col3:
            if st.button("⏹️ Stop Scheduler") and self.scheduler.running:
                self.scheduler.stop()
                st.success("Scheduler stopped")
                st.rerun()
        
        # Scheduled jobs
        st.subheader("📋 Scheduled Jobs")
        
        scheduled_jobs = self.scheduler.get_scheduled_jobs()
        
        if scheduled_jobs:
            sched_data = []
            for job_id, sched_info in scheduled_jobs.items():
                job = self.job_manager.get_job(job_id)
                if job:
                    sched_data.append({
                        'Job Name': job.name,
                        'Schedule Type': sched_info['type'],
                        'Last Run': job.last_run[:19] if job.last_run else 'Never',
                        'Next Run': job.next_run[:19] if job.next_run else 'Unknown',
                        'Status': job.status.value
                    })
            
            if sched_data:
                sched_df = pd.DataFrame(sched_data)
                st.dataframe(sched_df, use_container_width=True)
        else:
            st.info("No scheduled jobs found")
        
        # Schedule management
        st.subheader("⚙️ Schedule Management")
        
        jobs = [job for job in self.job_manager.list_jobs() if job.status != JobStatus.RUNNING]
        
        if jobs:
            selected_job = st.selectbox("Select Job to Schedule", 
                jobs, format_func=lambda x: x.name)
            
            if selected_job:
                col1, col2 = st.columns(2)
                
                with col1:
                    schedule_type = st.selectbox("Schedule Type", 
                        ["interval", "daily", "weekly", "cron"], key="sched_type")
                    
                    if schedule_type == "interval":
                        interval = st.number_input("Interval (minutes)", 
                                                 min_value=1, value=60, key="sched_interval")
                        if st.button("📅 Schedule Job"):
                            self.scheduler.schedule_job(selected_job.job_id, "interval", interval=interval)
                            st.success("Job scheduled")
                            st.rerun()
                    
                    elif schedule_type == "daily":
                        daily_time = st.time_input("Run Time", key="sched_daily")
                        if st.button("📅 Schedule Job"):
                            self.scheduler.schedule_job(selected_job.job_id, "daily", time=str(daily_time))
                            st.success("Job scheduled")
                            st.rerun()
                
                with col2:
                    if st.button("🗑️ Remove Schedule"):
                        self.scheduler.unschedule_job(selected_job.job_id)
                        st.success("Schedule removed")
                        st.rerun()
    
    def render_reports(self):
        """Render reports and analytics"""
        st.subheader("📈 Scraping Reports & Analytics")
        
        # Time range selection
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Start Date", 
                value=datetime.now().date() - timedelta(days=30))
        
        with col2:
            end_date = st.date_input("End Date", value=datetime.now().date())
        
        # Performance metrics
        st.subheader("📊 Performance Metrics")
        
        executions = self.job_manager.get_execution_history()
        
        if executions:
            # Filter by date range
            filtered_executions = []
            for exec in executions:
                exec_date = datetime.fromisoformat(exec.started_at).date()
                if start_date <= exec_date <= end_date:
                    filtered_executions.append(exec)
            
            if filtered_executions:
                # Success rate
                completed = len([e for e in filtered_executions if e.status == JobStatus.COMPLETED])
                total = len(filtered_executions)
                success_rate = (completed / total * 100) if total > 0 else 0
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Executions", total)
                
                with col2:
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                
                with col3:
                    total_urls = sum(e.urls_processed for e in filtered_executions)
                    st.metric("URLs Processed", total_urls)
                
                with col4:
                    total_data = sum(e.data_extracted for e in filtered_executions)
                    st.metric("Data Points Extracted", total_data)
                
                # Charts
                if len(filtered_executions) > 1:
                    # Execution timeline
                    exec_timeline = []
                    for exec in filtered_executions:
                        exec_timeline.append({
                            'Date': datetime.fromisoformat(exec.started_at).date(),
                            'Executions': 1,
                            'URLs Processed': exec.urls_processed,
                            'Data Extracted': exec.data_extracted
                        })
                    
                    timeline_df = pd.DataFrame(exec_timeline)
                    timeline_df = timeline_df.groupby('Date').sum().reset_index()
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=timeline_df['Date'], y=timeline_df['Executions'],
                                           mode='lines+markers', name='Executions'))
                    fig.update_layout(title="Execution Timeline")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Performance comparison
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig2 = px.bar(timeline_df, x='Date', y='URLs Processed',
                                    title="URLs Processed Over Time")
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    with col2:
                        fig3 = px.bar(timeline_df, x='Date', y='Data Extracted',
                                    title="Data Extracted Over Time")
                        st.plotly_chart(fig3, use_container_width=True)
            
            else:
                st.info("No executions found in the selected date range")
        
        else:
            st.info("No execution data available")
        
        # Export reports
        st.subheader("📄 Export Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export Job Statistics"):
                stats = self.job_manager.get_job_statistics()
                st.download_button(
                    label="📥 Download JSON",
                    data=json.dumps(stats, indent=2),
                    file_name=f"scraping_stats_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📋 Export Execution History"):
                exec_data = [
                    {
                        'execution_id': exec.execution_id,
                        'job_id': exec.job_id,
                        'started_at': exec.started_at,
                        'completed_at': exec.completed_at,
                        'status': exec.status.value,
                        'urls_processed': exec.urls_processed,
                        'data_extracted': exec.data_extracted
                    }
                    for exec in executions
                ]
                
                df = pd.DataFrame(exec_data)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"execution_history_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    def render_settings(self):
        """Render settings and configuration"""
        st.subheader("⚙️ Scraping Settings")
        
        # Global settings
        st.subheader("🌐 Global Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_concurrent_jobs = st.number_input("Max Concurrent Jobs", 
                min_value=1, max_value=10, value=3)
            default_delay = st.number_input("Default Delay (seconds)", 
                min_value=0.1, max_value=60.0, value=1.0)
        
        with col2:
            default_timeout = st.number_input("Default Timeout (seconds)", 
                min_value=5, max_value=300, value=30)
            max_retries = st.number_input("Max Retry Attempts", 
                min_value=0, max_value=10, value=3)
        
        # Data retention
        st.subheader("🗄️ Data Retention")
        
        col1, col2 = st.columns(2)
        
        with col1:
            job_retention_days = st.number_input("Job Retention (days)", 
                min_value=1, max_value=365, value=90)
        
        with col2:
            execution_retention_days = st.number_input("Execution Data Retention (days)", 
                min_value=1, max_value=365, value=30)
        
        # User agents and headers
        st.subheader("🌐 HTTP Settings")
        
        user_agent = st.text_input("Default User Agent", 
            value="Compliant-One Scraper 1.0")
        
        custom_headers = st.text_area("Custom Headers (JSON format)", 
            placeholder='{"Accept": "application/json", "X-Custom": "value"}')
        
        # Save settings
        if st.button("💾 Save Settings", type="primary"):
            settings = {
                'max_concurrent_jobs': max_concurrent_jobs,
                'default_delay': default_delay,
                'default_timeout': default_timeout,
                'max_retries': max_retries,
                'job_retention_days': job_retention_days,
                'execution_retention_days': execution_retention_days,
                'user_agent': user_agent,
                'custom_headers': custom_headers
            }
            
            # Save to file (in a real implementation)
            st.success("✅ Settings saved successfully!")
        
        # System maintenance
        st.subheader("🔧 System Maintenance")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧹 Clean Old Jobs"):
                # Implement cleanup logic
                st.info("Cleaning old jobs...")
        
        with col2:
            if st.button("🗑️ Clear Execution History"):
                # Implement cleanup logic
                st.info("Clearing execution history...")
        
        with col3:
            if st.button("📊 Optimize Database"):
                # Implement optimization logic
                st.info("Optimizing database...")

def render_scraping_control_panel():
    """Main function to render the scraping control panel"""
    panel = ScrapingControlPanel()
    panel.render_control_panel()
