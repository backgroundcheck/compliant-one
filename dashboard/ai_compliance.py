"""
AI Compliance Dashboard Component
RAGFlow-powered AI compliance interface for Compliant-One platform
"""

import streamlit as st
import asyncio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time

# Import RAGFlow integration
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from integrations.ragflow import (
    upload_regulation_document,
    upload_regulation_directory,
    search_compliance_regulations,
    get_ai_compliance_guidance,
    analyze_uploaded_document,
    get_ragflow_status
)
from services.ai.compliance_chat import QuestionType, UrgencyLevel

class AIComplianceDashboard:
    """AI-powered compliance dashboard"""
    
    def __init__(self):
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'ragflow_status' not in st.session_state:
            st.session_state.ragflow_status = None
        if 'uploaded_documents' not in st.session_state:
            st.session_state.uploaded_documents = []
        if 'search_results' not in st.session_state:
            st.session_state.search_results = []
        if 'chat_sessions' not in st.session_state:
            st.session_state.chat_sessions = {}
            
    def render(self):
        """Render the AI compliance dashboard"""
        
        st.title("🤖 AI Compliance Assistant")
        st.markdown("*Powered by RAGFlow - Advanced document understanding and compliance guidance*")
        
        # Check RAGFlow status
        self._render_status_section()
        
        # Main tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📄 Document Upload", 
            "🔍 Smart Search", 
            "💬 Compliance Chat",
            "📊 Analytics",
            "⚙️ Settings"
        ])
        
        with tab1:
            self._render_document_upload()
            
        with tab2:
            self._render_smart_search()
            
        with tab3:
            self._render_compliance_chat()
            
        with tab4:
            self._render_analytics()
            
        with tab5:
            self._render_settings()
            
    def _render_status_section(self):
        """Render RAGFlow status section"""
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("🔄 Check RAGFlow Status", key="check_status"):
                with st.spinner("Checking RAGFlow status..."):
                    try:
                        status = asyncio.run(get_ragflow_status())
                        st.session_state.ragflow_status = status
                    except Exception as e:
                        st.error(f"Failed to check status: {e}")
                        
        if st.session_state.ragflow_status:
            status = st.session_state.ragflow_status
            
            with col2:
                if status.get('health', {}).get('status') == 'healthy':
                    st.success("🟢 RAGFlow Healthy")
                else:
                    st.error("🔴 RAGFlow Issues")
                    
            with col3:
                sync_stats = status.get('synchronization', {})
                total_docs = sync_stats.get('total_documents', 0)
                st.metric("Documents", total_docs)
                
            # Detailed status in expander
            with st.expander("Detailed Status", expanded=False):
                st.json(status)
                
    def _render_document_upload(self):
        """Render document upload interface"""
        
        st.header("📄 Regulatory Document Upload")
        
        # Upload options
        upload_type = st.radio(
            "Upload Type:",
            ["Single Document", "Directory Batch"],
            horizontal=True
        )
        
        if upload_type == "Single Document":
            self._render_single_upload()
        else:
            self._render_batch_upload()
            
        # Recent uploads
        if st.session_state.uploaded_documents:
            st.subheader("Recent Uploads")
            
            upload_df = pd.DataFrame(st.session_state.uploaded_documents)
            st.dataframe(upload_df, use_container_width=True)
            
    def _render_single_upload(self):
        """Render single document upload"""
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose regulatory document",
                type=['pdf', 'docx', 'doc', 'txt', 'md'],
                help="Upload regulatory documents, policies, or compliance guidelines"
            )
            
        with col2:
            jurisdiction = st.selectbox(
                "Jurisdiction:",
                ["International", "US", "EU", "UK", "Singapore", "Hong Kong", "Other"]
            )
            
        if uploaded_file:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                document_type = st.selectbox(
                    "Document Type:",
                    ["Regulation", "Policy", "Guideline", "Standard", "Template"]
                )
                
            with col2:
                tags = st.text_input(
                    "Tags (comma-separated):",
                    placeholder="aml, kyc, fatf, sanctions"
                )
                
            if st.button("📤 Upload Document", type="primary"):
                self._process_single_upload(uploaded_file, jurisdiction, document_type, tags)
                
    def _render_batch_upload(self):
        """Render batch document upload"""
        
        st.info("📁 Upload a directory containing multiple regulatory documents")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            directory_path = st.text_input(
                "Directory Path:",
                placeholder="/path/to/regulations/directory",
                help="Path to directory containing regulatory documents"
            )
            
        with col2:
            jurisdiction = st.selectbox(
                "Jurisdiction:",
                ["International", "US", "EU", "UK", "Singapore", "Hong Kong"],
                key="batch_jurisdiction"
            )
            
        if st.button("📂 Upload Directory", type="primary"):
            if directory_path:
                self._process_batch_upload(directory_path, jurisdiction)
            else:
                st.error("Please specify a directory path")
                
    def _render_smart_search(self):
        """Render smart search interface"""
        
        st.header("🔍 Smart Regulatory Search")
        
        # Search input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input(
                "Search Query:",
                placeholder="Enter your compliance question or topic...",
                help="Use natural language to search regulatory content"
            )
            
        with col2:
            search_filters = st.selectbox(
                "Filter by:",
                ["All Documents", "Regulations", "Policies", "Guidelines"]
            )
            
        # Advanced search options
        with st.expander("🔧 Advanced Search Options"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                jurisdiction_filter = st.selectbox(
                    "Jurisdiction:",
                    ["All", "International", "US", "EU", "UK", "Singapore", "Hong Kong"]
                )
                
            with col2:
                date_range = st.date_input(
                    "Date Range:",
                    value=None,
                    help="Filter by document date"
                )
                
            with col3:
                result_limit = st.slider(
                    "Max Results:",
                    min_value=5,
                    max_value=50,
                    value=10
                )
                
        # Search button
        if st.button("🔍 Search", type="primary") and search_query:
            self._process_search(search_query, search_filters, jurisdiction_filter)
            
        # Display search results
        if st.session_state.search_results:
            self._display_search_results()
            
    def _render_compliance_chat(self):
        """Render compliance chat interface"""
        
        st.header("💬 AI Compliance Assistant")
        
        # Chat input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_question = st.text_area(
                "Ask a compliance question:",
                placeholder="e.g., What are the KYC requirements for high-risk customers?",
                height=100
            )
            
        with col2:
            question_type = st.selectbox(
                "Question Type:",
                [
                    "General Compliance",
                    "Regulatory Guidance", 
                    "Risk Assessment",
                    "KYC Guidance",
                    "AML Guidance",
                    "Sanctions Check",
                    "Policy Clarification",
                    "Reporting Requirements"
                ]
            )
            
            urgency = st.selectbox(
                "Urgency:",
                ["Low", "Medium", "High", "Critical"]
            )
            
        if st.button("💬 Ask Question", type="primary") and user_question:
            self._process_chat_question(user_question, question_type, urgency)
            
        # Chat history
        if 'current_chat' in st.session_state:
            st.subheader("Chat Response")
            
            chat_response = st.session_state.current_chat
            st.markdown(chat_response.get('guidance', 'No response generated'))
            
            # Sources
            if chat_response.get('sources'):
                with st.expander("📚 Sources & References"):
                    for i, source in enumerate(chat_response['sources'][:5]):
                        st.markdown(f"**Source {i+1}:** {source.get('content', 'N/A')[:200]}...")
                        
    def _render_analytics(self):
        """Render analytics dashboard"""
        
        st.header("📊 AI Compliance Analytics")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Documents Processed", len(st.session_state.uploaded_documents))
        with col2:
            st.metric("Search Queries", len(st.session_state.search_results))
        with col3:
            st.metric("Chat Sessions", len(st.session_state.chat_sessions))
        with col4:
            avg_conf = 0.85  # Placeholder
            st.metric("Avg Confidence", f"{avg_conf:.2f}")
            
        # Charts
        if st.session_state.uploaded_documents:
            # Document types distribution
            df = pd.DataFrame(st.session_state.uploaded_documents)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'document_type' in df.columns:
                    fig_pie = px.pie(
                        df, 
                        names='document_type',
                        title="Document Types Distribution"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
            with col2:
                if 'jurisdiction' in df.columns:
                    fig_bar = px.bar(
                        df.groupby('jurisdiction').size().reset_index(name='count'),
                        x='jurisdiction',
                        y='count',
                        title="Documents by Jurisdiction"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                    
    def _render_settings(self):
        """Render settings interface"""
        
        st.header("⚙️ RAGFlow Integration Settings")
        
        # Configuration settings
        with st.expander("🔧 Configuration", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                api_url = st.text_input(
                    "RAGFlow API URL:",
                    value="http://localhost:9380",
                    help="RAGFlow service endpoint"
                )
                
                chunk_size = st.slider(
                    "Chunk Size:",
                    min_value=256,
                    max_value=2048,
                    value=1024,
                    help="Document chunking size"
                )
                
            with col2:
                similarity_threshold = st.slider(
                    "Similarity Threshold:",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.8,
                    help="Search similarity threshold"
                )
                
                max_results = st.slider(
                    "Max Search Results:",
                    min_value=5,
                    max_value=50,
                    value=10
                )
                
        # Performance monitoring
        with st.expander("📈 Performance Monitoring"):
            if st.button("📊 Generate Performance Report"):
                self._generate_performance_report()
                
    def _process_single_upload(self, uploaded_file, jurisdiction, document_type, tags):
        """Process single document upload"""
        
        with st.spinner("Uploading and processing document..."):
            try:
                # Save uploaded file temporarily
                temp_path = f"/tmp/{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                    
                # Process tags
                tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
                
                # Upload to RAGFlow
                result = asyncio.run(upload_regulation_document(
                    temp_path,
                    jurisdiction.lower() if jurisdiction != "Other" else None,
                    tag_list
                ))
                
                if result['success']:
                    st.success(f"✅ Document uploaded successfully! Document ID: {result['document_id']}")
                    
                    # Add to session state
                    upload_info = {
                        'filename': uploaded_file.name,
                        'document_id': result['document_id'],
                        'jurisdiction': jurisdiction,
                        'document_type': document_type,
                        'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'chunks_created': result.get('chunks_created', 0),
                        'processing_time': f"{result.get('processing_time', 0):.2f}s"
                    }
                    st.session_state.uploaded_documents.append(upload_info)
                    
                    # Show processing details
                    with st.expander("Processing Details"):
                        st.json(result)
                        
                else:
                    st.error(f"❌ Upload failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Upload error: {e}")
                
    def _process_batch_upload(self, directory_path, jurisdiction):
        """Process batch document upload"""
        
        with st.spinner("Processing directory batch upload..."):
            try:
                result = asyncio.run(upload_regulation_directory(
                    directory_path,
                    jurisdiction.lower()
                ))
                
                st.success(f"✅ Batch upload completed!")
                st.info(f"📊 {result['successful']}/{result['total_processed']} documents processed successfully")
                
                # Show detailed results
                with st.expander("Batch Results Details"):
                    st.json(result)
                    
            except Exception as e:
                st.error(f"❌ Batch upload error: {e}")
                
    def _process_search(self, query, filters, jurisdiction):
        """Process search request"""
        
        with st.spinner("Searching regulatory documents..."):
            try:
                doc_type = None if filters == "All Documents" else filters.lower()
                juris = None if jurisdiction == "All" else jurisdiction.lower()
                
                result = asyncio.run(search_compliance_regulations(
                    query,
                    juris,
                    doc_type
                ))
                
                if result['success']:
                    st.session_state.search_results = result['results']
                    st.success(f"✅ Found {result['results_count']} relevant documents")
                else:
                    st.error(f"❌ Search failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Search error: {e}")
                
    def _process_chat_question(self, question, question_type, urgency):
        """Process chat question"""
        
        with st.spinner("Getting AI compliance guidance..."):
            try:
                # Map UI values to enum values
                type_mapping = {
                    "General Compliance": QuestionType.GENERAL_COMPLIANCE,
                    "Regulatory Guidance": QuestionType.REGULATORY_GUIDANCE,
                    "Risk Assessment": QuestionType.RISK_ASSESSMENT,
                    "KYC Guidance": QuestionType.KYC_GUIDANCE,
                    "AML Guidance": QuestionType.AML_GUIDANCE,
                    "Sanctions Check": QuestionType.SANCTIONS_CHECK,
                    "Policy Clarification": QuestionType.POLICY_CLARIFICATION,
                    "Reporting Requirements": QuestionType.REPORTING_REQUIREMENT
                }
                
                qt = type_mapping.get(question_type, QuestionType.GENERAL_COMPLIANCE)
                
                result = asyncio.run(get_ai_compliance_guidance(
                    question,
                    urgency.lower(),
                    qt
                ))
                
                if result['success']:
                    st.session_state.current_chat = result
                    st.success("✅ AI guidance generated successfully!")
                else:
                    st.error(f"❌ Chat failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Chat error: {e}")
                
    def _display_search_results(self):
        """Display search results"""
        
        st.subheader("🔍 Search Results")
        
        for i, result in enumerate(st.session_state.search_results):
            with st.expander(f"Result {i+1}: {result.get('doc_name', 'Unknown Document')}"):
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    content = result.get('content_with_weight', '')
                    st.markdown(f"**Content:** {content[:500]}...")
                    
                with col2:
                    st.metric("Relevance Score", f"{result.get('similarity', 0):.3f}")
                    st.metric("Compliance Score", f"{result.get('compliance_score', 0):.2f}")
                    
                # Action buttons
                if st.button(f"📄 Analyze Document", key=f"analyze_{i}"):
                    doc_id = result.get('doc_id')
                    if doc_id:
                        self._analyze_document(doc_id)
                        
    def _analyze_document(self, document_id):
        """Analyze document for compliance insights"""
        
        with st.spinner("Analyzing document for compliance insights..."):
            try:
                result = asyncio.run(analyze_uploaded_document(document_id))
                
                if result['success']:
                    analysis = result['analysis']
                    
                    st.subheader("📊 Compliance Analysis")
                    st.markdown(analysis.get('analysis', 'No analysis available'))
                    
                    # Key findings
                    if analysis.get('key_findings'):
                        st.subheader("🔍 Key Findings")
                        for finding in analysis['key_findings']:
                            st.markdown(f"• {finding}")
                            
                else:
                    st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Analysis error: {e}")
                
    def _generate_performance_report(self):
        """Generate performance monitoring report"""
        
        # Placeholder performance data
        performance_data = {
            'avg_upload_time': '2.3s',
            'avg_search_time': '0.8s',
            'avg_chat_response_time': '3.1s',
            'system_uptime': '99.8%',
            'total_documents': len(st.session_state.uploaded_documents),
            'total_searches': len(st.session_state.search_results)
        }
        
        st.json(performance_data)

def render_ai_compliance_dashboard():
    """Render the AI compliance dashboard"""
    dashboard = AIComplianceDashboard()
    dashboard.render()

if __name__ == "__main__":
    render_ai_compliance_dashboard()
