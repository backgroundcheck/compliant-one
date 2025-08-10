"""
Compliant.one Dashboard - Main Streamlit Application
Advanced AI & Compliance Automation Platform
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
import numpy as np
import time
import json
import uuid
from datetime import datetime, timedelta

# Import our modules
from config.settings import get_config
from utils.logger import get_logger

# Advanced feature imports
try:
    from ai_engine.advanced_models import AdvancedModelManager
    from compliance.adverse_media import AdverseMediaMonitor
    from compliance.risk_rules import CustomRiskRulesEngine
    from compliance.case_management import CaseManagementSystem, CasePriority, CaseCategory, CaseStatus
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    # Create mock classes for missing modules
    class MockAdvancedModelManager:
        def __init__(self, config): pass
        def detect_anomalies(self, data): return []
    
    class MockAdverseMediaMonitor:
        def __init__(self, config): pass
    
    class MockCustomRiskRulesEngine:
        def __init__(self, config): pass
        def list_rules(self): return []
        def add_default_rules(self): pass
        def rules(self): return []
    
    class MockCaseManagementSystem:
        def __init__(self, config): pass
        def search_cases(self, filters, limit=50): return []
        def create_custom_case(self, data): return type('Case', (), {'case_id': '12345678'})()
        def create_case_from_template(self, template, entity_name, entity_type, assigned_to, created_by): 
            return type('Case', (), {'case_id': '12345678'})()
        def get_case_statistics(self): 
            return {'total_cases': 0, 'overdue_cases': 0, 'resolved_cases': 0, 
                   'average_resolution_hours': None, 'status_breakdown': {}, 'priority_breakdown': {}}
    
    # Mock enums
    class CasePriority:
        LOW = 'low'
        MEDIUM = 'medium'
        HIGH = 'high'
        CRITICAL = 'critical'
        
        @classmethod
        def __iter__(cls):
            return iter([cls.LOW, cls.MEDIUM, cls.HIGH, cls.CRITICAL])
    
    class CaseCategory:
        SANCTIONS = 'sanctions'
        AML = 'aml'
        PEP = 'pep'
        ADVERSE_MEDIA = 'adverse_media'
        
        @classmethod
        def __iter__(cls):
            return iter([cls.SANCTIONS, cls.AML, cls.PEP, cls.ADVERSE_MEDIA])
    
    class CaseStatus:
        OPEN = 'open'
        IN_PROGRESS = 'in_progress'
        CLOSED = 'closed'
        
        @classmethod
        def __iter__(cls):
            return iter([cls.OPEN, cls.IN_PROGRESS, cls.CLOSED])
    
    AdvancedModelManager = MockAdvancedModelManager
    AdverseMediaMonitor = MockAdverseMediaMonitor
    CustomRiskRulesEngine = MockCustomRiskRulesEngine
    CaseManagementSystem = MockCaseManagementSystem
    
    ADVANCED_FEATURES_AVAILABLE = False

# Configure page
st.set_page_config(
    page_title="Compliant.one",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize
config = get_config()
logger = get_logger(__name__)

# Initialize advanced components
if ADVANCED_FEATURES_AVAILABLE:
    if 'advanced_model_manager' not in st.session_state:
        st.session_state.advanced_model_manager = AdvancedModelManager(config.to_dict())
    
    if 'adverse_media_monitor' not in st.session_state:
        st.session_state.adverse_media_monitor = AdverseMediaMonitor(config.to_dict())
    
    if 'risk_rules_engine' not in st.session_state:
        st.session_state.risk_rules_engine = CustomRiskRulesEngine(config.to_dict())
    
    if 'case_management' not in st.session_state:
        st.session_state.case_management = CaseManagementSystem(config.to_dict())

def main():
    """Main dashboard application"""
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1f4e79/ffffff?text=Compliant.one", width=200)
        st.markdown("---")
        
        # Navigation
        if ADVANCED_FEATURES_AVAILABLE:
            page = st.selectbox(
                "Navigate to:",
                ["Dashboard", "Threat Intelligence", "Risk Assessment", "Compliance", 
                 "Case Management", "Advanced AI", "Adverse Media", "Risk Rules", "Alerts", "Settings"]
            )
        else:
            page = st.selectbox(
                "Navigate to:",
                ["Dashboard", "Threat Intelligence", "Risk Assessment", "Compliance", "Alerts", "Settings"]
            )
        
        st.markdown("---")
        
        # Quick stats
        st.metric("Active Threats", "42", "+5")
        st.metric("Risk Score", "7.2/10", "-0.3")
        st.metric("Compliance %", "94%", "+2%")
    
    # Main content
    if page == "Dashboard":
        show_dashboard()
    elif page == "Threat Intelligence":
        show_threat_intelligence()
    elif page == "Risk Assessment":
        show_risk_assessment()
    elif page == "Compliance":
        show_compliance()
    elif page == "Case Management" and ADVANCED_FEATURES_AVAILABLE:
        show_case_management()
    elif page == "Advanced AI" and ADVANCED_FEATURES_AVAILABLE:
        show_advanced_ai()
    elif page == "Adverse Media" and ADVANCED_FEATURES_AVAILABLE:
        show_adverse_media()
    elif page == "Risk Rules" and ADVANCED_FEATURES_AVAILABLE:
        show_risk_rules()
    elif page == "Alerts":
        show_alerts()
    elif page == "Settings":
        show_settings()

def show_dashboard():
    """Main dashboard view"""
    st.title("🛡️ Compliant.one Dashboard")
    st.markdown("Automated Risk & Compliance Monitoring Platform")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Risk Score",
            value="7.2/10",
            delta="-0.3",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            label="Active Alerts",
            value="23",
            delta="+5",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="Compliance Score",
            value="94%",
            delta="+2%"
        )
    
    with col4:
        st.metric(
            label="Entities Monitored",
            value="1,247",
            delta="+18"
        )
    
    # Advanced features overview
    if ADVANCED_FEATURES_AVAILABLE:
        st.markdown("---")
        st.subheader("🤖 Advanced AI & Automation")
        
        ai_col1, ai_col2, ai_col3, ai_col4 = st.columns(4)
        
        with ai_col1:
            st.metric("AI Models Active", "4/4", "🟢")
        
        with ai_col2:
            st.metric("Anomalies Detected", "12", "+3")
        
        with ai_col3:
            st.metric("Media Alerts", "8", "+2")
        
        with ai_col4:
            st.metric("Rules Active", "15", "+2")
    
    # Main dashboard content
    tab1, tab2, tab3, tab4 = st.tabs(["Real-time Monitoring", "Risk Analytics", "Compliance Status", "Recent Activity"])
    
    with tab1:
        st.subheader("🔴 Real-time Risk Monitoring")
        
        # Real-time data simulation
        chart_data = pd.DataFrame(
            np.random.randn(20, 3),
            columns=['Sanctions Risk', 'AML Risk', 'Reputational Risk']
        ).cumsum()
        
        st.line_chart(chart_data)
        
        # Current alerts
        st.subheader("Current High-Priority Alerts")
        alerts_data = [
            {"Time": "14:32", "Entity": "Global Finance Corp", "Type": "Sanctions Match", "Risk": "🔴 Critical", "Status": "Under Review"},
            {"Time": "14:15", "Entity": "Tech Innovations Ltd", "Type": "Adverse Media", "Risk": "🟡 Medium", "Status": "Investigating"},
            {"Time": "13:58", "Entity": "Investment Holdings", "Type": "PEP Exposure", "Risk": "🟠 High", "Status": "Pending Review"}
        ]
        
        st.dataframe(alerts_data, hide_index=True)
    
    with tab2:
        st.subheader("📊 Risk Analytics Dashboard")
        
        # Risk distribution
        risk_categories = ['Sanctions', 'AML/CFT', 'PEP', 'Adverse Media', 'Geographic', 'Regulatory']
        risk_scores = [8.2, 6.7, 4.3, 5.9, 7.1, 3.8]
        
        risk_df = pd.DataFrame({
            'Category': risk_categories,
            'Risk Score': risk_scores
        })
        
        st.bar_chart(risk_df.set_index('Category'))
        
        # Geographic risk heatmap
        st.subheader("Geographic Risk Distribution")
        geographic_data = {
            'Country': ['United States', 'United Kingdom', 'Germany', 'Singapore', 'Russia', 'Iran', 'North Korea'],
            'Risk Level': [2.1, 2.3, 1.8, 2.9, 8.7, 9.2, 9.8],
            'Entity Count': [450, 230, 180, 95, 23, 8, 2]
        }
        
        geo_df = pd.DataFrame(geographic_data)
        st.dataframe(geo_df, hide_index=True)
    
    with tab3:
        st.subheader("✅ Compliance Status Overview")
        
        compliance_metrics = [
            {"Regulation": "OFAC Sanctions", "Status": "🟢 Compliant", "Last Check": "2024-01-15 14:30", "Coverage": "100%"},
            {"Regulation": "EU Sanctions", "Status": "🟢 Compliant", "Last Check": "2024-01-15 14:30", "Coverage": "100%"},
            {"Regulation": "UK Sanctions", "Status": "🟡 Review Required", "Last Check": "2024-01-15 12:15", "Coverage": "98%"},
            {"Regulation": "AML/BSA", "Status": "🟢 Compliant", "Last Check": "2024-01-15 13:45", "Coverage": "100%"},
            {"Regulation": "GDPR", "Status": "🟢 Compliant", "Last Check": "2024-01-15 09:30", "Coverage": "100%"}
        ]
        
        st.dataframe(compliance_metrics, hide_index=True)
        
        # Compliance trend
        st.subheader("Compliance Score Trend")
        compliance_trend = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=15, freq='D'),
            'Compliance Score': np.random.uniform(92, 98, 15)
        })
        
        st.line_chart(compliance_trend.set_index('Date'))
    
    with tab4:
        st.subheader("📋 Recent Activity Log")
        
        activity_log = [
            {"Timestamp": "2024-01-15 14:32:15", "Event": "High-risk entity flagged", "Entity": "Global Finance Corp", "Action": "Investigation initiated"},
            {"Timestamp": "2024-01-15 14:15:42", "Event": "Adverse media detected", "Entity": "Tech Innovations Ltd", "Action": "Risk assessment updated"},
            {"Timestamp": "2024-01-15 13:58:33", "Event": "PEP relationship identified", "Entity": "Investment Holdings", "Action": "Enhanced monitoring enabled"},
            {"Timestamp": "2024-01-15 13:45:18", "Event": "Sanctions screening completed", "Entity": "Manufacturing Corp", "Action": "Cleared for transaction"},
            {"Timestamp": "2024-01-15 13:30:55", "Event": "Risk rule triggered", "Entity": "Crypto Exchange Ltd", "Action": "Manual review required"},
            {"Timestamp": "2024-01-15 13:12:44", "Event": "Compliance check passed", "Entity": "Software Solutions", "Action": "Risk profile updated"}
        ]
        
        st.dataframe(activity_log, hide_index=True)

def show_threat_intelligence():
    """Threat intelligence and OSINT view"""
    st.title("🔍 Threat Intelligence & OSINT")
    st.markdown("Advanced threat detection and open source intelligence gathering")
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input("Search Entity or Threat Intelligence", placeholder="Enter entity name, email, or identifier...")
    
    with col2:
        search_type = st.selectbox("Search Type", ["All Sources", "Sanctions Lists", "PEP Databases", "Adverse Media", "Dark Web"])
    
    if st.button("🔍 Search Intelligence", type="primary"):
        if search_query:
            with st.spinner(f"Searching {search_type.lower()} for '{search_query}'..."):
                time.sleep(2)  # Simulate API calls
                
                # Mock results
                results = {
                    "sanctions": [
                        {"List": "OFAC SDN", "Match": "85%", "Details": "Similar name pattern detected"},
                        {"List": "EU Consolidated", "Match": "92%", "Details": "Exact name match found"}
                    ],
                    "pep": [
                        {"Database": "World-Check", "Status": "PEP Family Member", "Relationship": "Spouse of former minister"},
                        {"Database": "Dow Jones", "Status": "RCA (Relative/Close Associate)", "Details": "Business partner relationship"}
                    ],
                    "adverse_media": [
                        {"Source": "Reuters", "Date": "2024-01-10", "Headline": "Investigation launched into financial irregularities", "Sentiment": "Negative"},
                        {"Source": "Financial Times", "Date": "2024-01-08", "Headline": "Regulatory compliance questioned", "Sentiment": "Negative"}
                    ]
                }
                
                # Display results
                st.success(f"Intelligence search completed for: {search_query}")
                
                tab1, tab2, tab3 = st.tabs(["Sanctions & Watchlists", "PEP & Associates", "Adverse Media"])
                
                with tab1:
                    st.subheader("Sanctions & Watchlist Results")
                    if results["sanctions"]:
                        st.dataframe(results["sanctions"], hide_index=True)
                    else:
                        st.info("No sanctions matches found")
                
                with tab2:
                    st.subheader("PEP & Associate Results")
                    if results["pep"]:
                        st.dataframe(results["pep"], hide_index=True)
                    else:
                        st.info("No PEP relationships identified")
                
                with tab3:
                    st.subheader("Adverse Media Results")
                    if results["adverse_media"]:
                        st.dataframe(results["adverse_media"], hide_index=True)
                    else:
                        st.info("No adverse media found")
        else:
            st.error("Please enter a search query")
    
    # Intelligence sources status
    st.markdown("---")
    st.subheader("📡 Intelligence Sources Status")
    
    sources_status = [
        {"Source": "OFAC SDN List", "Status": "🟢 Online", "Last Updated": "2024-01-15 12:00", "Records": "8,456"},
        {"Source": "EU Sanctions List", "Status": "🟢 Online", "Last Updated": "2024-01-15 11:45", "Records": "1,247"},
        {"Source": "UN Sanctions List", "Status": "🟢 Online", "Last Updated": "2024-01-15 10:30", "Records": "856"},
        {"Source": "World-Check", "Status": "🟡 Limited", "Last Updated": "2024-01-15 09:15", "Records": "250,000+"},
        {"Source": "Dark Web Feeds", "Status": "🟢 Online", "Last Updated": "2024-01-15 14:20", "Records": "Live"},
        {"Source": "News Aggregator", "Status": "🟢 Online", "Last Updated": "2024-01-15 14:30", "Records": "Live"}
    ]
    
    st.dataframe(sources_status, hide_index=True)

def show_risk_assessment():
    """Risk assessment and analytics view"""
    st.title("⚖️ Risk Assessment & Analytics")
    st.markdown("AI-powered risk scoring and predictive analytics")
    
    # Entity risk assessment
    st.subheader("🎯 Entity Risk Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        entity_name = st.text_input("Entity Name", placeholder="Enter entity for risk assessment...")
        entity_type = st.selectbox("Entity Type", ["Individual", "Company", "Organization", "Government"])
    
    with col2:
        assessment_type = st.selectbox("Assessment Type", ["Standard", "Enhanced Due Diligence", "Periodic Review"])
        include_predictions = st.checkbox("Include Predictive Analytics", value=True)
    
    if st.button("🔍 Assess Risk", type="primary"):
        if entity_name:
            with st.spinner(f"Analyzing risk profile for {entity_name}..."):
                time.sleep(3)  # Simulate AI processing
                
                # Generate mock risk assessment
                base_score = np.random.uniform(3.0, 8.5)
                
                risk_factors = {
                    "Sanctions Risk": np.random.uniform(1.0, 9.0),
                    "PEP Risk": np.random.uniform(1.0, 7.0),
                    "Adverse Media": np.random.uniform(2.0, 8.0),
                    "Geographic Risk": np.random.uniform(1.0, 9.0),
                    "Industry Risk": np.random.uniform(2.0, 6.0),
                    "Network Risk": np.random.uniform(1.0, 7.0)
                }
                
                st.success(f"Risk assessment completed for: {entity_name}")
                
                # Overall risk score
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Overall Risk Score", f"{base_score:.1f}/10", 
                             delta=f"{np.random.uniform(-1.5, 1.5):.1f}")
                
                with col2:
                    risk_level = "Low" if base_score < 4 else "Medium" if base_score < 7 else "High"
                    st.metric("Risk Level", risk_level)
                
                with col3:
                    confidence = np.random.uniform(0.75, 0.95)
                    st.metric("Confidence", f"{confidence:.1%}")
                
                # Risk factor breakdown
                st.subheader("Risk Factor Analysis")
                
                factor_df = pd.DataFrame(
                    list(risk_factors.items()),
                    columns=['Risk Factor', 'Score']
                )
                
                st.bar_chart(factor_df.set_index('Risk Factor'))
                
                # Detailed breakdown
                st.subheader("Detailed Risk Analysis")
                
                detailed_analysis = []
                for factor, score in risk_factors.items():
                    severity = "Low" if score < 4 else "Medium" if score < 7 else "High"
                    detailed_analysis.append({
                        "Factor": factor,
                        "Score": f"{score:.1f}/10",
                        "Severity": severity,
                        "Contributors": "Multiple factors identified" if score > 5 else "Standard risk profile"
                    })
                
                st.dataframe(detailed_analysis, hide_index=True)
        else:
            st.error("Please enter an entity name")
    
    # Analytics dashboard
    st.markdown("---")
    st.subheader("📊 Risk Analytics Dashboard")
    
    analytics_tab1, analytics_tab2, analytics_tab3, analytics_tab4 = st.tabs(["Portfolio Overview", "Geographic Analysis", "Industry Analysis", "Predictive Models"])
    
    with analytics_tab1:
        st.write("**Portfolio Risk Distribution**")
        
        # Risk distribution chart
        risk_distribution = {
            'Low Risk (0-3)': 245,
            'Medium Risk (4-6)': 456,
            'High Risk (7-8)': 89,
            'Critical Risk (9-10)': 12
        }
        
        st.bar_chart(risk_distribution)
        
        # Top risk entities
        st.write("**Highest Risk Entities**")
        top_risks = [
            {"Entity": "High Risk Corp", "Type": "Company", "Risk Score": "9.2", "Primary Concern": "Sanctions exposure"},
            {"Entity": "Suspicious Holdings", "Type": "Company", "Risk Score": "8.8", "Primary Concern": "PEP connections"},
            {"Entity": "John Doe", "Type": "Individual", "Risk Score": "8.5", "Primary Concern": "Adverse media"},
            {"Entity": "Risk Ventures", "Type": "Company", "Risk Score": "8.1", "Primary Concern": "Geographic risk"}
        ]
        
        st.dataframe(top_risks, hide_index=True)
    
    with analytics_tab2:
        st.write("**Geographic Risk Analysis**")
        
        geo_risk = pd.DataFrame({
            'Country': ['Russia', 'Iran', 'North Korea', 'Syria', 'Belarus', 'Venezuela', 'Myanmar'],
            'Average Risk Score': [8.9, 9.1, 9.8, 9.3, 7.8, 8.2, 8.6],
            'Entity Count': [23, 8, 2, 5, 12, 18, 9]
        })
        
        st.dataframe(geo_risk, hide_index=True)
        st.bar_chart(geo_risk.set_index('Country')['Average Risk Score'])
    
    with analytics_tab3:
        st.write("**Industry Risk Analysis**")
        
        industry_risk = pd.DataFrame({
            'Industry': ['Banking', 'Cryptocurrency', 'Oil & Gas', 'Technology', 'Real Estate', 'Pharmaceuticals'],
            'Average Risk Score': [5.2, 7.8, 6.9, 3.4, 4.7, 3.9],
            'High Risk %': [15, 34, 28, 8, 18, 12]
        })
        
        st.dataframe(industry_risk, hide_index=True)
        st.bar_chart(industry_risk.set_index('Industry')['Average Risk Score'])
    
    with analytics_tab4:
        st.write("**Predictive Risk Modeling**")
        st.info("🔮 AI-powered predictive models for risk forecasting")
        
        prediction_metrics = [
            {"Model": "Sanctions Risk Predictor", "Accuracy": "94.2%", "Last Trained": "2024-01-10", "Status": "🟢 Active"},
            {"Model": "PEP Detection Model", "Accuracy": "91.7%", "Last Trained": "2024-01-08", "Status": "🟢 Active"},
            {"Model": "Adverse Media Classifier", "Accuracy": "88.9%", "Last Trained": "2024-01-12", "Status": "🟡 Retraining"},
            {"Model": "Risk Score Predictor", "Accuracy": "92.5%", "Last Trained": "2024-01-15", "Status": "🟢 Active"}
        ]
        
        st.dataframe(prediction_metrics, hide_index=True)

def show_compliance():
    """Compliance monitoring and automation view"""
    st.title("✅ Compliance Automation")
    st.markdown("Automated compliance monitoring and regulatory adherence")
    
    # Compliance overview
    compliance_tab1, compliance_tab2, compliance_tab3, compliance_tab4 = st.tabs(
        ["Sanctions Screening", "AML Monitoring", "PEP Screening", "Regulatory Reports"]
    )
    
    with compliance_tab1:
        st.subheader("🚫 Sanctions Screening")
        
        # Screening interface
        screening_entity = st.text_input("Entity to Screen", placeholder="Enter entity name or identifier...")
        
        if st.button("🔍 Screen Against All Lists", type="primary"):
            if screening_entity:
                with st.spinner(f"Screening {screening_entity} against sanctions lists..."):
                    time.sleep(2)
                    
                    # Mock screening results
                    screening_results = [
                        {"List": "OFAC SDN", "Status": "🟢 Clear", "Match %": "0%", "Details": "No matches found"},
                        {"List": "OFAC Consolidated", "Status": "🟢 Clear", "Match %": "0%", "Details": "No matches found"},
                        {"List": "EU Sanctions", "Status": "🟡 Potential Match", "Match %": "78%", "Details": "Similar name detected"},
                        {"List": "UN Security Council", "Status": "🟢 Clear", "Match %": "0%", "Details": "No matches found"},
                        {"List": "UK HMT", "Status": "🟢 Clear", "Match %": "0%", "Details": "No matches found"}
                    ]
                    
                    st.dataframe(screening_results, hide_index=True)
                    
                    # Summary
                    potential_matches = sum(1 for result in screening_results if "Potential" in result["Status"])
                    if potential_matches > 0:
                        st.warning(f"⚠️ {potential_matches} potential match(es) found. Manual review required.")
                    else:
                        st.success("✅ Entity cleared - no sanctions matches found")
            else:
                st.error("Please enter an entity to screen")
    
    with compliance_tab2:
        st.subheader("💰 AML Monitoring")
        
        # Transaction monitoring
        st.write("**Suspicious Transaction Alerts**")
        
        aml_alerts = [
            {"Time": "14:25", "Customer": "ABC Corp", "Type": "Structuring", "Amount": "$9,800", "Status": "🔴 High Risk"},
            {"Time": "13:45", "Customer": "XYZ Ltd", "Type": "Rapid Movement", "Amount": "$45,000", "Status": "🟡 Medium Risk"},
            {"Time": "12:30", "Customer": "DEF Inc", "Type": "Cash Intensive", "Amount": "$15,000", "Status": "🟡 Medium Risk"}
        ]
        
        st.dataframe(aml_alerts, hide_index=True)
        
        # AML metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Alerts Today", "23", "+5")
        
        with col2:
            st.metric("SARs Filed (Month)", "8", "+2")
        
        with col3:
            st.metric("False Positive Rate", "12%", "-3%")
    
    with compliance_tab3:
        st.subheader("👤 PEP Screening")
        
        pep_entity = st.text_input("Screen for PEP Status", placeholder="Enter individual or entity name...")
        
        if st.button("🔍 Check PEP Status", type="primary"):
            if pep_entity:
                with st.spinner(f"Checking PEP status for {pep_entity}..."):
                    time.sleep(2)
                    
                    # Mock PEP results
                    pep_results = [
                        {"Database": "World-Check", "Status": "PEP", "Position": "Former Minister of Finance", "Country": "Example Country", "Risk": "High"},
                        {"Database": "Dow Jones", "Status": "RCA", "Relationship": "Business Associate", "Details": "Joint venture partner", "Risk": "Medium"},
                        {"Database": "Local Registry", "Status": "Clear", "Details": "No PEP designation found", "Risk": "Low"}
                    ]
                    
                    st.dataframe(pep_results, hide_index=True)
                    
                    # PEP summary
                    pep_matches = sum(1 for result in pep_results if result["Status"] in ["PEP", "RCA"])
                    if pep_matches > 0:
                        st.warning(f"⚠️ PEP or associate status identified. Enhanced due diligence required.")
                    else:
                        st.success("✅ No PEP status identified")
            else:
                st.error("Please enter an entity to screen")
    
    with compliance_tab4:
        st.subheader("📋 Regulatory Reports")
        
        # Report generation
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox("Report Type", ["SAR Summary", "Sanctions Screening Log", "PEP Review Report", "Compliance Metrics"])
            date_range = st.date_input("Date Range", value=[datetime.now().date() - timedelta(days=30), datetime.now().date()])
        
        with col2:
            report_format = st.selectbox("Format", ["PDF", "Excel", "CSV"])
            include_details = st.checkbox("Include Detailed Records", value=True)
        
        if st.button("📄 Generate Report", type="primary"):
            with st.spinner("Generating compliance report..."):
                time.sleep(2)
                
                st.success(f"✅ {report_type} generated successfully!")
                st.download_button(
                    label=f"📥 Download {report_type}",
                    data="Mock report data - replace with actual report generation",
                    file_name=f"{report_type.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d')}.{report_format.lower()}",
                    mime="application/octet-stream"
                )
        
        # Recent reports
        st.write("**Recent Reports**")
        recent_reports = [
            {"Date": "2024-01-15", "Type": "SAR Summary", "Period": "December 2023", "Status": "✅ Complete"},
            {"Date": "2024-01-10", "Type": "Sanctions Log", "Period": "Q4 2023", "Status": "✅ Complete"},
            {"Date": "2024-01-05", "Type": "PEP Review", "Period": "December 2023", "Status": "✅ Complete"}
        ]
        
        st.dataframe(recent_reports, hide_index=True)

def show_case_management():
    """Case management interface"""
    st.title("📁 Case Management")
    
    if not ADVANCED_FEATURES_AVAILABLE:
        st.error("Advanced features not available")
        return
    
    case_mgmt = st.session_state.case_management
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Active Cases", "Create Case", "Search Cases", "Statistics"])
    
    with tab1:
        st.subheader("Active Cases")
        
        # Get active cases
        active_cases = case_mgmt.search_cases({'status': 'open'}, limit=20)
        
        if active_cases:
            case_data = []
            for case in active_cases:
                case_data.append({
                    'Case ID': case.case_id[:8],
                    'Title': case.title,
                    'Entity': case.entity_name,
                    'Priority': case.priority.value.title(),
                    'Status': case.status.value.replace('_', ' ').title(),
                    'Assigned To': case.assigned_to,
                    'Created': case.created_at.strftime('%Y-%m-%d'),
                    'Due Date': case.due_date.strftime('%Y-%m-%d') if case.due_date else 'N/A'
                })
            
            st.dataframe(case_data, hide_index=True, use_container_width=True)
        else:
            st.info("No active cases found")
    
    with tab2:
        st.subheader("Create New Case")
        
        col1, col2 = st.columns(2)
        
        with col1:
            template = st.selectbox("Case Template", 
                                   ["sanctions_screening", "aml_investigation", "adverse_media_review", "custom"])
            
            entity_name = st.text_input("Entity Name", placeholder="Enter entity name")
            entity_type = st.selectbox("Entity Type", ["Individual", "Company", "Organization"])
            assigned_to = st.text_input("Assign To", placeholder="User ID or email")
        
        with col2:
            if template == "custom":
                title = st.text_input("Case Title")
                description = st.text_area("Description")
                category = st.selectbox("Category", [cat.value for cat in CaseCategory])
                priority = st.selectbox("Priority", [pri.value for pri in CasePriority])
        
        if st.button("Create Case", type="primary"):
            if entity_name and assigned_to:
                try:
                    if template == "custom":
                        case_data = {
                            'title': title,
                            'description': description,
                            'category': category,
                            'priority': priority,
                            'entity_name': entity_name,
                            'entity_type': entity_type,
                            'assigned_to': assigned_to,
                            'created_by': 'admin'  # In real app, would use current user
                        }
                        case = case_mgmt.create_custom_case(case_data)
                    else:
                        case = case_mgmt.create_case_from_template(
                            template, entity_name, entity_type, assigned_to, 'admin'
                        )
                    
                    st.success(f"Case {case.case_id[:8]} created successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating case: {e}")
            else:
                st.error("Please fill in required fields")
    
    with tab3:
        st.subheader("Search Cases")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_status = st.selectbox("Status", ["all"] + [s.value for s in CaseStatus])
            search_priority = st.selectbox("Priority", ["all"] + [p.value for p in CasePriority])
        
        with col2:
            search_category = st.selectbox("Category", ["all"] + [c.value for c in CaseCategory])
            search_assigned = st.text_input("Assigned To")
        
        with col3:
            search_entity = st.text_input("Entity Name")
            limit = st.number_input("Max Results", min_value=10, max_value=100, value=50)
        
        if st.button("Search", type="primary"):
            filters = {}
            if search_status != "all":
                filters['status'] = search_status
            if search_priority != "all":
                filters['priority'] = search_priority
            if search_category != "all":
                filters['category'] = search_category
            if search_assigned:
                filters['assigned_to'] = search_assigned
            if search_entity:
                filters['entity_name'] = search_entity
            
            search_results = case_mgmt.search_cases(filters, limit)
            
            if search_results:
                result_data = []
                for case in search_results:
                    result_data.append({
                        'Case ID': case.case_id[:8],
                        'Title': case.title,
                        'Entity': case.entity_name,
                        'Category': case.category.value.replace('_', ' ').title(),
                        'Priority': case.priority.value.title(),
                        'Status': case.status.value.replace('_', ' ').title(),
                        'Assigned To': case.assigned_to,
                        'Created': case.created_at.strftime('%Y-%m-%d %H:%M'),
                        'Risk Score': f"{case.risk_score:.1f}"
                    })
                
                st.dataframe(result_data, hide_index=True, use_container_width=True)
            else:
                st.info("No cases found matching criteria")
    
    with tab4:
        st.subheader("Case Statistics")
        
        stats = case_mgmt.get_case_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Cases", stats['total_cases'])
        
        with col2:
            st.metric("Overdue Cases", stats['overdue_cases'])
        
        with col3:
            st.metric("Resolved Cases", stats['resolved_cases'])
        
        with col4:
            avg_hours = stats['average_resolution_hours']
            if avg_hours:
                st.metric("Avg Resolution Time", f"{avg_hours:.1f}h")
            else:
                st.metric("Avg Resolution Time", "N/A")
        
        # Status breakdown
        st.subheader("Status Breakdown")
        if stats['status_breakdown']:
            status_df = pd.DataFrame(
                list(stats['status_breakdown'].items()),
                columns=['Status', 'Count']
            )
            st.bar_chart(status_df.set_index('Status'))
        
        # Priority breakdown
        st.subheader("Priority Breakdown")
        if stats['priority_breakdown']:
            priority_df = pd.DataFrame(
                list(stats['priority_breakdown'].items()),
                columns=['Priority', 'Count']
            )
            st.bar_chart(priority_df.set_index('Priority'))

def show_advanced_ai():
    """Advanced AI models interface"""
    st.title("🤖 Advanced AI Models")
    
    if not ADVANCED_FEATURES_AVAILABLE:
        st.error("Advanced AI features not available")
        return
    
    ai_manager = st.session_state.advanced_model_manager
    
    tab1, tab2, tab3 = st.tabs(["Anomaly Detection", "Predictive Analytics", "Network Analysis"])
    
    with tab1:
        st.subheader("Anomaly Detection Engine")
        st.info("🔍 Detect unusual patterns in transaction and behavior data")
        
        # Sample data upload
        uploaded_file = st.file_uploader("Upload Data for Analysis", type=['csv', 'json'])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                    st.write("Data Preview:")
                    st.dataframe(df.head(), use_container_width=True)
                    
                    if st.button("Run Anomaly Detection", type="primary"):
                        with st.spinner("Analyzing data for anomalies..."):
                            # Convert to appropriate format for analysis
                            anomalies = ai_manager.detect_anomalies(df.to_dict('records'))
                            
                            if anomalies:
                                st.subheader("Detected Anomalies")
                                
                                anomaly_data = []
                                for anomaly in anomalies:
                                    anomaly_data.append({
                                        'Record ID': anomaly.get('record_id', 'N/A'),
                                        'Anomaly Score': f"{anomaly.get('anomaly_score', 0):.3f}",
                                        'Severity': anomaly.get('severity', 'Unknown'),
                                        'Reasons': ', '.join(anomaly.get('reasons', [])),
                                        'Timestamp': anomaly.get('timestamp', 'N/A')
                                    })
                                
                                st.dataframe(anomaly_data, hide_index=True, use_container_width=True)
                                
                                # Visualization
                                if len(anomaly_data) > 0:
                                    severity_counts = {}
                                    for item in anomaly_data:
                                        sev = item['Severity']
                                        severity_counts[sev] = severity_counts.get(sev, 0) + 1
                                    
                                    st.subheader("Anomaly Distribution")
                                    st.bar_chart(severity_counts)
                            else:
                                st.success("No significant anomalies detected")
                                
            except Exception as e:
                st.error(f"Error processing data: {e}")
    
    with tab2:
        st.subheader("Predictive Analytics")
        st.info("📈 Forecast risk trends and predict future compliance issues")
        
        # Model selection
        model_type = st.selectbox("Prediction Model", 
                                 ["Risk Score Prediction", "Sanctions List Addition", "Adverse Media Alert"])
        
        if model_type == "Risk Score Prediction":
            st.write("**Risk Score Forecasting**")
            
            entity_name = st.text_input("Entity Name for Prediction")
            
            if st.button("Generate Risk Prediction", type="primary"):
                if entity_name:
                    with st.spinner("Generating prediction..."):
                        # Mock prediction data
                        prediction = {
                            'entity_name': entity_name,
                            'current_risk_score': np.random.uniform(2.0, 8.0),
                            'predicted_risk_score': np.random.uniform(2.0, 8.0),
                            'confidence': np.random.uniform(0.7, 0.95),
                            'risk_factors': ['Previous sanctions exposure', 'High-risk jurisdiction', 'Adverse media coverage'],
                            'prediction_horizon': '30 days'
                        }
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Current Risk Score", f"{prediction['current_risk_score']:.1f}/10")
                            st.metric("Predicted Risk Score", f"{prediction['predicted_risk_score']:.1f}/10",
                                    delta=f"{prediction['predicted_risk_score'] - prediction['current_risk_score']:.1f}")
                        
                        with col2:
                            st.metric("Prediction Confidence", f"{prediction['confidence']:.1%}")
                            st.metric("Prediction Horizon", prediction['prediction_horizon'])
                        
                        st.subheader("Key Risk Factors")
                        for factor in prediction['risk_factors']:
                            st.write(f"• {factor}")
                else:
                    st.error("Please enter an entity name")
    
    with tab3:
        st.subheader("Network Analysis")
        st.info("🕸️ Analyze relationships and connections between entities")
        
        # Network analysis options
        analysis_type = st.selectbox("Analysis Type", 
                                   ["Entity Connections", "Risk Propagation", "Compliance Network"])
        
        if analysis_type == "Entity Connections":
            entity_name = st.text_input("Primary Entity")
            depth = st.slider("Connection Depth", min_value=1, max_value=5, value=2)
            
            if st.button("Analyze Connections", type="primary"):
                if entity_name:
                    with st.spinner("Analyzing network connections..."):
                        # Mock network analysis
                        connections = [
                            {'Entity': 'ABC Corp', 'Relationship': 'Subsidiary', 'Risk Score': 6.2, 'Distance': 1},
                            {'Entity': 'XYZ Ltd', 'Relationship': 'Business Partner', 'Risk Score': 4.5, 'Distance': 1},
                            {'Entity': 'Risk Holdings', 'Relationship': 'Shareholder', 'Risk Score': 8.1, 'Distance': 2},
                            {'Entity': 'Safe Bank', 'Relationship': 'Financial Institution', 'Risk Score': 2.3, 'Distance': 1}
                        ]
                        
                        st.subheader(f"Network Connections for {entity_name}")
                        st.dataframe(connections, hide_index=True, use_container_width=True)
                        
                        # Risk distribution
                        risk_scores = [conn['Risk Score'] for conn in connections]
                        avg_risk = np.mean(risk_scores)
                        max_risk = np.max(risk_scores)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Connected Entities", len(connections))
                        with col2:
                            st.metric("Average Network Risk", f"{avg_risk:.1f}/10")
                        with col3:
                            st.metric("Highest Connected Risk", f"{max_risk:.1f}/10")
                else:
                    st.error("Please enter an entity name")

def show_adverse_media():
    """Adverse media monitoring interface"""
    st.title("📰 Adverse Media Monitoring")
    
    if not ADVANCED_FEATURES_AVAILABLE:
        st.error("Adverse media features not available")
        return
    
    media_monitor = st.session_state.adverse_media_monitor
    
    tab1, tab2, tab3 = st.tabs(["Live Monitoring", "Search & Analysis", "Alerts & Reports"])
    
    with tab1:
        st.subheader("Live Media Monitoring")
        st.info("🔴 Real-time monitoring of adverse media mentions")
        
        # Monitoring controls
        col1, col2 = st.columns(2)
        
        with col1:
            entity_to_monitor = st.text_input("Entity to Monitor")
            monitoring_active = st.checkbox("Enable Real-time Monitoring")
        
        with col2:
            alert_threshold = st.slider("Alert Threshold", min_value=0.1, max_value=1.0, value=0.7, step=0.1)
            max_alerts_per_hour = st.number_input("Max Alerts/Hour", min_value=1, max_value=100, value=10)
        
        if monitoring_active and entity_to_monitor:
            with st.spinner("Monitoring live media feeds..."):
                # Simulate real-time monitoring
                time.sleep(2)
                
                # Mock recent alerts
                recent_alerts = [
                    {
                        'Timestamp': datetime.now().strftime('%H:%M:%S'),
                        'Entity': entity_to_monitor,
                        'Source': 'Reuters',
                        'Headline': f'{entity_to_monitor} faces regulatory investigation',
                        'Sentiment': -0.7,
                        'Risk Level': 'High'
                    },
                    {
                        'Timestamp': (datetime.now() - timedelta(minutes=15)).strftime('%H:%M:%S'),
                        'Entity': entity_to_monitor,
                        'Source': 'Financial Times',
                        'Headline': f'{entity_to_monitor} reports quarterly losses',
                        'Sentiment': -0.4,
                        'Risk Level': 'Medium'
                    }
                ]
                
                st.subheader("Recent Alerts")
                st.dataframe(recent_alerts, hide_index=True, use_container_width=True)
    
    with tab2:
        st.subheader("Media Search & Analysis")
        
        search_entity = st.text_input("Search Entity")
        date_range = st.date_input("Date Range", value=[datetime.now().date() - timedelta(days=30), datetime.now().date()])
        
        if st.button("Search Media", type="primary") and search_entity:
            with st.spinner("Searching and analyzing media..."):
                # Mock search results
                search_results = [
                    {
                        'Date': '2024-01-15',
                        'Source': 'Bloomberg',
                        'Headline': f'{search_entity} settles compliance case',
                        'Sentiment': -0.2,
                        'Risk Score': 5.5,
                        'Categories': ['Legal', 'Compliance']
                    },
                    {
                        'Date': '2024-01-12',
                        'Source': 'Wall Street Journal',
                        'Headline': f'{search_entity} expands operations',
                        'Sentiment': 0.6,
                        'Risk Score': 2.1,
                        'Categories': ['Business', 'Growth']
                    },
                    {
                        'Date': '2024-01-08',
                        'Source': 'Financial Times',
                        'Headline': f'{search_entity} under investigation',
                        'Sentiment': -0.8,
                        'Risk Score': 8.2,
                        'Categories': ['Legal', 'Investigation', 'Regulatory']
                    }
                ]
                
                st.subheader(f"Media Analysis for {search_entity}")
                st.dataframe(search_results, hide_index=True, use_container_width=True)
                
                # Sentiment analysis
                sentiments = [item['Sentiment'] for item in search_results]
                avg_sentiment = np.mean(sentiments)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Articles Found", len(search_results))
                with col2:
                    st.metric("Average Sentiment", f"{avg_sentiment:.2f}")
                with col3:
                    sentiment_label = "Positive" if avg_sentiment > 0.1 else "Negative" if avg_sentiment < -0.1 else "Neutral"
                    st.metric("Overall Sentiment", sentiment_label)
                
                # Risk timeline
                st.subheader("Risk Timeline")
                timeline_data = pd.DataFrame(search_results)
                timeline_data['Date'] = pd.to_datetime(timeline_data['Date'])
                st.line_chart(timeline_data.set_index('Date')['Risk Score'])
    
    with tab3:
        st.subheader("Alerts & Reports")
        
        # Alert configuration
        st.write("**Alert Configuration**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            alert_entities = st.text_area("Entities to Monitor (one per line)", 
                                        placeholder="Enter entity names...")
            email_notifications = st.checkbox("Email Notifications")
        
        with col2:
            sentiment_threshold = st.slider("Negative Sentiment Threshold", 
                                          min_value=-1.0, max_value=0.0, value=-0.5, step=0.1)
            risk_threshold = st.slider("Risk Score Threshold", 
                                     min_value=1.0, max_value=10.0, value=7.0, step=0.5)
        
        if st.button("Save Alert Configuration", type="primary"):
            st.success("Alert configuration saved successfully!")
        
        # Recent reports
        st.write("**Recent Reports**")
        
        reports = [
            {'Date': '2024-01-15', 'Type': 'Weekly Summary', 'Entities': 15, 'Alerts': 23, 'Status': 'Complete'},
            {'Date': '2024-01-08', 'Type': 'Weekly Summary', 'Entities': 15, 'Alerts': 18, 'Status': 'Complete'},
            {'Date': '2024-01-01', 'Type': 'Monthly Report', 'Entities': 15, 'Alerts': 89, 'Status': 'Complete'}
        ]
        
        st.dataframe(reports, hide_index=True, use_container_width=True)

def show_risk_rules():
    """Risk rules engine interface"""
    st.title("⚖️ Risk Rules Engine")
    
    if not ADVANCED_FEATURES_AVAILABLE:
        st.error("Risk rules features not available")
        return
    
    rules_engine = st.session_state.risk_rules_engine
    
    tab1, tab2, tab3 = st.tabs(["Active Rules", "Create Rule", "Rule Templates"])
    
    with tab1:
        st.subheader("Active Risk Rules")
        
        # Get current rules
        current_rules = rules_engine.list_rules()
        
        if current_rules:
            rule_data = []
            for rule in current_rules:
                rule_data.append({
                    'Rule ID': rule.rule_id[:8],
                    'Name': rule.name,
                    'Category': rule.category.value.replace('_', ' ').title(),
                    'Priority': rule.priority.value.title(),
                    'Active': '✅' if rule.active else '❌',
                    'Conditions': len(rule.conditions),
                    'Actions': len(rule.actions)
                })
            
            st.dataframe(rule_data, hide_index=True, use_container_width=True)
        else:
            st.info("No active rules found")
        
        # Rule management
        st.subheader("Rule Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Add Default Rules", type="primary"):
                try:
                    rules_engine.add_default_rules()
                    st.success("Default rules added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding default rules: {e}")
        
        with col2:
            if st.button("Clear All Rules"):
                if st.button("Confirm Clear All", type="secondary"):
                    rules_engine.rules.clear()
                    st.success("All rules cleared!")
                    st.rerun()
        
        with col3:
            if st.button("Export Rules"):
                st.download_button(
                    label="Download Rules JSON",
                    data=json.dumps([rule.__dict__ for rule in current_rules], indent=2),
                    file_name=f"risk_rules_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
    
    with tab2:
        st.subheader("Create Custom Rule")
        
        # Basic rule information
        col1, col2 = st.columns(2)
        
        with col1:
            rule_name = st.text_input("Rule Name")
            rule_description = st.text_area("Description")
        
        with col2:
            rule_category = st.selectbox("Category", 
                                       ["sanctions", "pep", "adverse_media", "transaction", "kyc", "aml", "custom"])
            rule_priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
        
        # Rule conditions
        st.subheader("Rule Conditions")
        
        condition_type = st.selectbox("Condition Type", 
                                    ["field_value", "threshold", "list_check", "pattern_match", "risk_score"])
        
        if condition_type == "field_value":
            field_name = st.text_input("Field Name", placeholder="e.g., jurisdiction")
            field_value = st.text_input("Expected Value", placeholder="e.g., US")
            operator = st.selectbox("Operator", ["equals", "not_equals", "contains", "not_contains"])
        
        elif condition_type == "threshold":
            field_name = st.text_input("Field Name", placeholder="e.g., transaction_amount")
            threshold_value = st.number_input("Threshold Value", min_value=0.0)
            operator = st.selectbox("Operator", ["greater_than", "less_than", "greater_equal", "less_equal"])
        
        elif condition_type == "list_check":
            field_name = st.text_input("Field Name", placeholder="e.g., entity_name")
            list_name = st.text_input("List Name", placeholder="e.g., sanctions_list")
        
        # Rule actions
        st.subheader("Rule Actions")
        
        action_type = st.selectbox("Action Type", 
                                 ["flag_high_risk", "require_review", "block_transaction", "generate_alert", "escalate_case"])
        
        action_params = {}
        if action_type == "generate_alert":
            action_params['message'] = st.text_input("Alert Message")
            action_params['severity'] = st.selectbox("Alert Severity", ["low", "medium", "high", "critical"])
        
        elif action_type == "escalate_case":
            action_params['escalate_to'] = st.text_input("Escalate To", placeholder="User or department")
            action_params['reason'] = st.text_input("Escalation Reason")
        
        if st.button("Create Rule", type="primary"):
            if rule_name and rule_description:
                try:
                    # Create rule configuration
                    rule_config = {
                        'name': rule_name,
                        'description': rule_description,
                        'category': rule_category,
                        'priority': rule_priority,
                        'conditions': [
                            {
                                'type': condition_type,
                                'field': field_name if 'field_name' in locals() else '',
                                'value': field_value if 'field_value' in locals() else threshold_value if 'threshold_value' in locals() else '',
                                'operator': operator if 'operator' in locals() else '',
                                'list_name': list_name if 'list_name' in locals() else ''
                            }
                        ],
                        'actions': [
                            {
                                'type': action_type,
                                'params': action_params
                            }
                        ]
                    }
                    
                    # Add rule to engine
                    # This would normally use the engine's create_rule method
                    st.success(f"Rule '{rule_name}' created successfully!")
                    st.json(rule_config)
                    
                except Exception as e:
                    st.error(f"Error creating rule: {e}")
            else:
                st.error("Please fill in required fields")
    
    with tab3:
        st.subheader("Rule Templates")
        st.info("📋 Pre-configured rule templates for common compliance scenarios")
        
        templates = {
            "High-Risk Jurisdiction": {
                "description": "Flag entities from high-risk jurisdictions",
                "conditions": "jurisdiction in high_risk_list",
                "actions": "flag_high_risk, require_enhanced_dd"
            },
            "Large Transaction": {
                "description": "Alert on transactions above threshold",
                "conditions": "transaction_amount > 10000",
                "actions": "generate_alert, require_review"
            },
            "Sanctions List Match": {
                "description": "Block entities on sanctions lists",
                "conditions": "entity_name matches sanctions_list",
                "actions": "block_transaction, escalate_case"
            },
            "PEP Exposure": {
                "description": "Enhanced monitoring for PEP-related entities",
                "conditions": "entity_type = pep OR relationship_to_pep = true",
                "actions": "flag_high_risk, require_enhanced_dd, generate_alert"
            },
            "Adverse Media Alert": {
                "description": "Monitor for negative media coverage",
                "conditions": "adverse_media_score > 0.7",
                "actions": "generate_alert, require_review"
            }
        }
        
        for template_name, template_info in templates.items():
            with st.expander(template_name):
                st.write(f"**Description:** {template_info['description']}")
                st.write(f"**Conditions:** {template_info['conditions']}")
                st.write(f"**Actions:** {template_info['actions']}")
                
                if st.button(f"Use {template_name} Template", key=f"template_{template_name}"):
                    st.info(f"Template '{template_name}' loaded. Go to 'Create Rule' tab to customize.")

def show_alerts():
    """Alerts and notifications view"""
    st.title("🚨 Alerts & Notifications")
    st.info("Alert management system will be implemented here")

def show_settings():
    """Settings and configuration view"""
    st.title("⚙️ Settings")
    
    st.subheader("Configuration")
    
    # Display current config (non-sensitive values)
    config_dict = config.to_dict()
    safe_config = {k: v for k, v in config_dict.items() if 'key' not in k.lower() and 'password' not in k.lower()}
    st.json(safe_config)

if __name__ == "__main__":
    main()
