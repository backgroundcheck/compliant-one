"""
Compliant.one Dashboard - Main Application
RegTech Platform for FATF-aligned AML/KYC Compliance Solutions
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore
from datetime import datetime, timedelta
import asyncio
import json

# Configure page
st.set_page_config(
    page_title="Compliant.one - RegTech Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize platform
try:
    from core.platform import CompliantOnePlatform, Customer, initialize_platform
    from config.settings import get_config, FATF_SERVICE_MAPPING
    from dashboard.admin import render_admin_dashboard
    from dashboard.auth_interface import auth_manager, get_current_user, has_permission, render_user_management, render_password_change
    
    if 'platform' not in st.session_state:
        st.session_state.platform = CompliantOnePlatform()
    
    platform = st.session_state.platform
    config = get_config()
    
except ImportError as e:
    st.error(f"Platform initialization failed: {e}")
    st.stop()

def main():
    """Main dashboard application"""
    
    # Check authentication first
    if not auth_manager.verify_session():
        auth_manager.render_auth_page()
        return
    
    # Header
    st.title("🛡️ Compliant.one")
    st.markdown("**Trusted Third-Party Independent Risk & Compliance Solutions Provider**")
    st.markdown("*Helping Financial Institutions, DNFBPs, and Corporates meet FATF-aligned AML/KYC obligations*")
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1f4e79/ffffff?text=Compliant.one", width=200)
        
        # Show user info
        auth_manager.show_user_info()
        
        st.markdown("---")
        
        # Navigation menu with permission-based filtering
        nav_options = ["🏠 Platform Overview"]
        
        # Add options based on user permissions
        if has_permission('compliance_screening'):
            nav_options.extend([
                "🔒 Digital Identity Verification",
                "📊 KYC/CDD/EDD Screening",
                "🕵️‍♂️ OSINT Risk Profiling",
                "🌐 Beneficial Ownership",
                "⚖️ Sanctions & PEP Screening",
                "🔍 Ongoing Monitoring",
                "🔗 Transaction Monitoring"
            ])
        
        # Phase 2 Advanced AI & Compliance Features
        if has_permission('compliance_screening'):
            nav_options.extend([
                "🤖 AI Risk Analytics",
                "📰 Adverse Media Intelligence",
                "⚖️ Smart Rules Engine",
                "📋 Case Management System",
                "📊 Comprehensive Assessment"
            ])
        
        # Scraping Control Panel
        if has_permission('data_source_management'):
            nav_options.extend([
                "🕷️ Scraping Control Panel",
                "🔍 Transparency Dashboard"
            ])
        
        if has_permission('reporting'):
            nav_options.extend([
                "💼 Regulatory Reporting",
                "📋 FATF Compliance Matrix"
            ])
        
        if has_permission('data_source_management'):
            nav_options.append("🔧 Admin Dashboard")
        
        if has_permission('user_management'):
            nav_options.append("👥 User Management")
        
        # Always show settings and password change
        nav_options.extend([
            "🔒 Change Password",
            "⚙️ Platform Settings"
        ])
        
        page = st.selectbox("🧭 Navigate to:", nav_options)
        
        st.markdown("---")
        
        # Quick metrics
        st.metric("🎯 FATF Coverage", "94%", "+2%")
        st.metric("🏛️ Active Clients", "1,247", "+15")
        st.metric("🔍 Daily Screenings", "45,892", "+8%")
        st.metric("⚡ Avg Response Time", "1.2s", "-0.3s")
    
    # Route to appropriate page
    if page == "🏠 Platform Overview":
        show_platform_overview()
    elif page == "🔒 Digital Identity Verification":
        if has_permission('compliance_screening'):
            show_identity_verification()
        else:
            st.error("❌ Access denied. Required permission: compliance_screening")
    elif page == "📊 KYC/CDD/EDD Screening":
        if has_permission('compliance_screening'):
            show_kyc_screening()
        else:
            st.error("❌ Access denied. Required permission: compliance_screening")
    elif page == "🕵️‍♂️ OSINT Risk Profiling":
        if has_permission('compliance_screening'):
            show_osint_profiling()
        else:
            st.error("❌ Access denied. Required permission: compliance_screening")
    elif page == "🌐 Beneficial Ownership":
        if has_permission('compliance_screening'):
            show_beneficial_ownership()
        else:
            st.error("❌ Access denied. Required permission: compliance_screening")
    elif page == "⚖️ Sanctions & PEP Screening":
        if has_permission('compliance_screening'):
            show_sanctions_screening()
        else:
            st.error("❌ Access denied. Required permission: compliance_screening")
    elif page == "🔍 Ongoing Monitoring":
        if has_permission('compliance_screening'):
            show_ongoing_monitoring()
        else:
            st.error("❌ Access denied. Required permission: compliance_screening")
    elif page == "🔗 Transaction Monitoring":
        if has_permission('compliance_screening'):
            show_transaction_monitoring()
        else:
            st.error("❌ Access denied. Required permission: compliance_screening")
    # Phase 2 Advanced AI & Compliance Features
    elif page == "🤖 AI Risk Analytics":
        if has_permission('compliance_screening'):
            show_ai_risk_analytics()
        else:
            st.error("❌ Access denied. Required permission: compliance_screening")
    elif page == "📰 Adverse Media Intelligence":
        if has_permission('compliance_screening'):
            show_adverse_media_intelligence()
        else:
            st.error("❌ Access denied. Required permission: compliance_screening")
    elif page == "⚖️ Smart Rules Engine":
        if has_permission('compliance_screening'):
            show_smart_rules_engine()
        else:
            st.error("❌ Access denied. Required permission: compliance_screening")
    elif page == "📋 Case Management System":
        if has_permission('compliance_screening'):
            show_case_management_system()
        else:
            st.error("❌ Access denied. Required permission: compliance_screening")
    elif page == "📊 Comprehensive Assessment":
        if has_permission('compliance_screening'):
            show_comprehensive_assessment()
        else:
            st.error("❌ Access denied. Required permission: compliance_screening")
    elif page == "🕷️ Scraping Control Panel":
        if has_permission('data_source_management'):
            from dashboard.scraping_panel import render_scraping_control_panel
            render_scraping_control_panel()
        else:
            st.error("❌ Access denied. Required permission: data_source_management")
    elif page == "🔍 Transparency Dashboard":
        if has_permission('data_source_management'):
            show_transparency_dashboard()
        else:
            st.error("❌ Access denied. Required permission: data_source_management")
    elif page == "💼 Regulatory Reporting":
        if has_permission('reporting'):
            show_regulatory_reporting()
        else:
            st.error("❌ Access denied. Required permission: reporting")
    elif page == "📋 FATF Compliance Matrix":
        if has_permission('reporting'):
            show_fatf_compliance()
        else:
            st.error("❌ Access denied. Required permission: reporting")
    elif page == "🔧 Admin Dashboard":
        if has_permission('data_source_management'):
            render_admin_dashboard()
        else:
            st.error("❌ Access denied. Required permission: data_source_management")
    elif page == "👥 User Management":
        if has_permission('user_management'):
            render_user_management()
        else:
            st.error("❌ Access denied. Required permission: user_management")
    elif page == "🔒 Change Password":
        render_password_change()
    elif page == "⚙️ Platform Settings":
        show_platform_settings()

def show_platform_overview():
    """Platform overview dashboard"""
    st.header("🏠 Platform Overview")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🏛️ Institutions Served",
            value="1,247",
            delta="15 new this month"
        )
    
    with col2:
        st.metric(
            label="🌍 Global Coverage",
            value="85 Countries",
            delta="3 new jurisdictions"
        )
    
    with col3:
        st.metric(
            label="🎯 FATF Compliance",
            value="94%",
            delta="2% improvement"
        )
    
    with col4:
        st.metric(
            label="⚡ Processing Speed",
            value="1.2s avg",
            delta="-0.3s faster"
        )
    
    st.markdown("---")
    
    # Service overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔑 Core Services & USP")
        
        services = [
            ("🔒", "Digital Identity Verification", "Multi-factor validation, document authentication, biometric matching"),
            ("📊", "KYC/CDD/EDD Screening", "Risk-based customer categorization with automated workflows"),
            ("🕵️‍♂️", "OSINT Risk Profiling", "AI-powered intelligence gathering and threat assessment"),
            ("🌐", "Beneficial Ownership", "UBO identification and corporate structure mapping"),
            ("⚖️", "Sanctions & PEP Screening", "Real-time screening against global watchlists"),
            ("🔍", "Ongoing Monitoring", "Continuous surveillance and adverse media detection"),
            ("🔗", "Transaction Monitoring", "AI-powered suspicious activity detection"),
            ("💼", "Regulatory Reporting", "Automated compliance reporting and audit trails")
        ]
        
        for icon, service, description in services:
            with st.expander(f"{icon} {service}"):
                st.write(description)
                if st.button(f"Launch {service}", key=f"launch_{service}"):
                    st.success(f"Launching {service}...")
    
    with col2:
        st.subheader("📈 Real-time Analytics")
        
        # Mock real-time data
        screening_data = pd.DataFrame({
            'Time': pd.date_range(start='2024-07-20 00:00', periods=24, freq='H'),
            'Screenings': [45 + i*2 + (i%3)*10 for i in range(24)],
            'Alerts': [2 + (i%5) for i in range(24)]
        })
        
        fig = px.line(screening_data, x='Time', y=['Screenings', 'Alerts'], 
                     title="24-Hour Screening Activity")
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk distribution
        risk_data = pd.DataFrame({
            'Risk Level': ['Low', 'Medium', 'High', 'Critical'],
            'Count': [756, 334, 127, 30]
        })
        
        fig2 = px.pie(risk_data, values='Count', names='Risk Level', 
                     title="Risk Distribution", color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    
    # FATF mapping
    st.subheader("🗺️ FATF Recommendation Mapping")
    
    fatf_col1, fatf_col2 = st.columns(2)
    
    with fatf_col1:
        st.write("**Direct Service Alignment:**")
        direct_mapping = [
            ("R.10", "Customer Due Diligence", "KYC/EDD Profiles"),
            ("R.12", "PEPs", "PEP Screening Engine"), 
            ("R.15", "New Tech Risks", "AI-powered OSINT"),
            ("R.16", "Wire Transfers", "Beneficial Ownership Validation"),
            ("R.22/23", "DNFBP Requirements", "Specialized Due Diligence"),
            ("R.24/25", "Transparency", "Corporate Registry Analysis")
        ]
        
        for rec, name, service in direct_mapping:
            st.write(f"• **{rec}** ({name}) → {service}")
    
    with fatf_col2:
        st.write("**Platform Capabilities:**")
        capabilities = [
            "✅ Real-time sanctions screening",
            "✅ Multi-jurisdiction compliance",
            "✅ AI-powered risk assessment", 
            "✅ Automated reporting workflows",
            "✅ Cross-border entity validation",
            "✅ Continuous monitoring alerts",
            "✅ Audit trail maintenance",
            "✅ Regulatory change tracking"
        ]
        
        for capability in capabilities:
            st.write(capability)

def show_identity_verification():
    """Digital Identity Verification service interface"""
    st.header("🔒 Digital Identity Verification")
    st.markdown("*Multi-factor digital identity validation with document authentication and biometric matching*")
    
    # Service description
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Service Capabilities")
        
        tabs = st.tabs(["📄 Document Verification", "🤳 Biometric Matching", "🌍 Cross-Border Validation", "🔍 Fraud Detection"])
        
        with tabs[0]:
            st.write("**Supported Documents:**")
            st.write("• Passports with MRZ and chip verification")
            st.write("• Driver's licenses with barcode validation")
            st.write("• National IDs with security feature detection")
            st.write("• Utility bills and bank statements")
            
            # Mock verification interface
            uploaded_file = st.file_uploader("Upload Identity Document", type=['jpg', 'png', 'pdf'])
            if uploaded_file:
                st.success("Document uploaded successfully!")
                if st.button("Verify Document"):
                    with st.spinner("Verifying document authenticity..."):
                        import time
                        time.sleep(2)
                    st.success("✅ Document verified - Authenticity score: 94%")
        
        with tabs[1]:
            st.write("**Biometric Capabilities:**")
            st.write("• Live selfie capture with liveness detection")
            st.write("• Face matching against document photos")
            st.write("• Fingerprint verification (optional)")
            st.write("• Voice pattern analysis (premium)")
            
            if st.button("Capture Live Selfie"):
                st.info("📸 Live selfie capture would open camera interface")
        
        with tabs[2]:
            st.write("**Global Coverage:**")
            coverage_data = {
                'Region': ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Africa', 'Middle East'],
                'Countries': [23, 45, 38, 22, 31, 18],
                'Document Types': [12, 18, 16, 10, 8, 12]
            }
            coverage_df = pd.DataFrame(coverage_data)
            st.dataframe(coverage_df)
        
        with tabs[3]:
            st.write("**Fraud Detection Features:**")
            st.write("• Document tampering detection")
            st.write("• Synthetic identity recognition")
            st.write("• Device fingerprinting")
            st.write("• Behavioral pattern analysis")
    
    with col2:
        st.subheader("🧪 Test Verification")
        
        # Mock customer form
        with st.form("identity_verification"):
            customer_name = st.text_input("Customer Name", "John Smith")
            customer_type = st.selectbox("Customer Type", ["Individual", "Corporate"])
            verification_level = st.selectbox("Verification Level", ["Standard", "Enhanced", "Comprehensive"])
            
            submitted = st.form_submit_button("Start Verification")
            
            if submitted:
                with st.spinner("Processing identity verification..."):
                    import time
                    time.sleep(3)
                
                # Mock results
                st.success("✅ Identity Verification Complete")
                
                results = {
                    "Overall Score": "92%",
                    "Document Authenticity": "95%",
                    "Biometric Match": "89%",
                    "Fraud Risk": "Low",
                    "Verification Status": "VERIFIED"
                }
                
                for key, value in results.items():
                    st.metric(key, value)
                
                st.write("**Risk Indicators:**")
                st.write("• ✅ No document tampering detected")
                st.write("• ✅ Liveness verification passed")
                st.write("• ✅ No synthetic identity patterns")

def show_kyc_screening():
    """KYC/CDD/EDD Screening service interface"""
    st.header("📊 KYC/CDD/EDD Screening")
    st.markdown("*Risk-based customer categorization with automated due diligence workflows*")
    
    # Service overview
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("🎯 Due Diligence Levels")
        
        dd_tabs = st.tabs(["📝 SDD", "📋 CDD", "📊 EDD"])
        
        with dd_tabs[0]:
            st.write("**Simplified Due Diligence (SDD)**")
            st.write("*For low-risk customers and relationships*")
            st.write("• Basic identity verification")
            st.write("• Sanctions list screening")
            st.write("• Simplified record keeping")
            st.write("• Reduced monitoring requirements")
        
        with dd_tabs[1]:
            st.write("**Customer Due Diligence (CDD)**")
            st.write("*Standard due diligence for most customers*")
            st.write("• Identity and address verification")
            st.write("• PEP and sanctions screening")
            st.write("• Source of funds verification")
            st.write("• Purpose of relationship assessment")
        
        with dd_tabs[2]:
            st.write("**Enhanced Due Diligence (EDD)**")
            st.write("*For high-risk customers and relationships*")
            st.write("• Comprehensive identity verification")
            st.write("• Source of wealth documentation")
            st.write("• Beneficial ownership analysis")
            st.write("• Enhanced ongoing monitoring")
    
    with col2:
        st.subheader("🧪 KYC Assessment")
        
        with st.form("kyc_assessment"):
            entity_name = st.text_input("Entity Name", "ABC Corporation")
            entity_type = st.selectbox("Entity Type", ["Individual", "Corporate", "DNFBP", "Government"])
            jurisdiction = st.selectbox("Jurisdiction", ["United States", "United Kingdom", "Singapore", "High Risk Country"])
            business_sector = st.selectbox("Business Sector", ["Financial Services", "Technology", "Real Estate", "Gaming"])
            expected_volume = st.number_input("Expected Annual Volume ($)", min_value=0, value=1000000)
            
            assess_button = st.form_submit_button("Perform KYC Assessment")
            
            if assess_button:
                with st.spinner("Analyzing risk profile..."):
                    import time
                    time.sleep(2)
                
                # Mock risk assessment
                st.success("✅ KYC Assessment Complete")
                
                # Determine risk category and DD level
                if jurisdiction == "High Risk Country" or business_sector == "Gaming":
                    risk_category = "HIGH"
                    dd_level = "EDD"
                    risk_score = 8.2
                elif business_sector == "Real Estate":
                    risk_category = "MEDIUM"
                    dd_level = "CDD"
                    risk_score = 5.5
                else:
                    risk_category = "LOW"
                    dd_level = "SDD"
                    risk_score = 2.1
                
                # Display results
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Risk Category", risk_category)
                with col_b:
                    st.metric("DD Level", dd_level)
                with col_c:
                    st.metric("Risk Score", f"{risk_score}/10")
                
                # Risk factors
                st.write("**Risk Factors:**")
                if risk_category == "HIGH":
                    st.write("• 🔴 High-risk jurisdiction")
                    st.write("• 🔴 Cash-intensive business")
                elif risk_category == "MEDIUM":
                    st.write("• 🟡 Medium-risk sector")
                    st.write("• 🟡 Cross-border operations")
                else:
                    st.write("• 🟢 Low-risk profile")
                    st.write("• 🟢 Regulated entity")

def show_osint_profiling():
    """OSINT Risk Profiling service interface"""
    st.header("🕵️‍♂️ OSINT Risk Profiling")
    st.markdown("*AI-powered intelligence gathering with real-time threat assessment*")
    
    # OSINT sources overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📡 Intelligence Sources")
        
        source_tabs = st.tabs(["🌐 Open Web", "📰 News Media", "🏛️ Government", "🕳️ Dark Web"])
        
        with source_tabs[0]:
            st.write("**Social Media & Web Sources:**")
            sources = [
                ("LinkedIn", "Professional networks", "95%"),
                ("Twitter/X", "Social sentiment", "88%"),
                ("Corporate Websites", "Business information", "92%"),
                ("Online Forums", "Community discussions", "75%"),
                ("Academic Sources", "Research publications", "85%")
            ]
            
            for source, desc, reliability in sources:
                st.write(f"• **{source}** - {desc} (Reliability: {reliability})")
        
        with source_tabs[1]:
            st.write("**News & Media Sources:**")
            st.write("• Global news aggregators")
            st.write("• Financial publications")
            st.write("• Regulatory announcements")
            st.write("• Industry publications")
            st.write("• Local news sources")
        
        with source_tabs[2]:
            st.write("**Government & Official Sources:**")
            st.write("• Corporate registries")
            st.write("• Court records")
            st.write("• Regulatory filings")
            st.write("• Sanctions lists")
            st.write("• Enforcement actions")
        
        with source_tabs[3]:
            st.write("**Dark Web Monitoring:**")
            st.info("🔒 Requires special authorization and compliance approval")
            st.write("• Marketplace monitoring")
            st.write("• Credential leak detection")
            st.write("• Threat intelligence")
            st.write("• Criminal forum surveillance")
    
    with col2:
        st.subheader("🔍 OSINT Analysis")
        
        with st.form("osint_search"):
            search_entity = st.text_input("Entity Name", "Sample Corporation")
            entity_type = st.selectbox("Entity Type", ["Individual", "Corporate", "Government"])
            search_depth = st.selectbox("Search Depth", ["Standard", "Deep", "Comprehensive"])
            
            sources = st.multiselect(
                "Sources to Search",
                ["Social Media", "News Media", "Government Records", "Corporate Registries", "Court Records"],
                default=["Social Media", "News Media", "Government Records"]
            )
            
            search_button = st.form_submit_button("Start OSINT Analysis")
            
            if search_button:
                with st.spinner(f"Gathering intelligence from {len(sources)} sources..."):
                    import time
                    time.sleep(4)
                
                st.success("🎯 OSINT Analysis Complete")
                
                # Mock results
                threat_level = "MEDIUM" if "risk" in search_entity.lower() else "LOW"
                confidence = 87
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Threat Level", threat_level)
                with col_b:
                    st.metric("Confidence", f"{confidence}%")
                
                # Findings summary
                st.write("**Key Findings:**")
                if threat_level == "MEDIUM":
                    st.write("• ⚠️ Regulatory investigation mentioned")
                    st.write("• ⚠️ Negative media coverage found")
                    st.write("• ℹ️ Complex corporate structure")
                else:
                    st.write("• ✅ No adverse findings")
                    st.write("• ✅ Positive media coverage")
                    st.write("• ✅ Transparent operations")
                
                # Risk indicators
                with st.expander("📊 Detailed Risk Analysis"):
                    indicators = {
                        "Financial Crime": 0.2 if threat_level == "LOW" else 0.6,
                        "Regulatory Risk": 0.1 if threat_level == "LOW" else 0.5,
                        "Reputational Risk": 0.3 if threat_level == "LOW" else 0.7,
                        "Operational Risk": 0.2 if threat_level == "LOW" else 0.4
                    }
                    
                    for indicator, score in indicators.items():
                        st.progress(score, f"{indicator}: {score:.1%}")

def show_beneficial_ownership():
    """Beneficial Ownership service interface"""
    st.header("🌐 Beneficial Ownership Analysis")
    st.markdown("*UBO identification and corporate structure mapping with transparency scoring*")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🏗️ Ownership Structure Analysis")
        
        # Mock ownership structure visualization
        st.write("**Sample Corporate Structure:**")
        
        # Create a simple hierarchical structure
        ownership_data = {
            'Entity': ['ABC Corp', 'Holdings Ltd', 'Investment Fund', 'John Smith', 'Jane Doe', 'Trust Entity'],
            'Type': ['Target', 'Corporate', 'Fund', 'Individual', 'Individual', 'Trust'],
            'Ownership %': [100, 51, 30, 60, 40, 19],
            'Layer': [0, 1, 1, 2, 2, 1],
            'Jurisdiction': ['Delaware', 'Cayman', 'Luxembourg', 'UK', 'UK', 'Jersey']
        }
        
        ownership_df = pd.DataFrame(ownership_data)
        st.dataframe(ownership_df)
        
        # Ownership visualization
        fig = go.Figure(go.Treemap(
            labels=ownership_df['Entity'],
            parents=[''] + ['ABC Corp'] * (len(ownership_df) - 1),
            values=ownership_df['Ownership %'],
            text=ownership_df['Type'],
            texttemplate="<b>%{label}</b><br>%{text}<br>%{value}%"
        ))
        
        fig.update_layout(title="Ownership Structure Visualization")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🔍 UBO Analysis")
        
        with st.form("ubo_analysis"):
            company_name = st.text_input("Company Name", "ABC Corporation")
            jurisdiction = st.selectbox("Jurisdiction", ["Delaware", "UK", "Singapore", "Cayman Islands"])
            ownership_threshold = st.slider("UBO Threshold (%)", 10, 50, 25)
            
            analyze_button = st.form_submit_button("Analyze Ownership")
            
            if analyze_button:
                with st.spinner("Mapping ownership structure..."):
                    import time
                    time.sleep(3)
                
                st.success("✅ UBO Analysis Complete")
                
                # Mock UBO results
                ubos_found = 2
                layers_identified = 3
                transparency_score = 0.75 if jurisdiction != "Cayman Islands" else 0.45
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("UBOs Found", ubos_found)
                with col_b:
                    st.metric("Layers", layers_identified)
                with col_c:
                    st.metric("Transparency", f"{transparency_score:.0%}")
                
                # UBO details
                st.write("**Identified UBOs:**")
                st.write("1. **John Smith** (60% indirect)")
                st.write("   - UK National")
                st.write("   - No PEP/Sanctions matches")
                st.write("2. **Jane Doe** (40% indirect)")
                st.write("   - UK National") 
                st.write("   - No adverse findings")
                
                # Red flags
                if transparency_score < 0.6:
                    st.warning("⚠️ **Red Flags Detected:**")
                    st.write("• Offshore jurisdiction")
                    st.write("• Complex layered structure")
                else:
                    st.success("✅ **No Red Flags**")
                    st.write("• Transparent structure")
                    st.write("• All UBOs identified")

def show_sanctions_screening():
    """Sanctions & PEP Screening interface"""
    st.header("⚖️ Sanctions & PEP Screening")
    st.markdown("*Real-time screening against global watchlists and PEP databases*")
    
    # Screening interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Screening Sources")
        
        screening_tabs = st.tabs(["🚫 Sanctions Lists", "🏛️ PEP Databases", "⚡ Real-time Updates"])
        
        with screening_tabs[0]:
            sanctions_sources = [
                ("OFAC SDN List", "US Treasury", "8,456 entries", "🟢 Online"),
                ("EU Consolidated List", "European Union", "1,247 entries", "🟢 Online"), 
                ("UN Security Council", "United Nations", "856 entries", "🟢 Online"),
                ("UK HMT List", "UK Treasury", "634 entries", "🟢 Online"),
                ("AUSTRAC List", "Australia", "423 entries", "🟢 Online")
            ]
            
            for name, authority, entries, status in sanctions_sources:
                col_a, col_b, col_c, col_d = st.columns([2, 2, 1, 1])
                with col_a:
                    st.write(f"**{name}**")
                with col_b:
                    st.write(authority)
                with col_c:
                    st.write(entries)
                with col_d:
                    st.write(status)
        
        with screening_tabs[1]:
            st.write("**PEP Categories Covered:**")
            pep_categories = [
                "• Heads of State and Government",
                "• Senior Politicians and Ministers", 
                "• Supreme Court Judges",
                "• Senior Military Officers",
                "• Board Members of State Enterprises",
                "• Immediate Family Members",
                "• Close Associates"
            ]
            
            for category in pep_categories:
                st.write(category)
        
        with screening_tabs[2]:
            st.write("**Update Frequency:**")
            st.write("• **OFAC SDN:** Real-time updates")
            st.write("• **EU Lists:** Daily updates")
            st.write("• **UN Lists:** Weekly updates")
            st.write("• **PEP Databases:** Monthly updates")
    
    with col2:
        st.subheader("🔍 Quick Screening")
        
        with st.form("screening_form"):
            search_name = st.text_input("Name to Screen", "John Smith")
            search_type = st.selectbox("Search Type", ["Individual", "Entity", "Vessel", "Address"])
            screening_lists = st.multiselect(
                "Lists to Check",
                ["Sanctions", "PEP", "Watchlists", "Adverse Media"],
                default=["Sanctions", "PEP"]
            )
            
            screen_button = st.form_submit_button("Screen Now")
            
            if screen_button:
                with st.spinner("Screening against selected lists..."):
                    import time
                    time.sleep(2)
                
                # Mock screening results
                has_matches = "sanctions" in search_name.lower() or "politician" in search_name.lower()
                
                if has_matches:
                    st.warning("⚠️ **Potential Matches Found**")
                    
                    match_data = {
                        'List': ['OFAC SDN', 'EU Consolidated'],
                        'Match %': ['85%', '92%'],
                        'Type': ['Similar Name', 'Exact Match'],
                        'Details': ['Review Required', 'High Risk']
                    }
                    
                    match_df = pd.DataFrame(match_data)
                    st.dataframe(match_df)
                    
                    st.write("**Recommended Actions:**")
                    st.write("• Conduct enhanced due diligence")
                    st.write("• Obtain legal approval")
                    st.write("• Document risk assessment")
                
                else:
                    st.success("✅ **No Matches Found**")
                    st.write("• Clean screening result")
                    st.write("• No sanctions matches")
                    st.write("• No PEP matches")
                    st.write("• Proceed with onboarding")

def show_ongoing_monitoring():
    """Ongoing Monitoring interface"""
    st.header("🔍 Ongoing Monitoring & Alerts")
    st.markdown("*Continuous surveillance with adverse media detection and real-time alerts*")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("🚨 Recent Alerts")
        
        # Mock alerts data
        alerts_data = {
            'Timestamp': [
                '2024-07-20 14:30',
                '2024-07-20 12:15', 
                '2024-07-20 09:45',
                '2024-07-19 16:20',
                '2024-07-19 11:30'
            ],
            'Entity': [
                'Risk Corporation Ltd',
                'John Politician',
                'Suspicious Holdings Inc',
                'Global Trade Partners',
                'Investment Fund ABC'
            ],
            'Alert Type': [
                'Adverse Media',
                'PEP Status Change',
                'Sanctions Update',
                'Corporate Structure Change',
                'High-Value Transaction'
            ],
            'Severity': ['High', 'Medium', 'Critical', 'Low', 'Medium'],
            'Status': ['Open', 'Investigating', 'Escalated', 'Closed', 'Reviewing']
        }
        
        alerts_df = pd.DataFrame(alerts_data)
        
        # Color code severity
        def color_severity(val):
            if val == 'Critical':
                return 'background-color: #ff6b6b'
            elif val == 'High':
                return 'background-color: #ffa726'
            elif val == 'Medium':
                return 'background-color: #ffee58'
            else:
                return 'background-color: #a5d6a7'
        
        styled_df = alerts_df.style.applymap(color_severity, subset=['Severity'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Alert details
        selected_alert = st.selectbox("Select Alert for Details", alerts_df['Entity'].tolist())
        
        if selected_alert:
            alert_info = alerts_df[alerts_df['Entity'] == selected_alert].iloc[0]
            
            st.write(f"**Alert Details for {selected_alert}:**")
            st.write(f"• **Type:** {alert_info['Alert Type']}")
            st.write(f"• **Severity:** {alert_info['Severity']}")
            st.write(f"• **Status:** {alert_info['Status']}")
            st.write(f"• **Time:** {alert_info['Timestamp']}")
            
            if alert_info['Alert Type'] == 'Adverse Media':
                st.write("• **Source:** Financial Times")
                st.write("• **Headline:** 'Regulatory investigation launched into compliance practices'")
                st.write("• **Sentiment:** Negative")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("Mark Reviewed"):
                    st.success("Alert marked as reviewed")
            with col_b:
                if st.button("Escalate"):
                    st.warning("Alert escalated to compliance team")
            with col_c:
                if st.button("Close Alert"):
                    st.info("Alert closed")
    
    with col2:
        st.subheader("📊 Monitoring Stats")
        
        # Monitoring metrics
        st.metric("Active Monitors", "1,247")
        st.metric("Alerts Today", "23", "+5")
        st.metric("Critical Alerts", "3", "+1")
        st.metric("Response Time", "12 min", "-3 min")
        
        st.markdown("---")
        
        st.subheader("⚙️ Monitoring Controls")
        
        with st.form("monitoring_settings"):
            st.write("**Alert Thresholds:**")
            adverse_media = st.slider("Adverse Media Sensitivity", 1, 10, 7)
            sanctions_changes = st.checkbox("Sanctions List Updates", True)
            pep_changes = st.checkbox("PEP Status Changes", True)
            structure_changes = st.checkbox("Corporate Structure Changes", True)
            
            update_button = st.form_submit_button("Update Settings")
            
            if update_button:
                st.success("Monitoring settings updated!")

def show_transaction_monitoring():
    """Transaction Monitoring interface"""
    st.header("🔗 Transaction Monitoring Integration")
    st.markdown("*AI-powered suspicious activity detection with regulatory threshold monitoring*")
    
    st.info("🔧 **Integration Ready** - Connect your transaction monitoring system via API")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Transaction Analytics")
        
        # Mock transaction data
        tx_data = pd.DataFrame({
            'Date': pd.date_range(start='2024-07-01', periods=30, freq='D'),
            'Volume': [50000 + i*1000 + (i%7)*5000 for i in range(30)],
            'Count': [150 + i*2 + (i%5)*10 for i in range(30)],
            'Alerts': [(i%10) for i in range(30)]
        })
        
        # Volume chart
        fig1 = px.line(tx_data, x='Date', y='Volume', title='Daily Transaction Volume')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Alerts distribution
        fig2 = px.bar(tx_data.tail(7), x='Date', y='Alerts', title='Daily Alerts (Last 7 Days)')
        st.plotly_chart(fig2, use_container_width=True)
        
        st.subheader("🚨 Suspicious Activity Patterns")
        
        patterns = [
            ("Structuring", "Multiple transactions just below reporting threshold", "High"),
            ("Rapid Movement", "Funds moved quickly between accounts", "Medium"),
            ("Unusual Geography", "Transactions from high-risk jurisdictions", "High"),
            ("Round Dollar Amounts", "Frequent round-number transactions", "Low"),
            ("Velocity Anomaly", "Transaction frequency spike detected", "Medium")
        ]
        
        for pattern, description, risk in patterns:
            with st.expander(f"🔍 {pattern} - {risk} Risk"):
                st.write(f"**Pattern:** {description}")
                st.write(f"**Risk Level:** {risk}")
                if risk == "High":
                    st.write("**Action:** Immediate investigation required")
                elif risk == "Medium":
                    st.write("**Action:** Enhanced monitoring")
                else:
                    st.write("**Action:** Routine review")
    
    with col2:
        st.subheader("⚙️ Integration Setup")
        
        with st.form("tm_integration"):
            st.write("**API Configuration:**")
            api_endpoint = st.text_input("Transaction System API", "https://api.yoursystem.com")
            api_key = st.text_input("API Key", type="password")
            batch_size = st.number_input("Batch Size", min_value=100, max_value=10000, value=1000)
            
            st.write("**Monitoring Rules:**")
            threshold_amount = st.number_input("Threshold Amount ($)", min_value=1000, value=10000)
            velocity_limit = st.number_input("Daily Transaction Limit", min_value=1, value=100)
            
            setup_button = st.form_submit_button("Setup Integration")
            
            if setup_button:
                st.success("✅ Transaction monitoring integration configured!")
                st.info("Next steps: Test connection and deploy monitoring rules")
        
        st.markdown("---")
        
        st.subheader("📊 Real-time Stats")
        st.metric("Transactions Today", "2,847")
        st.metric("Alerts Generated", "12")
        st.metric("False Positive Rate", "15%")
        st.metric("Investigation Queue", "8")

def show_regulatory_reporting():
    """Regulatory Reporting interface"""
    st.header("💼 Regulatory Reporting Support")
    st.markdown("*Automated compliance reporting with audit trail management*")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Available Reports")
        
        reports_tabs = st.tabs(["🏛️ Regulatory", "📊 Management", "🔍 Audit"])
        
        with reports_tabs[0]:
            regulatory_reports = [
                ("SAR/STR Filing", "Suspicious Activity Reports", "Weekly", "Automated"),
                ("CTR Filing", "Currency Transaction Reports", "Daily", "Automated"),
                ("FBAR Report", "Foreign Bank Account Report", "Annual", "Manual"),
                ("BSA Compliance", "Bank Secrecy Act Reporting", "Quarterly", "Automated"),
                ("FATCA Reporting", "Foreign Account Tax Compliance", "Annual", "Semi-automated")
            ]
            
            for report, description, frequency, method in regulatory_reports:
                with st.expander(f"📄 {report}"):
                    st.write(f"**Description:** {description}")
                    st.write(f"**Frequency:** {frequency}")
                    st.write(f"**Method:** {method}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"Generate {report}", key=f"gen_{report}"):
                            st.success(f"Generating {report}...")
                    with col_b:
                        if st.button(f"Schedule {report}", key=f"sched_{report}"):
                            st.info(f"Scheduled {report} generation")
        
        with reports_tabs[1]:
            st.write("**Management Reporting:**")
            mgmt_reports = [
                "• Executive Risk Dashboard",
                "• Compliance Metrics Summary", 
                "• Customer Risk Distribution",
                "• Alert Resolution Statistics",
                "• Regulatory Change Impact Assessment"
            ]
            
            for report in mgmt_reports:
                st.write(report)
        
        with reports_tabs[2]:
            st.write("**Audit Trail Reports:**")
            audit_reports = [
                "• User Activity Logs",
                "• System Access Reports",
                "• Data Modification History",
                "• Compliance Decision Audit",
                "• Exception Handling Report"
            ]
            
            for report in audit_reports:
                st.write(report)
    
    with col2:
        st.subheader("🎯 Quick Report Generator")
        
        with st.form("quick_report"):
            report_type = st.selectbox(
                "Report Type",
                ["Customer Risk Summary", "Alert Statistics", "Screening Results", "Compliance Metrics"]
            )
            
            date_range = st.date_input(
                "Report Period",
                value=[datetime.now() - timedelta(days=30), datetime.now()]
            )
            
            format_type = st.selectbox("Output Format", ["PDF", "Excel", "CSV", "JSON"])
            
            include_charts = st.checkbox("Include Charts", True)
            include_details = st.checkbox("Include Details", True)
            
            generate_button = st.form_submit_button("Generate Report")
            
            if generate_button:
                with st.spinner("Generating report..."):
                    import time
                    time.sleep(2)
                
                st.success(f"✅ {report_type} generated successfully!")
                
                # Mock download link
                st.download_button(
                    label="📥 Download Report",
                    data="Mock report data...",
                    file_name=f"{report_type.replace(' ', '_').lower()}.{format_type.lower()}",
                    mime="application/octet-stream"
                )
        
        st.markdown("---")
        
        st.subheader("📈 Reporting Metrics")
        st.metric("Reports Generated", "1,456")
        st.metric("Avg Generation Time", "45s")
        st.metric("Success Rate", "99.2%")
        st.metric("Scheduled Reports", "127")

def show_fatf_compliance():
    """FATF Compliance Matrix"""
    st.header("📋 FATF Compliance Matrix")
    st.markdown("*Comprehensive mapping of platform services to FATF 40 Recommendations*")
    
    # Coverage overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Recommendations", "40")
    with col2:
        st.metric("Covered by Platform", "37", "+2")
    with col3:
        st.metric("Coverage Percentage", "92.5%", "+5%")
    
    st.markdown("---")
    
    # FATF mapping table
    st.subheader("🗺️ Detailed FATF Mapping")
    
    # Create comprehensive FATF mapping
    fatf_mapping = []
    for rec, info in FATF_SERVICE_MAPPING.items():
        fatf_mapping.append({
            'Recommendation': rec,
            'Name': info['name'],
            'Service': info['service'].replace('_', ' ').title(),
            'Description': info['description'],
            'Status': '✅ Covered',
            'Implementation': 'Automated'
        })
    
    # Add some uncovered recommendations
    uncovered = [
        {'Recommendation': 'R.26', 'Name': 'Regulation of FIs', 'Service': 'N/A', 
         'Description': 'Financial institution regulation', 'Status': '⚠️ Partial', 'Implementation': 'Manual'},
        {'Recommendation': 'R.35', 'Name': 'Sanctions', 'Service': 'N/A',
         'Description': 'Sanctions implementation', 'Status': '🔄 Planned', 'Implementation': 'Future'},
        {'Recommendation': 'R.40', 'Name': 'International Cooperation', 'Service': 'N/A',
         'Description': 'Information exchange', 'Status': '🔄 Planned', 'Implementation': 'Future'}
    ]
    
    fatf_mapping.extend(uncovered)
    
    fatf_df = pd.DataFrame(fatf_mapping)
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=['✅ Covered', '⚠️ Partial', '🔄 Planned'],
            default=['✅ Covered', '⚠️ Partial', '🔄 Planned']
        )
    
    with col2:
        service_filter = st.multiselect(
            "Filter by Service",
            options=fatf_df['Service'].unique(),
            default=fatf_df['Service'].unique()
        )
    
    # Apply filters
    filtered_df = fatf_df[
        (fatf_df['Status'].isin(status_filter)) &
        (fatf_df['Service'].isin(service_filter))
    ]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Service coverage chart
    st.subheader("📊 Service Coverage Analysis")
    
    service_coverage = fatf_df[fatf_df['Status'] == '✅ Covered']['Service'].value_counts()
    
    fig = px.bar(
        x=service_coverage.index,
        y=service_coverage.values,
        title="FATF Recommendations Covered by Service"
    )
    fig.update_xaxis(title="Service")
    fig.update_yaxis(title="Number of Recommendations")
    st.plotly_chart(fig, use_container_width=True)

def show_platform_settings():
    """Platform Settings"""
    st.header("⚙️ Platform Settings")
    st.markdown("*Configure platform parameters and service integrations*")
    
    settings_tabs = st.tabs(["🔧 General", "🔌 Integrations", "🛡️ Security", "📊 Monitoring"])
    
    with settings_tabs[0]:
        st.subheader("General Platform Settings")
        
        with st.form("general_settings"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Risk Thresholds:**")
                low_risk_threshold = st.slider("Low Risk Threshold", 0.0, 1.0, 0.3, 0.1)
                medium_risk_threshold = st.slider("Medium Risk Threshold", 0.0, 1.0, 0.6, 0.1)
                high_risk_threshold = st.slider("High Risk Threshold", 0.0, 1.0, 0.8, 0.1)
                
                st.write("**Processing Settings:**")
                batch_size = st.number_input("Default Batch Size", 100, 10000, 1000)
                timeout_seconds = st.number_input("Request Timeout (s)", 10, 300, 60)
            
            with col2:
                st.write("**Compliance Settings:**")
                ubo_threshold = st.slider("UBO Ownership Threshold (%)", 10, 50, 25)
                pep_monitoring = st.checkbox("PEP Monitoring Enabled", True)
                adverse_media = st.checkbox("Adverse Media Monitoring", True)
                
                st.write("**Retention Settings:**")
                data_retention_days = st.number_input("Data Retention (days)", 30, 2555, 365)
                log_retention_days = st.number_input("Log Retention (days)", 30, 2555, 90)
            
            if st.form_submit_button("Save General Settings"):
                st.success("✅ General settings saved successfully!")
    
    with settings_tabs[1]:
        st.subheader("Third-Party Integrations")
        
        integrations = [
            ("World-Check", "Thomson Reuters", "Connected", "🟢"),
            ("Dow Jones", "Risk Center", "Connected", "🟢"), 
            ("LexisNexis", "WorldCompliance", "Disconnected", "🔴"),
            ("Refinitiv", "World-Check One", "Connected", "🟢"),
            ("ACUANT", "Identity Verification", "Connected", "🟢"),
            ("Jumio", "KYX Platform", "Testing", "🟡")
        ]
        
        for name, provider, status, indicator in integrations:
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                st.write(f"**{name}**")
            with col2:
                st.write(provider)
            with col3:
                st.write(f"{indicator} {status}")
            with col4:
                if st.button("Configure", key=f"config_{name}"):
                    st.info(f"Opening {name} configuration...")
    
    with settings_tabs[2]:
        st.subheader("Security Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Authentication Settings:**")
            mfa_enabled = st.checkbox("Multi-Factor Authentication", True)
            session_timeout = st.number_input("Session Timeout (minutes)", 15, 480, 120)
            password_policy = st.selectbox("Password Policy", ["Standard", "Strong", "Enterprise"])
            
            st.write("**Access Control:**")
            role_based_access = st.checkbox("Role-Based Access Control", True)
            audit_logging = st.checkbox("Comprehensive Audit Logging", True)
        
        with col2:
            st.write("**Data Protection:**")
            encryption_at_rest = st.checkbox("Encryption at Rest", True)
            encryption_in_transit = st.checkbox("Encryption in Transit", True)
            data_masking = st.checkbox("Sensitive Data Masking", True)
            
            st.write("**Compliance:**")
            gdpr_compliance = st.checkbox("GDPR Compliance Mode", True)
            data_localization = st.selectbox("Data Localization", ["Global", "EU Only", "US Only"])
    
    with settings_tabs[3]:
        st.subheader("Monitoring & Alerting")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**System Monitoring:**")
            health_check_interval = st.number_input("Health Check Interval (minutes)", 1, 60, 5)
            alert_threshold = st.slider("Alert Threshold (% uptime)", 90.0, 100.0, 99.5)
            
            st.write("**Performance Monitoring:**")
            response_time_threshold = st.number_input("Response Time Alert (ms)", 100, 5000, 1000)
            throughput_monitoring = st.checkbox("Throughput Monitoring", True)
        
        with col2:
            st.write("**Alert Destinations:**")
            email_alerts = st.text_input("Alert Email", "admin@compliant.one")
            slack_webhook = st.text_input("Slack Webhook URL")
            sms_alerts = st.checkbox("SMS Alerts", False)
            
            st.write("**Notification Frequency:**")
            immediate_alerts = st.checkbox("Immediate Critical Alerts", True)
            daily_summary = st.checkbox("Daily Summary Report", True)
            weekly_report = st.checkbox("Weekly Performance Report", True)

# Phase 2 Advanced AI & Compliance Dashboard Functions

def show_ai_risk_analytics():
    """AI Risk Analytics dashboard"""
    st.header("🤖 AI Risk Analytics")
    st.subheader("Advanced AI-powered risk assessment and anomaly detection")
    
    # Create tabs for different AI analytics
    ai_tabs = st.tabs(["🔍 Customer Analysis", "⚠️ Anomaly Detection", "📈 Predictive Analytics", "🕸️ Network Analysis"])
    
    with ai_tabs[0]:  # Customer Analysis
        st.subheader("Customer Risk Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
            customer_type = st.selectbox("Customer Type", ["Individual", "Corporate"])
            jurisdiction = st.selectbox("Jurisdiction", ["US", "UK", "SG", "AE", "RU", "CN", "Other"])
        
        with col2:
            analysis_type = st.selectbox("Analysis Type", 
                ["Comprehensive", "Anomaly Detection", "Predictive Risk", "Network Analysis"])
            risk_threshold = st.slider("Risk Threshold", 0.0, 1.0, 0.7)
        
        if st.button("🔍 Run AI Analysis"):
            if customer_name:
                with st.spinner("Running AI analysis..."):
                    # Create customer for analysis
                    customer = Customer(
                        customer_id=f"AI_{hash(customer_name) % 10000}",
                        name=customer_name,
                        customer_type=customer_type.upper(),
                        jurisdiction=jurisdiction,
                        risk_category="MEDIUM"
                    )
                    
                    # Run analysis
                    try:
                        analysis_result = asyncio.run(platform.ai_risk_analysis(customer, analysis_type.lower().replace(' ', '_')))
                        
                        if 'error' not in analysis_result:
                            st.success("✅ AI Analysis Completed")
                            
                            # Display results
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                risk_score = analysis_result.get('overall_risk_score', 0)
                                st.metric("Overall Risk Score", f"{risk_score:.3f}", 
                                         delta=f"{'High' if risk_score > 0.7 else 'Medium' if risk_score > 0.4 else 'Low'}")
                            
                            with col2:
                                analysis_type_result = analysis_result.get('analysis_type', 'Unknown')
                                st.metric("Analysis Type", analysis_type_result)
                            
                            with col3:
                                confidence = analysis_result.get('confidence_score', 0.85)
                                st.metric("Confidence", f"{confidence:.2%}")
                            
                            # Show recommendations
                            recommendations = analysis_result.get('recommendations', [])
                            if recommendations:
                                st.subheader("🎯 AI Recommendations")
                                for i, rec in enumerate(recommendations[:5], 1):
                                    st.write(f"{i}. {rec}")
                        else:
                            st.error(f"❌ Analysis failed: {analysis_result['error']}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("Please enter a customer name")
    
    with ai_tabs[1]:  # Anomaly Detection
        st.subheader("Anomaly Detection")
        
        # Sample anomaly data for visualization
        if st.button("🔍 Detect Anomalies"):
            with st.spinner("Scanning for anomalies..."):
                # Simulate anomaly detection results
                anomalies_data = {
                    'Entity': ['Customer A', 'Customer B', 'Customer C', 'Customer D'],
                    'Anomaly Score': [0.95, 0.87, 0.82, 0.76],
                    'Type': ['Transaction Pattern', 'KYC Data Mismatch', 'Behavioral Change', 'Network Connection'],
                    'Risk Level': ['Critical', 'High', 'High', 'Medium']
                }
                
                df = pd.DataFrame(anomalies_data)
                st.dataframe(df, use_container_width=True)
                
                # Visualization
                fig = px.bar(df, x='Entity', y='Anomaly Score', color='Risk Level',
                           title="Detected Anomalies by Risk Level")
                st.plotly_chart(fig, use_container_width=True)
    
    with ai_tabs[2]:  # Predictive Analytics
        st.subheader("Predictive Risk Analytics")
        
        col1, col2 = st.columns(2)
        with col1:
            prediction_timeframe = st.selectbox("Prediction Timeframe", ["30 days", "90 days", "6 months", "1 year"])
            risk_factors = st.multiselect("Risk Factors", 
                ["Transaction Volume", "Geographic Exposure", "Industry Risk", "PEP Status"])
        
        with col2:
            model_type = st.selectbox("Model Type", ["Random Forest", "Neural Network", "Ensemble"])
            confidence_threshold = st.slider("Confidence Threshold", 0.5, 0.95, 0.8)
        
        if st.button("📈 Generate Predictions"):
            with st.spinner("Generating predictions..."):
                # Sample prediction data
                prediction_data = {
                    'Customer': [f'Customer {i}' for i in range(1, 11)],
                    'Current Risk': [0.3, 0.6, 0.2, 0.8, 0.4, 0.7, 0.1, 0.9, 0.5, 0.3],
                    'Predicted Risk': [0.4, 0.8, 0.3, 0.9, 0.6, 0.8, 0.2, 0.95, 0.7, 0.4],
                    'Risk Change': ['+33%', '+33%', '+50%', '+13%', '+50%', '+14%', '+100%', '+6%', '+40%', '+33%']
                }
                
                df = pd.DataFrame(prediction_data)
                st.dataframe(df, use_container_width=True)
                
                # Trend visualization
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df['Customer'], y=df['Current Risk'], 
                                       mode='lines+markers', name='Current Risk'))
                fig.add_trace(go.Scatter(x=df['Customer'], y=df['Predicted Risk'], 
                                       mode='lines+markers', name='Predicted Risk'))
                fig.update_layout(title="Risk Prediction Trends")
                st.plotly_chart(fig, use_container_width=True)
    
    with ai_tabs[3]:  # Network Analysis
        st.subheader("Network Relationship Analysis")
        
        entity_name = st.text_input("Entity for Network Analysis", placeholder="Enter entity name")
        analysis_depth = st.selectbox("Analysis Depth", ["1 degree", "2 degrees", "3 degrees"])
        
        if st.button("🕸️ Analyze Network"):
            if entity_name:
                with st.spinner("Analyzing network relationships..."):
                    st.info("🔍 Network analysis in progress...")
                    
                    # Sample network data
                    st.subheader("Connected Entities")
                    network_data = {
                        'Connected Entity': ['Entity A', 'Entity B', 'Entity C', 'Entity D'],
                        'Relationship': ['Director', 'Shareholder', 'Business Partner', 'Family Member'],
                        'Risk Score': [0.8, 0.6, 0.7, 0.4],
                        'Connection Strength': ['Strong', 'Medium', 'Strong', 'Weak']
                    }
                    
                    df = pd.DataFrame(network_data)
                    st.dataframe(df, use_container_width=True)

def show_adverse_media_intelligence():
    """Adverse Media Intelligence dashboard"""
    st.header("📰 Adverse Media Intelligence")
    st.subheader("Real-time adverse media monitoring and analysis")
    
    media_tabs = st.tabs(["🔍 Entity Monitoring", "📊 Media Analysis", "🚨 Alert Management", "📈 Trends"])
    
    with media_tabs[0]:  # Entity Monitoring
        st.subheader("Entity Media Monitoring")
        
        col1, col2 = st.columns(2)
        with col1:
            entity_name = st.text_input("Entity Name", placeholder="Enter entity name to monitor")
            entity_type = st.selectbox("Entity Type", ["Individual", "Corporate", "Government"])
            search_depth = st.selectbox("Search Depth", ["Standard", "Deep", "Comprehensive"])
        
        with col2:
            timeframe = st.selectbox("Timeframe", ["24 hours", "7 days", "30 days", "90 days"])
            sentiment_threshold = st.slider("Adverse Sentiment Threshold", -1.0, 0.0, -0.3)
            max_results = st.number_input("Max Results", 10, 1000, 100)
        
        if st.button("🔍 Start Monitoring"):
            if entity_name:
                with st.spinner("Scanning media sources..."):
                    try:
                        options = {
                            'max_results': max_results,
                            'timeframe': timeframe.replace(' ', '_'),
                            'sentiment_threshold': sentiment_threshold
                        }
                        
                        result = asyncio.run(platform.adverse_media_monitoring(entity_name, options))
                        
                        if 'error' not in result:
                            st.success("✅ Media scan completed")
                            
                            # Overall assessment
                            overall = result.get('overall_assessment', {})
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                risk_level = overall.get('overall_risk_level', 'UNKNOWN')
                                st.metric("Risk Level", risk_level)
                            
                            with col2:
                                risk_score = overall.get('overall_risk_score', 0)
                                st.metric("Risk Score", f"{risk_score:.3f}")
                            
                            with col3:
                                sentiment = overall.get('overall_sentiment', 0)
                                st.metric("Sentiment", f"{sentiment:.3f}")
                            
                            with col4:
                                confidence = overall.get('confidence_score', 0.8)
                                st.metric("Confidence", f"{confidence:.2%}")
                            
                            # News results
                            news_results = result.get('news_media_results', {})
                            st.subheader("📰 News Media Results")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Total Articles", news_results.get('total_articles', 0))
                            with col2:
                                st.metric("Adverse Articles", news_results.get('adverse_articles', 0))
                            
                            # Social media results
                            social_results = result.get('social_media_results', {})
                            st.subheader("📱 Social Media Results")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Total Mentions", social_results.get('total_mentions', 0))
                            with col2:
                                st.metric("Adverse Mentions", social_results.get('adverse_mentions', 0))
                        else:
                            st.error(f"❌ Monitoring failed: {result['error']}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("Please enter an entity name")
    
    with media_tabs[1]:  # Media Analysis
        st.subheader("Media Analysis Dashboard")
        
        # Sample media analysis data
        if st.button("📊 Generate Analysis"):
            with st.spinner("Analyzing media data..."):
                # Sample data for visualization
                sources_data = {
                    'Source': ['Reuters', 'Bloomberg', 'BBC', 'Twitter', 'LinkedIn'],
                    'Articles': [25, 18, 12, 89, 34],
                    'Adverse': [5, 3, 2, 23, 7],
                    'Sentiment': [-0.2, -0.1, -0.3, -0.4, -0.2]
                }
                
                df = pd.DataFrame(sources_data)
                st.dataframe(df, use_container_width=True)
                
                # Visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    fig1 = px.bar(df, x='Source', y='Articles', title="Articles by Source")
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    fig2 = px.scatter(df, x='Articles', y='Sentiment', size='Adverse', 
                                    hover_name='Source', title="Sentiment vs Volume")
                    st.plotly_chart(fig2, use_container_width=True)
    
    with media_tabs[2]:  # Alert Management
        st.subheader("Alert Management")
        
        # Alert configuration
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Alert Thresholds:**")
            risk_threshold = st.slider("Risk Score Threshold", 0.0, 1.0, 0.6)
            sentiment_threshold = st.slider("Sentiment Threshold", -1.0, 0.0, -0.4)
            volume_threshold = st.number_input("Volume Threshold", 1, 100, 10)
        
        with col2:
            st.write("**Alert Destinations:**")
            email_alerts = st.text_input("Alert Email", "compliance@company.com")
            slack_webhook = st.checkbox("Slack Notifications")
            sms_alerts = st.checkbox("SMS Alerts")
        
        # Recent alerts
        st.subheader("🚨 Recent Alerts")
        alerts_data = {
            'Timestamp': ['2024-07-22 10:30', '2024-07-22 09:15', '2024-07-22 08:45'],
            'Entity': ['Company A', 'Person B', 'Entity C'],
            'Alert Type': ['High Risk Score', 'Negative Sentiment', 'Volume Spike'],
            'Severity': ['High', 'Medium', 'High'],
            'Status': ['Active', 'Reviewed', 'Active']
        }
        
        alerts_df = pd.DataFrame(alerts_data)
        st.dataframe(alerts_df, use_container_width=True)
    
    with media_tabs[3]:  # Trends
        st.subheader("Media Trends Analysis")
        
        # Trend visualization
        dates = pd.date_range('2024-07-01', periods=22, freq='D')
        trend_data = {
            'Date': dates,
            'Total Articles': [50 + i*2 + (i%3)*10 for i in range(22)],
            'Adverse Articles': [8 + i//3 + (i%5)*2 for i in range(22)],
            'Average Sentiment': [-0.1 - (i%7)*0.05 for i in range(22)]
        }
        
        trend_df = pd.DataFrame(trend_data)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['Total Articles'], 
                               mode='lines+markers', name='Total Articles'))
        fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['Adverse Articles'], 
                               mode='lines+markers', name='Adverse Articles'))
        fig.update_layout(title="Media Coverage Trends")
        st.plotly_chart(fig, use_container_width=True)

def show_smart_rules_engine():
    """Smart Rules Engine dashboard"""
    st.header("⚖️ Smart Rules Engine")
    st.subheader("Customizable compliance rules and automated decision making")
    
    rules_tabs = st.tabs(["📝 Rule Configuration", "📊 Rule Performance", "🔧 Rule Management", "📈 Analytics"])
    
    with rules_tabs[0]:  # Rule Configuration
        st.subheader("Create New Rule")
        
        col1, col2 = st.columns(2)
        with col1:
            rule_name = st.text_input("Rule Name", placeholder="Enter rule name")
            rule_description = st.text_area("Description", placeholder="Describe the rule purpose")
            risk_level = st.selectbox("Risk Level", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        
        with col2:
            rule_category = st.selectbox("Rule Category", 
                ["Transaction Monitoring", "Customer Screening", "Sanctions Check", "PEP Screening", "KYC/CDD"])
            confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.7)
            rule_enabled = st.checkbox("Enable Rule", value=True)
        
        # Rule conditions
        st.subheader("Rule Conditions")
        num_conditions = st.number_input("Number of Conditions", 1, 10, 1)
        
        conditions = []
        for i in range(num_conditions):
            st.write(f"**Condition {i+1}:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                field = st.selectbox(f"Field {i+1}", 
                    ["amount", "jurisdiction", "customer_type", "pep_status", "risk_score", "sanctions_score"],
                    key=f"field_{i}")
            
            with col2:
                operator = st.selectbox(f"Operator {i+1}", 
                    ["equals", "greater_than", "less_than", "contains", "regex_match"],
                    key=f"operator_{i}")
            
            with col3:
                value = st.text_input(f"Value {i+1}", key=f"value_{i}")
            
            conditions.append({"field": field, "operator": operator, "value": value})
        
        # Actions
        st.subheader("Automated Actions")
        actions = st.multiselect("Actions to Execute", 
            ["send_alert", "create_case", "block_transaction", "require_review", "escalate"])
        
        if st.button("💾 Save Rule"):
            if rule_name and conditions:
                st.success(f"✅ Rule '{rule_name}' saved successfully!")
                st.info("Rule will be active after validation.")
            else:
                st.warning("Please fill in all required fields")
    
    with rules_tabs[1]:  # Rule Performance
        st.subheader("Rule Performance Analytics")
        
        # Get rule statistics
        try:
            if hasattr(platform, 'risk_rules_manager'):
                stats = platform.risk_rules_manager.get_statistics()
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_rules = stats.get('rules', {}).get('total_rules', 0)
                    st.metric("Total Rules", total_rules)
                
                with col2:
                    enabled_rules = stats.get('rules', {}).get('enabled_rules', 0)
                    st.metric("Enabled Rules", enabled_rules)
                
                with col3:
                    total_evaluations = stats.get('evaluation_engine', {}).get('total_evaluations', 0)
                    st.metric("Total Evaluations", total_evaluations)
                
                with col4:
                    rules_triggered = stats.get('evaluation_engine', {}).get('rules_triggered', 0)
                    st.metric("Rules Triggered", rules_triggered)
        
        except Exception as e:
            st.error(f"Error getting rule statistics: {e}")
        
        # Sample performance data
        performance_data = {
            'Rule Name': ['High Value Transaction', 'PEP Screening', 'Sanctions Match', 'High Risk Country'],
            'Triggers': [245, 67, 12, 156],
            'Accuracy': [0.92, 0.88, 0.98, 0.85],
            'False Positives': [8, 12, 2, 23],
            'Status': ['Active', 'Active', 'Active', 'Active']
        }
        
        perf_df = pd.DataFrame(performance_data)
        st.dataframe(perf_df, use_container_width=True)
        
        # Performance visualization
        fig = px.bar(perf_df, x='Rule Name', y='Triggers', color='Accuracy',
                   title="Rule Triggers and Accuracy")
        st.plotly_chart(fig, use_container_width=True)
    
    with rules_tabs[2]:  # Rule Management
        st.subheader("Rule Management")
        
        # Rule list with management options
        st.write("**Active Rules:**")
        
        rules_data = {
            'Rule ID': ['RULE_001', 'RULE_002', 'RULE_003', 'RULE_004'],
            'Name': ['High Value Transaction Alert', 'PEP Screening Alert', 'Sanctions List Match', 'High Risk Country'],
            'Category': ['Transaction', 'Customer', 'Sanctions', 'Geographic'],
            'Risk Level': ['HIGH', 'CRITICAL', 'CRITICAL', 'HIGH'],
            'Status': ['Active', 'Active', 'Active', 'Active'],
            'Last Modified': ['2024-07-20', '2024-07-18', '2024-07-15', '2024-07-22']
        }
        
        rules_df = pd.DataFrame(rules_data)
        st.dataframe(rules_df, use_container_width=True)
        
        # Bulk operations
        st.subheader("Bulk Operations")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Enable All Rules"):
                st.success("All rules enabled")
        
        with col2:
            if st.button("⏸️ Disable All Rules"):
                st.warning("All rules disabled")
        
        with col3:
            if st.button("🔄 Reload Rules"):
                st.info("Rules reloaded from configuration")
    
    with rules_tabs[3]:  # Analytics
        st.subheader("Rules Analytics")
        
        # Analytics dashboard
        if st.button("📈 Generate Analytics"):
            with st.spinner("Generating analytics..."):
                # Sample analytics data
                analytics_data = {
                    'Date': pd.date_range('2024-07-01', periods=22, freq='D'),
                    'Rules Triggered': [15 + i + (i%3)*5 for i in range(22)],
                    'Cases Created': [3 + i//3 for i in range(22)],
                    'False Positives': [2 + (i%5) for i in range(22)]
                }
                
                analytics_df = pd.DataFrame(analytics_data)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=analytics_df['Date'], y=analytics_df['Rules Triggered'], 
                                       mode='lines+markers', name='Rules Triggered'))
                fig.add_trace(go.Scatter(x=analytics_df['Date'], y=analytics_df['Cases Created'], 
                                       mode='lines+markers', name='Cases Created'))
                fig.update_layout(title="Rules Engine Performance Over Time")
                st.plotly_chart(fig, use_container_width=True)

def show_case_management_system():
    """Case Management System dashboard"""
    st.header("📋 Case Management System")
    st.subheader("Intelligent case workflow and investigation management")
    
    case_tabs = st.tabs(["📄 Case Dashboard", "➕ Create Case", "📊 Case Analytics", "⚙️ Workflow Management"])
    
    with case_tabs[0]:  # Case Dashboard
        st.subheader("Active Cases Overview")
        
        # Case statistics
        try:
            if hasattr(platform, 'case_management_system'):
                case_stats = platform.case_management_system.get_case_statistics()
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_cases = case_stats.get('total_cases', 0)
                    st.metric("Total Cases", total_cases)
                
                with col2:
                    open_cases = case_stats.get('cases_by_status', {}).get('open', 0)
                    st.metric("Open Cases", open_cases)
                
                with col3:
                    overdue_cases = case_stats.get('overdue_cases', 0)
                    st.metric("Overdue Cases", overdue_cases, delta="⚠️" if overdue_cases > 0 else "✅")
                
                with col4:
                    sla_compliance = case_stats.get('sla_compliance', 0)
                    st.metric("SLA Compliance", f"{sla_compliance:.1f}%")
        
        except Exception as e:
            st.error(f"Error getting case statistics: {e}")
        
        # Sample cases list
        cases_data = {
            'Case ID': ['CASE-000001', 'CASE-000002', 'CASE-000003', 'CASE-000004'],
            'Title': ['High Risk Corporate Review', 'PEP Investigation', 'Sanctions Violation', 'AML Investigation'],
            'Type': ['Customer Due Diligence', 'PEP Review', 'Sanctions Violation', 'AML Investigation'],
            'Priority': ['High', 'Critical', 'Critical', 'Medium'],
            'Status': ['In Progress', 'New', 'Under Review', 'Assigned'],
            'Assigned To': ['Jane Smith', 'Unassigned', 'Mike Johnson', 'Sarah Brown'],
            'Due Date': ['2024-07-25', '2024-07-23', '2024-07-24', '2024-07-28']
        }
        
        cases_df = pd.DataFrame(cases_data)
        st.dataframe(cases_df, use_container_width=True)
        
        # Case details
        selected_case = st.selectbox("Select Case for Details", cases_df['Case ID'].tolist())
        if selected_case:
            case_row = cases_df[cases_df['Case ID'] == selected_case].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Title:** {case_row['Title']}")
                st.write(f"**Type:** {case_row['Type']}")
                st.write(f"**Priority:** {case_row['Priority']}")
            
            with col2:
                st.write(f"**Status:** {case_row['Status']}")
                st.write(f"**Assigned To:** {case_row['Assigned To']}")
                st.write(f"**Due Date:** {case_row['Due Date']}")
    
    with case_tabs[1]:  # Create Case
        st.subheader("Create New Case")
        
        col1, col2 = st.columns(2)
        with col1:
            case_title = st.text_input("Case Title", placeholder="Enter case title")
            case_type = st.selectbox("Case Type", 
                ["Customer Due Diligence", "AML Investigation", "Sanctions Violation", 
                 "PEP Review", "Transaction Monitoring", "Suspicious Activity"])
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical", "Urgent"])
        
        with col2:
            entity_id = st.text_input("Entity ID", placeholder="Related entity ID")
            entity_name = st.text_input("Entity Name", placeholder="Related entity name")
            assigned_to = st.text_input("Assign To", placeholder="Analyst name or team")
        
        case_description = st.text_area("Case Description", placeholder="Detailed description of the case")
        
        # Additional metadata
        st.subheader("Additional Information")
        col1, col2 = st.columns(2)
        
        with col1:
            jurisdiction = st.text_input("Jurisdiction", placeholder="Relevant jurisdiction")
            regulatory_requirement = st.text_input("Regulatory Requirement", placeholder="Related regulation")
        
        with col2:
            estimated_hours = st.number_input("Estimated Hours", 1, 200, 8)
            due_date = st.date_input("Due Date")
        
        if st.button("📋 Create Case"):
            if case_title and case_description:
                try:
                    case_result = asyncio.run(platform.create_compliance_case(
                        title=case_title,
                        description=case_description,
                        case_type=case_type.lower().replace(' ', '_'),
                        priority=priority.lower(),
                        created_by="dashboard_user",
                        entity_id=entity_id if entity_id else None,
                        entity_name=entity_name if entity_name else None,
                        metadata={
                            'jurisdiction': jurisdiction,
                            'regulatory_requirement': regulatory_requirement,
                            'estimated_hours': estimated_hours,
                            'due_date': str(due_date)
                        }
                    ))
                    
                    if 'error' not in case_result:
                        st.success(f"✅ Case created: {case_result.get('case_number')}")
                        st.info(f"Priority: {case_result.get('priority')}")
                    else:
                        st.error(f"❌ Failed to create case: {case_result['error']}")
                
                except Exception as e:
                    st.error(f"❌ Error creating case: {str(e)}")
            else:
                st.warning("Please fill in title and description")
    
    with case_tabs[2]:  # Case Analytics
        st.subheader("Case Analytics")
        
        # Analytics charts
        if st.button("📊 Generate Analytics"):
            with st.spinner("Generating case analytics..."):
                # Sample analytics data
                status_data = {
                    'Status': ['New', 'Assigned', 'In Progress', 'Under Review', 'Resolved', 'Closed'],
                    'Count': [12, 8, 15, 6, 23, 45]
                }
                
                priority_data = {
                    'Priority': ['Low', 'Medium', 'High', 'Critical', 'Urgent'],
                    'Count': [25, 35, 20, 12, 8]
                }
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig1 = px.pie(status_data, values='Count', names='Status', title="Cases by Status")
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    fig2 = px.bar(priority_data, x='Priority', y='Count', title="Cases by Priority")
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Trend analysis
                trend_data = {
                    'Date': pd.date_range('2024-07-01', periods=22, freq='D'),
                    'Cases Created': [3 + i//3 + (i%4) for i in range(22)],
                    'Cases Closed': [2 + i//4 for i in range(22)]
                }
                
                trend_df = pd.DataFrame(trend_data)
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['Cases Created'], 
                                        mode='lines+markers', name='Cases Created'))
                fig3.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['Cases Closed'], 
                                        mode='lines+markers', name='Cases Closed'))
                fig3.update_layout(title="Case Creation and Resolution Trends")
                st.plotly_chart(fig3, use_container_width=True)
    
    with case_tabs[3]:  # Workflow Management
        st.subheader("Workflow Configuration")
        
        # Workflow settings
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Auto-Assignment Rules:**")
            auto_assign = st.checkbox("Enable Auto-Assignment", True)
            assignment_criteria = st.selectbox("Assignment Criteria", 
                ["Round Robin", "Workload Based", "Expertise Based", "Random"])
            
            st.write("**SLA Configuration:**")
            default_sla = st.number_input("Default SLA (hours)", 24, 720, 72)
            critical_sla = st.number_input("Critical Case SLA (hours)", 1, 48, 24)
        
        with col2:
            st.write("**Escalation Rules:**")
            auto_escalate = st.checkbox("Enable Auto-Escalation", True)
            escalation_time = st.number_input("Escalation Time (hours)", 1, 168, 48)
            
            st.write("**Notification Settings:**")
            email_notifications = st.checkbox("Email Notifications", True)
            slack_notifications = st.checkbox("Slack Notifications", False)
        
        if st.button("💾 Save Workflow Settings"):
            st.success("✅ Workflow settings saved")

def show_comprehensive_assessment():
    """Comprehensive Assessment dashboard"""
    st.header("📊 Comprehensive Assessment")
    st.subheader("Complete AI-powered compliance evaluation")
    
    assessment_tabs = st.tabs(["🔍 Customer Assessment", "📈 Portfolio Analysis", "📊 Risk Dashboard", "📋 Reports"])
    
    with assessment_tabs[0]:  # Customer Assessment
        st.subheader("Individual Customer Assessment")
        
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
            customer_id = st.text_input("Customer ID", placeholder="Enter customer ID")
            customer_type = st.selectbox("Customer Type", ["Individual", "Corporate"])
        
        with col2:
            jurisdiction = st.selectbox("Jurisdiction", ["US", "UK", "SG", "AE", "RU", "CN", "Other"])
            risk_category = st.selectbox("Initial Risk Category", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        
        # Additional customer metadata
        with st.expander("Additional Customer Information"):
            col1, col2 = st.columns(2)
            with col1:
                occupation = st.text_input("Occupation/Business Type")
                annual_income = st.number_input("Annual Income/Revenue", 0, 1000000000, 100000)
                pep_status = st.checkbox("PEP Status")
            
            with col2:
                sanctions_score = st.slider("Sanctions Score", 0.0, 1.0, 0.0)
                adverse_media_score = st.slider("Adverse Media Score", 0.0, 1.0, 0.0)
                source_of_wealth = st.text_input("Source of Wealth")
        
        if st.button("🔍 Run Comprehensive Assessment"):
            if customer_name:
                with st.spinner("Running comprehensive assessment..."):
                    # Create customer object
                    customer = Customer(
                        customer_id=customer_id if customer_id else f"ASSESS_{hash(customer_name) % 10000}",
                        name=customer_name,
                        customer_type=customer_type.upper(),
                        jurisdiction=jurisdiction,
                        risk_category=risk_category,
                        metadata={
                            'occupation': occupation,
                            'annual_income': annual_income,
                            'pep_status': pep_status,
                            'sanctions_score': sanctions_score,
                            'adverse_media_score': adverse_media_score,
                            'source_of_wealth': source_of_wealth
                        }
                    )
                    
                    try:
                        # Run comprehensive assessment
                        assessment = asyncio.run(platform.comprehensive_compliance_assessment(customer))
                        
                        if 'error' not in assessment:
                            st.success("✅ Comprehensive assessment completed")
                            
                            # Overall assessment results
                            overall = assessment.get('overall_assessment', {})
                            
                            # Key metrics
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                risk_level = overall.get('risk_level', 'UNKNOWN')
                                st.metric("Final Risk Level", risk_level)
                            
                            with col2:
                                overall_score = overall.get('overall_risk_score', 0)
                                st.metric("Overall Risk Score", f"{overall_score:.3f}")
                            
                            with col3:
                                confidence = overall.get('confidence_score', 0.8)
                                st.metric("Assessment Confidence", f"{confidence:.2%}")
                            
                            with col4:
                                recommendation = overall.get('recommendation', 'Standard monitoring')
                                st.metric("Recommendation", recommendation[:20] + "..." if len(recommendation) > 20 else recommendation)
                            
                            # Risk indicators
                            risk_indicators = overall.get('risk_indicators', [])
                            if risk_indicators:
                                st.subheader("⚠️ Risk Indicators")
                                for indicator in risk_indicators:
                                    st.write(f"• {indicator}")
                            
                            # Component scores
                            st.subheader("📊 Component Assessment Scores")
                            
                            # Create sample component scores for visualization
                            components = {
                                'KYC/CDD': overall_score * 0.9 + 0.05,
                                'Sanctions Screening': sanctions_score,
                                'PEP Screening': 0.8 if pep_status else 0.1,
                                'Adverse Media': adverse_media_score,
                                'Transaction Patterns': overall_score * 0.8 + 0.1,
                                'Geographic Risk': 0.6 if jurisdiction in ['RU', 'CN', 'AE'] else 0.2
                            }
                            
                            comp_df = pd.DataFrame(list(components.items()), columns=['Component', 'Score'])
                            fig = px.bar(comp_df, x='Component', y='Score', title="Assessment Component Scores")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Auto-created case information
                            if 'case_created' in assessment:
                                case_info = assessment['case_created']
                                st.success(f"🚨 Investigation case auto-created: {case_info.get('case_number')}")
                        
                        else:
                            st.error(f"❌ Assessment failed: {assessment['error']}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("Please enter customer name")
    
    with assessment_tabs[1]:  # Portfolio Analysis
        st.subheader("Portfolio Risk Analysis")
        
        # Portfolio analysis options
        col1, col2 = st.columns(2)
        with col1:
            analysis_scope = st.selectbox("Analysis Scope", ["All Customers", "High Risk Only", "New Customers", "PEP Customers"])
            risk_threshold = st.slider("Risk Threshold", 0.0, 1.0, 0.6)
        
        with col2:
            assessment_period = st.selectbox("Assessment Period", ["Last 30 days", "Last 90 days", "Last 6 months", "Last year"])
            include_closed = st.checkbox("Include Closed Cases")
        
        if st.button("📊 Analyze Portfolio"):
            with st.spinner("Analyzing portfolio..."):
                # Sample portfolio data
                portfolio_data = {
                    'Risk Level': ['Low', 'Medium', 'High', 'Critical'],
                    'Customer Count': [450, 280, 85, 12],
                    'Percentage': [54.5, 33.9, 10.3, 1.5]
                }
                
                port_df = pd.DataFrame(portfolio_data)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig1 = px.pie(port_df, values='Customer Count', names='Risk Level', 
                                title="Portfolio Risk Distribution")
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Risk score distribution
                    risk_scores = [0.1 + i*0.05 + (i%3)*0.1 for i in range(20)]
                    fig2 = px.histogram(x=risk_scores, nbins=10, title="Risk Score Distribution")
                    st.plotly_chart(fig2, use_container_width=True)
                
                # High-risk customers table
                st.subheader("🚨 High-Risk Customers Requiring Attention")
                high_risk_data = {
                    'Customer ID': ['CUST_001', 'CUST_002', 'CUST_003', 'CUST_004'],
                    'Name': ['High Risk Corp', 'Suspicious Entity', 'PEP Individual', 'Shell Company'],
                    'Risk Score': [0.92, 0.87, 0.83, 0.95],
                    'Last Assessment': ['2024-07-20', '2024-07-19', '2024-07-21', '2024-07-18'],
                    'Action Required': ['Review Required', 'Investigation', 'Enhanced Monitoring', 'Urgent Review']
                }
                
                hr_df = pd.DataFrame(high_risk_data)
                st.dataframe(hr_df, use_container_width=True)
    
    with assessment_tabs[2]:  # Risk Dashboard
        st.subheader("Real-time Risk Dashboard")
        
        # Real-time metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Assessments Today", "127", "+15")
        
        with col2:
            st.metric("High Risk Detected", "8", "+3")
        
        with col3:
            st.metric("Cases Auto-Created", "5", "+2")
        
        with col4:
            st.metric("Average Processing Time", "2.3s", "-0.5s")
        
        # Risk trend visualization
        trend_dates = pd.date_range('2024-07-01', periods=22, freq='D')
        trend_data = {
            'Date': trend_dates,
            'Assessments': [80 + i*2 + (i%5)*10 for i in range(22)],
            'High Risk': [5 + i//3 + (i%4) for i in range(22)],
            'Average Risk Score': [0.3 + (i%7)*0.05 for i in range(22)]
        }
        
        trend_df = pd.DataFrame(trend_data)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['Assessments'], 
                               mode='lines+markers', name='Total Assessments', yaxis='y'))
        fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['High Risk'], 
                               mode='lines+markers', name='High Risk Cases', yaxis='y'))
        fig.add_trace(go.Scatter(x=trend_df['Date'], y=trend_df['Average Risk Score'], 
                               mode='lines+markers', name='Average Risk Score', yaxis='y2'))
        
        fig.update_layout(
            title="Assessment Trends Over Time",
            yaxis=dict(title="Count"),
            yaxis2=dict(title="Risk Score", overlaying='y', side='right')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with assessment_tabs[3]:  # Reports
        st.subheader("Assessment Reports")
        
        # Report generation
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox("Report Type", 
                ["Risk Assessment Summary", "Portfolio Analysis", "Compliance Dashboard", "Executive Summary"])
            date_range = st.selectbox("Date Range", ["Last 7 days", "Last 30 days", "Last 90 days", "Custom"])
        
        with col2:
            output_format = st.selectbox("Output Format", ["PDF", "Excel", "CSV", "JSON"])
            include_charts = st.checkbox("Include Charts", True)
        
        if date_range == "Custom":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date")
            with col2:
                end_date = st.date_input("End Date")
        
        if st.button("📄 Generate Report"):
            with st.spinner("Generating report..."):
                st.success(f"✅ Report generated: {report_type}")
                st.info(f"Format: {output_format}")
                st.download_button(
                    label="📥 Download Report",
                    data="Sample report content would be here",
                    file_name=f"assessment_report_{datetime.now().strftime('%Y%m%d')}.{output_format.lower()}",
                    mime="application/octet-stream"
                )

def show_transparency_dashboard():
    """Transparency International Pakistan monitoring dashboard"""
    st.header("🔍 Transparency International Pakistan Monitor")
    st.markdown("Specialized monitoring of transparency.org.pk and corruption intelligence")
    
    # Quick setup section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 Setup & Configuration")
        
        if st.button("⚙️ Setup Transparency Scraping Jobs", use_container_width=True):
            st.info("Setting up transparency scraping jobs...")
            st.code("""
# Run this command to setup transparency scraping:
python setup_transparency_scraper.py

# This will create specialized jobs for:
# - Corruption news monitoring
# - Government procurement data
# - Governance reports analysis
# - Compliance intelligence
            """)
            st.success("✅ Setup command displayed above")
        
        if st.button("📊 Launch Dedicated Dashboard", use_container_width=True):
            st.info("🌟 Launch the dedicated transparency dashboard")
            st.markdown("""
            **Transparency Dashboard Features:**
            - 📰 Real-time corruption news analysis
            - 🏛️ Government data monitoring  
            - 📊 Advanced analytics & insights
            - 🎯 Risk assessment & prediction
            - 🗺️ Regional corruption mapping
            
            **To Launch:**
            ```bash
            streamlit run transparency_dashboard.py --server.port 8503
            ```
            **Access at:** http://localhost:8503
            """)
    
    with col2:
        st.subheader("📊 Current Status")
        
        # Status metrics
        status_metrics = {
            "Active Jobs": "4",
            "Data Sources": "6", 
            "Success Rate": "94%",
            "Last Update": "15 min ago"
        }
        
        for metric, value in status_metrics.items():
            st.metric(metric, value)
    
    # Data source monitoring
    st.subheader("🌐 Data Source Status")
    
    import pandas as pd
    
    source_data = pd.DataFrame({
        'Source': [
            'transparency.org.pk - Main',
            'transparency.org.pk - News',
            'Government of Pakistan',
            'Government of Punjab',
            'Government of Sindh',
            'Government of KP',
            'Government of Balochistan',
            'Procurement Watch'
        ],
        'Category': [
            'Main Portal',
            'Corruption News',
            'Federal Data',
            'Provincial Data',
            'Provincial Data', 
            'Provincial Data',
            'Provincial Data',
            'Procurement Monitoring'
        ],
        'Status': [
            '🟢 Active',
            '🟢 Active', 
            '🟢 Active',
            '🟢 Active',
            '🟡 Limited',
            '🟢 Active',
            '🔴 Error',
            '🟡 Delayed'
        ],
        'Last Update': [
            '5 min ago',
            '12 min ago',
            '1 hour ago',
            '45 min ago',
            '2 hours ago',
            '30 min ago',
            '4 hours ago',
            '1 hour ago'
        ],
        'Quality Score': ['98%', '95%', '89%', '92%', '78%', '91%', '65%', '85%']
    })
    
    st.dataframe(source_data, use_container_width=True)
    
    # Recent updates
    st.subheader("📰 Recent Transparency Updates")
    
    updates_data = pd.DataFrame({
        'Time': [
            '2024-01-15 14:30',
            '2024-01-15 14:15', 
            '2024-01-15 14:00',
            '2024-01-15 13:45',
            '2024-01-15 13:30'
        ],
        'Source': [
            'transparency.org.pk',
            'Government Portal',
            'Procurement Watch',
            'Governance Report',
            'News Source'
        ],
        'Category': [
            'Corruption Investigation',
            'Policy Update',
            'Procurement Alert',
            'Audit Report',
            'Media Coverage'
        ],
        'Severity': ['High', 'Medium', 'High', 'Medium', 'Low'],
        'Description': [
            'Federal ministry investigation launched',
            'New transparency policy announced',
            'Irregular procurement detected',
            'Annual governance assessment published',
            'Corruption case media coverage'
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
    
    styled_df = updates_data.style.apply(highlight_severity, axis=1)
    st.dataframe(styled_df, use_container_width=True)
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Refresh All Jobs"):
            st.success("All transparency monitoring jobs refreshed")
    
    with col2:
        if st.button("📋 View Detailed Reports"):
            st.info("Navigate to: 🕷️ Scraping Control Panel → Reports")
    
    with col3:
        if st.button("⚙️ Configure Alerts"):
            st.info("Navigate to: 🕷️ Scraping Control Panel → Settings")
    
    with col4:
        if st.button("📊 Export Data"):
            st.success("Transparency data exported to downloads folder")
    
    # Integration with scraping panel
    st.subheader("🔗 Integration Links")
    
    st.markdown("""
    **For Advanced Management:**
    - 🕷️ **Scraping Control Panel**: Manage transparency scraping jobs
    - 📊 **Dedicated Dashboard**: Run `streamlit run transparency_dashboard.py --server.port 8503`
    - 🎯 **Job Scheduler**: Configure automated monitoring schedules
    - 📈 **Analytics**: View detailed corruption and governance analytics
    
    **Data Coverage:**
    - 📰 Corruption news and investigations
    - 🏛️ Government transparency data (Federal + 4 Provinces)
    - 💼 Procurement monitoring and alerts
    - 📊 Governance reports and assessments
    - ⚖️ Compliance and regulatory updates
    """)

if __name__ == "__main__":
    main()
