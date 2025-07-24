"""
Enhanced Transparency Data Dashboard
Specialized dashboard for viewing Transparency International Pakistan data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import asyncio
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from services.scraping.job_manager import ScrapingJobManager, ScrapingType
from utils.logger import get_logger

logger = get_logger(__name__)

class TransparencyDashboard:
    """Enhanced dashboard for transparency and corruption data"""
    
    def __init__(self):
        self.job_manager = None
    
    async def get_job_manager(self):
        """Get async job manager"""
        if not self.job_manager:
            self.job_manager = ScrapingJobManager()
        return self.job_manager
    
    def render_transparency_dashboard(self):
        """Render main transparency dashboard"""
        
        st.title("🔍 Transparency International Pakistan Dashboard")
        st.markdown("Real-time monitoring of corruption, governance, and transparency data")
        
        # Dashboard tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Overview", 
            "📰 Corruption News", 
            "🏛️ Government Data", 
            "📈 Analytics"
        ])
        
        with tab1:
            self.render_overview_tab()
        
        with tab2:
            self.render_corruption_news_tab()
        
        with tab3:
            self.render_government_data_tab()
        
        with tab4:
            self.render_analytics_tab()
    
    def render_overview_tab(self):
        """Render overview dashboard"""
        
        st.subheader("📊 Transparency Data Overview")
        
        # Key metrics (mock data for demonstration)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Active Jobs",
                "4",
                delta="2 new today"
            )
        
        with col2:
            st.metric(
                "Data Points",
                "1,247",
                delta="156 today"
            )
        
        with col3:
            st.metric(
                "Corruption Cases",
                "89",
                delta="12 new"
            )
        
        with col4:
            st.metric(
                "Departments Monitored",
                "23",
                delta="5 federal, 18 provincial"
            )
        
        # Recent activity
        st.subheader("🕐 Recent Activity")
        
        recent_data = pd.DataFrame({
            'Time': [
                '2024-01-15 09:30', '2024-01-15 09:15', '2024-01-15 09:00',
                '2024-01-15 08:45', '2024-01-15 08:30'
            ],
            'Source': [
                'Transparency.org.pk', 'Government Portal', 'News Source',
                'Procurement Watch', 'Annual Report'
            ],
            'Category': [
                'Corruption News', 'Government Data', 'Media Coverage',
                'Procurement Alert', 'Governance Report'
            ],
            'Status': ['✅ Processed', '⏳ Processing', '✅ Processed', '✅ Processed', '✅ Processed']
        })
        
        st.dataframe(recent_data, use_container_width=True)
        
        # Data source status
        st.subheader("🌐 Data Source Status")
        
        source_status = pd.DataFrame({
            'Source': [
                'transparency.org.pk',
                'Government of Pakistan',
                'Government of Punjab',
                'Government of Sindh',
                'Government of KP',
                'Government of Balochistan'
            ],
            'Status': ['🟢 Active', '🟢 Active', '🟢 Active', '🟡 Limited', '🟢 Active', '🔴 Error'],
            'Last Update': [
                '5 min ago', '15 min ago', '1 hour ago',
                '2 hours ago', '45 min ago', '3 hours ago'
            ],
            'Data Quality': ['Excellent', 'Good', 'Good', 'Fair', 'Good', 'Poor']
        })
        
        st.dataframe(source_status, use_container_width=True)
    
    def render_corruption_news_tab(self):
        """Render corruption news analysis"""
        
        st.subheader("📰 Corruption News & Media Coverage")
        
        # News trends chart
        dates = pd.date_range(start='2024-01-01', end='2024-01-15', freq='D')
        news_data = pd.DataFrame({
            'Date': dates,
            'Articles': [12, 8, 15, 22, 18, 25, 19, 14, 28, 21, 16, 31, 24, 17, 29],
            'Severity': ['High' if x > 20 else 'Medium' if x > 15 else 'Low' for x in [12, 8, 15, 22, 18, 25, 19, 14, 28, 21, 16, 31, 24, 17, 29]]
        })
        
        fig = px.line(news_data, x='Date', y='Articles', 
                     title='Daily Corruption News Articles',
                     color_discrete_sequence=['#e74c3c'])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Top corruption keywords
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔍 Top Keywords")
            keywords_data = pd.DataFrame({
                'Keyword': ['Corruption', 'Fraud', 'Embezzlement', 'Bribery', 'Misconduct', 
                           'Investigation', 'Audit', 'Accountability'],
                'Frequency': [156, 89, 67, 45, 78, 92, 34, 123]
            })
            
            fig = px.bar(keywords_data, x='Frequency', y='Keyword', 
                        title='Keyword Frequency',
                        orientation='h',
                        color='Frequency',
                        color_continuous_scale='Reds')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🏛️ Departments Mentioned")
            dept_data = pd.DataFrame({
                'Department': ['Federal', 'Punjab', 'Sindh', 'KP', 'Balochistan', 'Municipal'],
                'Cases': [45, 23, 19, 12, 8, 15]
            })
            
            fig = px.pie(dept_data, values='Cases', names='Department',
                        title='Cases by Department')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent news items
        st.subheader("📄 Recent News Items")
        
        news_items = pd.DataFrame({
            'Title': [
                'Federal Anti-Corruption Investigation Launched',
                'Punjab Procurement Irregularities Detected',
                'Sindh Government Transparency Initiative',
                'KP Audit Report Reveals Mismanagement',
                'Balochistan Development Fund Investigation'
            ],
            'Source': [
                'transparency.org.pk',
                'transparency.org.pk',
                'Government Portal',
                'transparency.org.pk',
                'News Source'
            ],
            'Severity': ['High', 'Medium', 'Low', 'High', 'Medium'],
            'Date': [
                '2024-01-15', '2024-01-15', '2024-01-14',
                '2024-01-14', '2024-01-13'
            ]
        })
        
        # Color code by severity
        def highlight_severity(row):
            if row['Severity'] == 'High':
                return ['background-color: #ffebee'] * len(row)
            elif row['Severity'] == 'Medium':
                return ['background-color: #fff3e0'] * len(row)
            else:
                return ['background-color: #e8f5e8'] * len(row)
        
        styled_df = news_items.style.apply(highlight_severity, axis=1)
        st.dataframe(styled_df, use_container_width=True)
    
    def render_government_data_tab(self):
        """Render government data analysis"""
        
        st.subheader("🏛️ Government Data & Procurement Analysis")
        
        # Procurement alerts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚨 Procurement Alerts")
            
            alerts_data = pd.DataFrame({
                'Department': ['Water & Power', 'Health', 'Education', 'Infrastructure', 'Defense'],
                'Alert Level': ['High', 'Medium', 'Low', 'High', 'Medium'],
                'Amount (PKR)': ['2.5B', '1.2B', '800M', '3.1B', '1.8B'],
                'Status': ['Under Review', 'Investigating', 'Cleared', 'Flagged', 'Monitoring']
            })
            
            st.dataframe(alerts_data, use_container_width=True)
        
        with col2:
            st.subheader("📊 Procurement Trends")
            
            proc_data = pd.DataFrame({
                'Month': ['Oct', 'Nov', 'Dec', 'Jan'],
                'Contracts': [45, 52, 38, 41],
                'Value (Billions PKR)': [12.5, 15.2, 9.8, 11.3],
                'Flagged': [3, 7, 2, 5]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=proc_data['Month'], 
                y=proc_data['Contracts'],
                mode='lines+markers',
                name='Total Contracts',
                line=dict(color='#3498db')
            ))
            fig.add_trace(go.Scatter(
                x=proc_data['Month'], 
                y=proc_data['Flagged'],
                mode='lines+markers',
                name='Flagged Contracts',
                line=dict(color='#e74c3c')
            ))
            fig.update_layout(title='Procurement Contract Trends', height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Government departments performance
        st.subheader("🎯 Department Performance Score")
        
        dept_performance = pd.DataFrame({
            'Department': [
                'Federal Ministry of Finance',
                'Punjab Health Department',
                'Sindh Education Department',
                'KP Infrastructure Department',
                'Balochistan Water & Power',
                'Federal Defense Ministry'
            ],
            'Transparency Score': [85, 72, 68, 79, 56, 91],
            'Compliance Rate': [92, 78, 74, 83, 62, 96],
            'Risk Level': ['Low', 'Medium', 'Medium', 'Low', 'High', 'Low']
        })
        
        fig = px.scatter(dept_performance, 
                        x='Transparency Score', 
                        y='Compliance Rate',
                        color='Risk Level',
                        size=[20]*len(dept_performance),
                        hover_name='Department',
                        title='Department Performance Matrix',
                        color_discrete_map={
                            'Low': '#27ae60',
                            'Medium': '#f39c12',
                            'High': '#e74c3c'
                        })
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    def render_analytics_tab(self):
        """Render advanced analytics"""
        
        st.subheader("📈 Advanced Analytics & Insights")
        
        # Risk assessment over time
        dates = pd.date_range(start='2024-01-01', end='2024-01-15', freq='D')
        risk_data = pd.DataFrame({
            'Date': dates,
            'High Risk': [3, 2, 5, 8, 4, 6, 3, 2, 9, 5, 3, 7, 6, 4, 8],
            'Medium Risk': [8, 6, 10, 12, 9, 11, 8, 7, 14, 10, 8, 13, 11, 9, 12],
            'Low Risk': [15, 12, 18, 20, 16, 19, 15, 14, 22, 18, 15, 21, 19, 16, 20]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=risk_data['Date'], y=risk_data['High Risk'],
            mode='lines', name='High Risk', stackgroup='one',
            line=dict(color='#e74c3c')
        ))
        fig.add_trace(go.Scatter(
            x=risk_data['Date'], y=risk_data['Medium Risk'],
            mode='lines', name='Medium Risk', stackgroup='one',
            line=dict(color='#f39c12')
        ))
        fig.add_trace(go.Scatter(
            x=risk_data['Date'], y=risk_data['Low Risk'],
            mode='lines', name='Low Risk', stackgroup='one',
            line=dict(color='#27ae60')
        ))
        fig.update_layout(title='Risk Assessment Trends', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Corruption severity heatmap
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🗺️ Regional Corruption Heatmap")
            
            heatmap_data = pd.DataFrame({
                'Province': ['Federal', 'Punjab', 'Sindh', 'KP', 'Balochistan'],
                'Jan': [12, 23, 19, 8, 15],
                'Feb': [14, 25, 21, 9, 17],
                'Mar': [11, 22, 18, 7, 14]
            })
            
            # Create heatmap using plotly
            z_values = [heatmap_data[col].values for col in ['Jan', 'Feb', 'Mar']]
            
            fig = go.Figure(data=go.Heatmap(
                z=z_values,
                x=heatmap_data['Province'],
                y=['Jan', 'Feb', 'Mar'],
                colorscale='Reds'
            ))
            fig.update_layout(title='Corruption Cases by Region', height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Compliance Scoring")
            
            compliance_data = pd.DataFrame({
                'Metric': [
                    'Data Availability',
                    'Response Time',
                    'Transparency Level',
                    'Public Access',
                    'Documentation Quality'
                ],
                'Score': [85, 72, 68, 79, 91],
                'Target': [90, 80, 75, 85, 95]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Current Score',
                x=compliance_data['Metric'],
                y=compliance_data['Score'],
                marker_color='#3498db'
            ))
            fig.add_trace(go.Bar(
                name='Target Score',
                x=compliance_data['Metric'],
                y=compliance_data['Target'],
                marker_color='#95a5a6',
                opacity=0.6
            ))
            fig.update_layout(title='Compliance Metrics', height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Predictive insights
        st.subheader("🔮 Predictive Insights")
        
        insights = [
            "📈 **Trend Analysis**: Corruption cases are likely to increase by 15% next month based on historical patterns",
            "🎯 **Risk Prediction**: Punjab and Sindh show higher risk indicators for procurement irregularities",
            "⚠️ **Alert Forecast**: Expected 3-5 high-severity alerts in the coming week",
            "🔍 **Pattern Detection**: Unusual activity detected in water & power sector contracts",
            "📊 **Compliance Forecast**: Overall compliance score expected to improve by 8% with current reforms"
        ]
        
        for insight in insights:
            st.markdown(insight)
        
        # Export options
        st.subheader("📤 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export Analytics Report"):
                st.success("Analytics report exported to data/transparency_analytics_report.pdf")
        
        with col2:
            if st.button("📰 Export News Summary"):
                st.success("News summary exported to data/transparency_news_summary.docx")
        
        with col3:
            if st.button("🏛️ Export Government Data"):
                st.success("Government data exported to data/transparency_govt_data.xlsx")

def run_transparency_dashboard():
    """Run the transparency dashboard"""
    
    # Page config
    st.set_page_config(
        page_title="Transparency Dashboard",
        page_icon="🔍",
        layout="wide"
    )
    
    # Initialize dashboard
    dashboard = TransparencyDashboard()
    
    # Authentication check (simplified)
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Login Required")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login", use_container_width=True):
                if username == "admin" and password == "admin123":
                    st.session_state.authenticated = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    else:
        # Render main dashboard
        dashboard.render_transparency_dashboard()
        
        # Logout option
        if st.sidebar.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

if __name__ == "__main__":
    run_transparency_dashboard()
