"""
Compliance Chat Service with RAGFlow Integration
Provides AI-powered conversational interface for compliance questions and guidance
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from .ragflow_client import get_ragflow_client, get_knowledge_manager, RAGFlowError
from ...utils.logger import get_logger

logger = get_logger(__name__)

class QuestionType(Enum):
    """Types of compliance questions"""
    REGULATORY_GUIDANCE = "regulatory_guidance"
    RISK_ASSESSMENT = "risk_assessment"
    POLICY_CLARIFICATION = "policy_clarification"
    PROCEDURE_INQUIRY = "procedure_inquiry"
    SANCTIONS_CHECK = "sanctions_check"
    KYC_GUIDANCE = "kyc_guidance"
    AML_GUIDANCE = "aml_guidance"
    REPORTING_REQUIREMENT = "reporting_requirement"
    GENERAL_COMPLIANCE = "general_compliance"

class UrgencyLevel(Enum):
    """Urgency levels for compliance questions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ChatMessage:
    """Chat message structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: str = "user"  # user, assistant, system
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    question_type: Optional[QuestionType] = None
    urgency: Optional[UrgencyLevel] = None
    sources: List[Dict] = field(default_factory=list)
    confidence_score: float = 0.0
    processing_time: float = 0.0

@dataclass
class ChatSession:
    """Chat session management"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    title: str = "Compliance Chat"
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)

class ComplianceChatService:
    """AI-powered compliance chat service"""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.active_sessions: Dict[str, ChatSession] = {}
        
        # Compliance-specific prompts and templates
        self.system_prompts = {
            QuestionType.REGULATORY_GUIDANCE: """
            You are an expert compliance advisor specializing in financial regulations.
            Provide precise, actionable guidance based on current regulatory requirements.
            Always cite specific regulations, standards, or guidelines when applicable.
            Focus on practical implementation steps and compliance requirements.
            """,
            
            QuestionType.RISK_ASSESSMENT: """
            You are a risk assessment specialist with expertise in AML/CFT compliance.
            Analyze scenarios for potential compliance risks and provide mitigation strategies.
            Consider FATF recommendations, local regulations, and industry best practices.
            Provide risk ratings and detailed remediation steps.
            """,
            
            QuestionType.KYC_GUIDANCE: """
            You are a KYC/CDD expert with deep knowledge of customer due diligence requirements.
            Provide guidance on customer identification, verification, and ongoing monitoring.
            Reference applicable FATF recommendations and local KYC regulations.
            Focus on practical implementation and documentation requirements.
            """,
            
            QuestionType.AML_GUIDANCE: """
            You are an AML specialist with expertise in anti-money laundering compliance.
            Provide guidance on AML program requirements, suspicious activity monitoring,
            and regulatory reporting obligations. Reference FATF recommendations and
            jurisdiction-specific AML laws and regulations.
            """,
            
            QuestionType.SANCTIONS_CHECK: """
            You are a sanctions compliance expert with knowledge of global sanctions programs.
            Provide guidance on sanctions screening, list management, and compliance procedures.
            Consider OFAC, EU, UN, and other relevant sanctions regimes.
            Focus on operational procedures and risk mitigation.
            """
        }
        
    async def create_session(self, user_id: Optional[str] = None, 
                           title: str = "Compliance Chat") -> str:
        """Create new chat session"""
        
        session = ChatSession(
            user_id=user_id,
            title=title
        )
        
        self.active_sessions[session.session_id] = session
        
        # Add welcome message
        welcome_msg = ChatMessage(
            role="assistant",
            content="""
            Welcome to Compliant-One AI Compliance Assistant! 
            
            I can help you with:
            • Regulatory guidance and interpretation
            • Risk assessment and mitigation strategies  
            • KYC/AML compliance requirements
            • Sanctions screening procedures
            • Policy clarification and implementation
            • Regulatory reporting requirements
            
            Please describe your compliance question or scenario, and I'll provide 
            expert guidance based on current regulations and best practices.
            """.strip()
        )
        
        session.messages.append(welcome_msg)
        
        self.logger.info(f"Created new chat session: {session.session_id}")
        return session.session_id
        
    async def send_message(self, session_id: str, content: str,
                         question_type: Optional[QuestionType] = None,
                         urgency: Optional[UrgencyLevel] = None) -> ChatMessage:
        """Send message and get AI response"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session not found: {session_id}")
            
        session = self.active_sessions[session_id]
        start_time = datetime.now()
        
        # Add user message
        user_msg = ChatMessage(
            role="user",
            content=content,
            question_type=question_type,
            urgency=urgency
        )
        session.messages.append(user_msg)
        
        try:
            # Determine question type if not provided
            if not question_type:
                question_type = await self._classify_question(content)
                
            # Generate AI response
            response = await self._generate_response(
                session, content, question_type, urgency
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create assistant message
            assistant_msg = ChatMessage(
                role="assistant",
                content=response["answer"],
                question_type=question_type,
                sources=response.get("sources", []),
                confidence_score=response.get("confidence", 0.0),
                processing_time=processing_time
            )
            
            session.messages.append(assistant_msg)
            session.last_activity = datetime.now()
            
            self.logger.info(
                f"Generated response for session {session_id}: "
                f"{len(response['answer'])} chars in {processing_time:.2f}s"
            )
            
            return assistant_msg
            
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            self.logger.error(error_msg)
            
            error_response = ChatMessage(
                role="assistant",
                content=f"I apologize, but I encountered an error processing your question: {error_msg}. Please try rephrasing your question or contact support if the issue persists.",
                question_type=question_type,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
            session.messages.append(error_response)
            return error_response
            
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session"""
        return self.active_sessions.get(session_id)
        
    async def list_sessions(self, user_id: Optional[str] = None) -> List[ChatSession]:
        """List chat sessions for user"""
        sessions = list(self.active_sessions.values())
        
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
            
        # Sort by last activity
        sessions.sort(key=lambda s: s.last_activity, reverse=True)
        return sessions
        
    async def delete_session(self, session_id: str) -> bool:
        """Delete chat session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            self.logger.info(f"Deleted chat session: {session_id}")
            return True
        return False
        
    async def get_compliance_summary(self, session_id: str) -> Dict[str, Any]:
        """Generate compliance summary for session"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session not found: {session_id}")
            
        session = self.active_sessions[session_id]
        
        # Analyze session content
        user_messages = [msg for msg in session.messages if msg.role == "user"]
        assistant_messages = [msg for msg in session.messages if msg.role == "assistant"]
        
        # Extract key topics and recommendations
        topics = set()
        recommendations = []
        sources = []
        
        for msg in assistant_messages:
            if msg.question_type:
                topics.add(msg.question_type.value)
            recommendations.extend(self._extract_recommendations(msg.content))
            sources.extend(msg.sources)
            
        return {
            "session_id": session_id,
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "message_count": len(session.messages),
            "topics_covered": list(topics),
            "key_recommendations": recommendations[:10],  # Top 10
            "sources_referenced": len(set(s.get("doc_id", "") for s in sources if s.get("doc_id"))),
            "average_confidence": sum(msg.confidence_score for msg in assistant_messages) / len(assistant_messages) if assistant_messages else 0,
            "total_processing_time": sum(msg.processing_time for msg in assistant_messages)
        }
        
    async def _classify_question(self, content: str) -> QuestionType:
        """Classify question type based on content"""
        
        content_lower = content.lower()
        
        # Simple keyword-based classification
        if any(word in content_lower for word in ['sanction', 'embargo', 'blacklist', 'screening']):
            return QuestionType.SANCTIONS_CHECK
        elif any(word in content_lower for word in ['kyc', 'know your customer', 'customer due diligence', 'cdd']):
            return QuestionType.KYC_GUIDANCE
        elif any(word in content_lower for word in ['aml', 'anti-money laundering', 'suspicious activity']):
            return QuestionType.AML_GUIDANCE
        elif any(word in content_lower for word in ['risk', 'assessment', 'rating', 'mitigation']):
            return QuestionType.RISK_ASSESSMENT
        elif any(word in content_lower for word in ['report', 'filing', 'sar', 'ctr', 'suspicious transaction']):
            return QuestionType.REPORTING_REQUIREMENT
        elif any(word in content_lower for word in ['policy', 'procedure', 'implementation']):
            return QuestionType.POLICY_CLARIFICATION
        elif any(word in content_lower for word in ['regulation', 'requirement', 'law', 'fatf']):
            return QuestionType.REGULATORY_GUIDANCE
        else:
            return QuestionType.GENERAL_COMPLIANCE
            
    async def _generate_response(self, session: ChatSession, content: str,
                               question_type: QuestionType, 
                               urgency: Optional[UrgencyLevel]) -> Dict[str, Any]:
        """Generate AI response using RAGFlow"""
        
        try:
            # Get system prompt for question type
            system_prompt = self.system_prompts.get(
                question_type, 
                self.system_prompts[QuestionType.REGULATORY_GUIDANCE]
            )
            
            # Build context-aware prompt
            enhanced_prompt = self._build_enhanced_prompt(
                content, question_type, urgency, session, system_prompt
            )
            
            # Get response from knowledge manager
            knowledge_manager = await get_knowledge_manager()
            response = await knowledge_manager.get_compliance_guidance(
                enhanced_prompt,
                urgency.value if urgency else "medium"
            )
            
            return {
                "answer": response.get("guidance", "I'm sorry, I couldn't generate a response for your question."),
                "sources": response.get("sources", []),
                "confidence": response.get("confidence", 0.0)
            }
            
        except Exception as e:
            self.logger.error(f"Response generation failed: {e}")
            raise
            
    def _build_enhanced_prompt(self, content: str, question_type: QuestionType,
                             urgency: Optional[UrgencyLevel], session: ChatSession,
                             system_prompt: str) -> str:
        """Build enhanced prompt with context"""
        
        urgency_text = f"URGENCY: {urgency.value.upper()}" if urgency else ""
        
        # Get recent conversation context
        recent_messages = session.messages[-6:]  # Last 3 exchanges
        context_text = ""
        
        if len(recent_messages) > 2:
            context_text = "Previous conversation context:\n"
            for msg in recent_messages[:-1]:  # Exclude current message
                if msg.role in ["user", "assistant"]:
                    context_text += f"{msg.role}: {msg.content[:200]}...\n"
            context_text += "\n"
            
        enhanced_prompt = f"""
        {system_prompt}
        
        {urgency_text}
        
        {context_text}
        
        Current Question ({question_type.value}):
        {content}
        
        Please provide a comprehensive response that addresses the specific compliance question
        with practical guidance, relevant regulations, and actionable recommendations.
        """.strip()
        
        return enhanced_prompt
        
    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract key recommendations from response content"""
        
        recommendations = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for recommendation patterns
            if any(line.startswith(prefix) for prefix in ['•', '-', '1.', '2.', '3.', '4.', '5.']):
                if any(keyword in line.lower() for keyword in ['recommend', 'should', 'must', 'ensure', 'implement']):
                    recommendations.append(line)
                    
        return recommendations

# Service instance
compliance_chat = ComplianceChatService()

async def create_chat_session(user_id: Optional[str] = None, 
                            title: str = "Compliance Chat") -> str:
    """Create new compliance chat session"""
    return await compliance_chat.create_session(user_id, title)

async def send_chat_message(session_id: str, content: str,
                          question_type: Optional[QuestionType] = None,
                          urgency: Optional[UrgencyLevel] = None) -> ChatMessage:
    """Send message to compliance chat"""
    return await compliance_chat.send_message(session_id, content, question_type, urgency)

async def get_chat_session(session_id: str) -> Optional[ChatSession]:
    """Get chat session"""
    return await compliance_chat.get_session(session_id)

async def list_chat_sessions(user_id: Optional[str] = None) -> List[ChatSession]:
    """List chat sessions"""
    return await compliance_chat.list_sessions(user_id)

async def delete_chat_session(session_id: str) -> bool:
    """Delete chat session"""
    return await compliance_chat.delete_session(session_id)

async def get_session_summary(session_id: str) -> Dict[str, Any]:
    """Get compliance summary for session"""
    return await compliance_chat.get_compliance_summary(session_id)
