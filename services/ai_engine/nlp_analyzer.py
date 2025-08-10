"""
AI-Powered Risk Analysis Engine for Compliant.one
Advanced NLP, sentiment analysis, anomaly detection, and predictive analytics
"""

import logging
import re
import json
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
import asyncio

# NLP and ML imports (with fallbacks for missing packages)
try:
    import spacy
    from spacy import displacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import DBSCAN
    from sklearn.decomposition import PCA
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    # Create dummy classes to avoid NameError when sklearn is not available
    class TfidfVectorizer:
        def __init__(self, *args, **kwargs):
            pass
    
    class IsolationForest:
        def __init__(self, *args, **kwargs):
            pass
    
    HAS_SKLEARN = False

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk level classifications"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"

class EntityType(Enum):
    """Entity types for NLP extraction"""
    PERSON = "PERSON"
    ORGANIZATION = "ORG"
    LOCATION = "GPE"
    MONEY = "MONEY"
    DATE = "DATE"
    EVENT = "EVENT"

@dataclass
class ExtractedEntity:
    """Extracted entity from NLP processing"""
    text: str
    label: str
    confidence: float
    start: int
    end: int
    context: str

@dataclass
class RiskScore:
    """Risk score with breakdown"""
    overall_score: float
    sentiment_score: float
    entity_risk_score: float
    temporal_score: float
    network_score: float
    confidence: float
    risk_level: RiskLevel

class AIRiskAnalyzer:
    """Advanced AI-powered risk analysis engine"""
    
    def __init__(self, config):
        self.config = config
        self.nlp_model = None
        self.sentiment_analyzer = None
        self.anomaly_detector = None
        self.vectorizer = None
        self.entity_network = defaultdict(set)
        self.risk_patterns = self._load_risk_patterns()
        
        # Initialize AI models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize AI/ML models"""
        try:
            # Initialize spaCy NLP model
            if HAS_SPACY:
                try:
                    self.nlp_model = spacy.load("en_core_web_sm")
                    logger.info("SpaCy model loaded successfully")
                except OSError:
                    logger.warning("SpaCy en_core_web_sm model not found. Install with: python -m spacy download en_core_web_sm")
                    self.nlp_model = None
            
            # Initialize sentiment analysis
            if HAS_TRANSFORMERS:
                try:
                    self.sentiment_analyzer = pipeline(
                        "sentiment-analysis",
                        model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                        return_all_scores=True
                    )
                    logger.info("Sentiment analyzer loaded successfully")
                except Exception as e:
                    logger.warning(f"Could not load sentiment analyzer: {e}")
                    # Fallback to simpler model
                    try:
                        self.sentiment_analyzer = pipeline("sentiment-analysis")
                        logger.info("Fallback sentiment analyzer loaded")
                    except:
                        self.sentiment_analyzer = None
            
            # Initialize anomaly detection
            if HAS_SKLEARN:
                self.anomaly_detector = IsolationForest(
                    contamination=0.1,
                    random_state=42
                )
                self.vectorizer = TfidfVectorizer(
                    max_features=5000,
                    stop_words='english',
                    ngram_range=(1, 3)
                )
                logger.info("Anomaly detection models initialized")
            
        except Exception as e:
            logger.error(f"Model initialization error: {e}")
    
    def _load_risk_patterns(self) -> Dict[str, List[str]]:
        """Load risk-indicating patterns and keywords"""
        return {
            'corruption': [
                'bribery', 'kickback', 'embezzlement', 'fraud', 'money laundering',
                'corruption', 'graft', 'payoff', 'under the table', 'illicit payment',
                'slush fund', 'political donation', 'conflict of interest'
            ],
            'sanctions_evasion': [
                'sanctions evasion', 'embargo violation', 'trade restriction',
                'export control', 'dual-use', 'restricted entity', 'blocked person',
                'shell company', 'front company', 'beneficial ownership'
            ],
            'financial_crime': [
                'tax evasion', 'tax haven', 'offshore account', 'shell company',
                'structured transaction', 'smurfing', 'layering', 'placement',
                'hawala', 'correspondent banking', 'trade-based money laundering'
            ],
            'terrorist_financing': [
                'terrorist financing', 'material support', 'charity fraud',
                'hawala', 'value transfer', 'bulk cash smuggling', 'trade-based'
            ],
            'pep_indicators': [
                'politically exposed person', 'government official', 'public official',
                'minister', 'ambassador', 'judge', 'military officer', 'party official',
                'state-owned enterprise', 'government contract'
            ],
            'adverse_media': [
                'investigation', 'alleged', 'accused', 'charged', 'indicted',
                'prosecution', 'lawsuit', 'settlement', 'fine', 'penalty',
                'misconduct', 'violation', 'breach', 'scandal'
            ]
        }
    
    async def analyze_text(self, text: str, source_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive AI analysis of text content
        
        Args:
            text: Text content to analyze
            source_metadata: Metadata about the source
            
        Returns:
            Complete analysis results
        """
        if not text or not text.strip():
            return self._empty_analysis()
        
        logger.debug(f"Analyzing text: {text[:100]}...")
        
        # Parallel analysis tasks
        tasks = [
            self._extract_entities(text),
            self._analyze_sentiment(text),
            self._detect_risk_patterns(text),
            self._extract_relationships(text)
        ]
        
        try:
            entities, sentiment, risk_patterns, relationships = await asyncio.gather(*tasks)
            
            # Calculate comprehensive risk score
            risk_score = self._calculate_risk_score(
                text, entities, sentiment, risk_patterns, relationships, source_metadata
            )
            
            # Detect anomalies
            anomalies = await self._detect_anomalies(text, entities, source_metadata)
            
            return {
                'text': text[:500],  # Truncated for storage
                'entities': entities,
                'sentiment': sentiment,
                'risk_patterns': risk_patterns,
                'relationships': relationships,
                'risk_score': risk_score.__dict__,
                'anomalies': anomalies,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'source_metadata': source_metadata or {}
            }
            
        except Exception as e:
            logger.error(f"Text analysis error: {e}")
            return self._empty_analysis()
    
    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities using NLP"""
        if not self.nlp_model:
            return self._fallback_entity_extraction(text)
        
        try:
            doc = self.nlp_model(text)
            entities = []
            
            for ent in doc.ents:
                entity = {
                    'text': ent.text,
                    'label': ent.label_,
                    'description': spacy.explain(ent.label_),
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': getattr(ent, 'kb_score_', 0.8),  # Default confidence
                    'context': text[max(0, ent.start_char-50):ent.end_char+50]
                }
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
            return self._fallback_entity_extraction(text)
    
    def _fallback_entity_extraction(self, text: str) -> List[Dict[str, Any]]:
        """Fallback entity extraction using regex patterns"""
        entities = []
        
        # Basic patterns for common entities
        patterns = {
            'PERSON': [
                r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # John Doe
                r'\b[A-Z][a-z]+, [A-Z][a-z]+\b'  # Doe, John
            ],
            'ORG': [
                r'\b[A-Z][a-zA-Z\s]+ (Inc|Corp|LLC|Ltd|Company|Group|Bank|Fund)\b',
                r'\b[A-Z]{2,} [A-Z][a-zA-Z\s]+\b'  # Acronym + name
            ],
            'MONEY': [
                r'\$[\d,]+\.?\d*\s?(million|billion|thousand)?',
                r'€[\d,]+\.?\d*\s?(million|billion|thousand)?',
                r'£[\d,]+\.?\d*\s?(million|billion|thousand)?'
            ],
            'GPE': [
                r'\b[A-Z][a-z]+ (City|State|Country|Province|Territory)\b'
            ]
        }
        
        for label, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        'text': match.group(),
                        'label': label,
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.6,  # Lower confidence for regex
                        'context': text[max(0, match.start()-50):match.end()+50]
                    })
        
        return entities
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        if not self.sentiment_analyzer:
            return self._fallback_sentiment_analysis(text)
        
        try:
            # Handle long text by chunking
            chunks = [text[i:i+512] for i in range(0, len(text), 512)]
            all_scores = []
            
            for chunk in chunks[:5]:  # Limit to first 5 chunks
                if chunk.strip():
                    result = self.sentiment_analyzer(chunk)
                    all_scores.extend(result)
            
            if not all_scores:
                return {'sentiment': 'neutral', 'confidence': 0.0, 'scores': []}
            
            # Aggregate scores
            if isinstance(all_scores[0], list):
                # Multiple scores per chunk
                sentiment_scores = defaultdict(list)
                for chunk_scores in all_scores:
                    for score in chunk_scores:
                        sentiment_scores[score['label']].append(score['score'])
            else:
                # Single score per chunk
                sentiment_scores = defaultdict(list)
                for score in all_scores:
                    sentiment_scores[score['label']].append(score['score'])
            
            # Calculate average scores
            avg_scores = {}
            for label, scores in sentiment_scores.items():
                avg_scores[label] = sum(scores) / len(scores)
            
            # Determine overall sentiment
            best_sentiment = max(avg_scores, key=avg_scores.get)
            confidence = avg_scores[best_sentiment]
            
            return {
                'sentiment': best_sentiment.lower(),
                'confidence': confidence,
                'scores': avg_scores,
                'analysis_method': 'transformer'
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return self._fallback_sentiment_analysis(text)
    
    def _fallback_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback sentiment analysis using keyword matching"""
        positive_words = ['good', 'excellent', 'positive', 'success', 'growth', 'profit', 'win']
        negative_words = ['bad', 'terrible', 'negative', 'loss', 'decline', 'fraud', 'scandal', 'corruption']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return {'sentiment': 'neutral', 'confidence': 0.0, 'scores': {}}
        
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        
        if negative_ratio > positive_ratio:
            sentiment = 'negative'
            confidence = min(negative_ratio * 10, 1.0)
        elif positive_ratio > negative_ratio:
            sentiment = 'positive'
            confidence = min(positive_ratio * 10, 1.0)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'scores': {'positive': positive_ratio, 'negative': negative_ratio},
            'analysis_method': 'keyword'
        }
    
    async def _detect_risk_patterns(self, text: str) -> Dict[str, Any]:
        """Detect risk-indicating patterns in text"""
        text_lower = text.lower()
        detected_patterns = {}
        
        for risk_category, patterns in self.risk_patterns.items():
            matches = []
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    # Find all occurrences
                    start = 0
                    while True:
                        pos = text_lower.find(pattern.lower(), start)
                        if pos == -1:
                            break
                        matches.append({
                            'pattern': pattern,
                            'position': pos,
                            'context': text[max(0, pos-50):pos+len(pattern)+50]
                        })
                        start = pos + 1
            
            if matches:
                detected_patterns[risk_category] = {
                    'count': len(matches),
                    'matches': matches,
                    'risk_weight': self._get_risk_weight(risk_category)
                }
        
        return detected_patterns
    
    def _get_risk_weight(self, risk_category: str) -> float:
        """Get risk weight for different categories"""
        weights = {
            'corruption': 0.9,
            'sanctions_evasion': 0.95,
            'financial_crime': 0.85,
            'terrorist_financing': 1.0,
            'pep_indicators': 0.7,
            'adverse_media': 0.6
        }
        return weights.get(risk_category, 0.5)
    
    async def _extract_relationships(self, text: str) -> List[Dict[str, Any]]:
        """Extract relationships between entities"""
        if not self.nlp_model:
            return []
        
        try:
            doc = self.nlp_model(text)
            relationships = []
            
            # Simple relationship extraction based on dependency parsing
            for token in doc:
                if token.dep_ in ['nsubj', 'dobj', 'pobj'] and token.head.pos_ == 'VERB':
                    subject = token.text
                    verb = token.head.text
                    
                    # Find object
                    obj = None
                    for child in token.head.children:
                        if child.dep_ in ['dobj', 'pobj'] and child != token:
                            obj = child.text
                            break
                    
                    if obj:
                        relationships.append({
                            'subject': subject,
                            'relation': verb,
                            'object': obj,
                            'confidence': 0.7,
                            'context': str(token.sent)
                        })
            
            return relationships
            
        except Exception as e:
            logger.error(f"Relationship extraction error: {e}")
            return []
    
    def _calculate_risk_score(self, 
                            text: str,
                            entities: List[Dict],
                            sentiment: Dict,
                            risk_patterns: Dict,
                            relationships: List[Dict],
                            source_metadata: Dict = None) -> RiskScore:
        """Calculate comprehensive risk score"""
        
        # Base score
        base_score = 0.0
        
        # Sentiment contribution (negative sentiment increases risk)
        sentiment_score = 0.0
        if sentiment['sentiment'] == 'negative':
            sentiment_score = sentiment['confidence'] * 0.3
        elif sentiment['sentiment'] == 'positive':
            sentiment_score = -sentiment['confidence'] * 0.1  # Slightly lower risk
        
        # Entity risk contribution
        entity_risk_score = 0.0
        high_risk_entities = ['PERSON', 'ORG', 'MONEY']
        for entity in entities:
            if entity['label'] in high_risk_entities:
                entity_risk_score += 0.1 * entity['confidence']
        
        # Risk pattern contribution
        pattern_score = 0.0
        for category, data in risk_patterns.items():
            weight = data['risk_weight']
            count = min(data['count'], 5)  # Cap at 5 occurrences
            pattern_score += weight * (count / 5) * 0.4
        
        # Temporal score (recent events are higher risk)
        temporal_score = 0.0
        if source_metadata and 'published_date' in source_metadata:
            try:
                pub_date = datetime.fromisoformat(source_metadata['published_date'].replace('Z', '+00:00'))
                days_ago = (datetime.utcnow() - pub_date).days
                if days_ago <= 1:
                    temporal_score = 0.2
                elif days_ago <= 7:
                    temporal_score = 0.1
                elif days_ago <= 30:
                    temporal_score = 0.05
            except:
                pass
        
        # Network score (placeholder for relationship analysis)
        network_score = len(relationships) * 0.02  # Small contribution
        
        # Calculate overall score
        overall_score = min(
            base_score + sentiment_score + entity_risk_score + pattern_score + temporal_score + network_score,
            1.0
        )
        
        # Confidence calculation
        confidence = min(
            (sentiment['confidence'] + 
             (sum(e['confidence'] for e in entities) / max(len(entities), 1)) +
             (0.8 if risk_patterns else 0.2)) / 3,
            1.0
        )
        
        # Risk level categorization
        if overall_score >= 0.8:
            risk_level = RiskLevel.CRITICAL
        elif overall_score >= 0.6:
            risk_level = RiskLevel.HIGH
        elif overall_score >= 0.4:
            risk_level = RiskLevel.MEDIUM
        elif overall_score >= 0.2:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.NEGLIGIBLE
        
        return RiskScore(
            overall_score=overall_score,
            sentiment_score=sentiment_score,
            entity_risk_score=entity_risk_score,
            temporal_score=temporal_score,
            network_score=network_score,
            confidence=confidence,
            risk_level=risk_level
        )
    
    async def _detect_anomalies(self, text: str, entities: List[Dict], source_metadata: Dict = None) -> Dict[str, Any]:
        """Detect anomalies and unusual patterns"""
        anomalies = {
            'detected': False,
            'anomaly_types': [],
            'confidence': 0.0,
            'details': []
        }
        
        # Text length anomaly
        if len(text) > 10000:  # Very long text
            anomalies['anomaly_types'].append('excessive_length')
            anomalies['details'].append({
                'type': 'excessive_length',
                'description': f'Text length ({len(text)}) is unusually long',
                'confidence': 0.7
            })
        
        # Entity density anomaly
        entity_density = len(entities) / max(len(text.split()), 1)
        if entity_density > 0.3:  # High entity density
            anomalies['anomaly_types'].append('high_entity_density')
            anomalies['details'].append({
                'type': 'high_entity_density',
                'description': f'High entity density ({entity_density:.2f})',
                'confidence': 0.6
            })
        
        # Repetitive content detection
        words = text.lower().split()
        word_counts = Counter(words)
        most_common = word_counts.most_common(1)
        if most_common and most_common[0][1] > len(words) * 0.1:  # Word appears >10% of time
            anomalies['anomaly_types'].append('repetitive_content')
            anomalies['details'].append({
                'type': 'repetitive_content',
                'description': f'Word "{most_common[0][0]}" appears {most_common[0][1]} times',
                'confidence': 0.8
            })
        
        anomalies['detected'] = len(anomalies['anomaly_types']) > 0
        if anomalies['detected']:
            anomalies['confidence'] = sum(d['confidence'] for d in anomalies['details']) / len(anomalies['details'])
        
        return anomalies
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'text': '',
            'entities': [],
            'sentiment': {'sentiment': 'neutral', 'confidence': 0.0, 'scores': {}},
            'risk_patterns': {},
            'relationships': [],
            'risk_score': RiskScore(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, RiskLevel.NEGLIGIBLE).__dict__,
            'anomalies': {'detected': False, 'anomaly_types': [], 'confidence': 0.0, 'details': []},
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'source_metadata': {}
        }
    
    async def batch_analyze(self, texts: List[str], metadata_list: List[Dict] = None) -> List[Dict[str, Any]]:
        """Analyze multiple texts in batch"""
        if metadata_list is None:
            metadata_list = [{}] * len(texts)
        
        tasks = [
            self.analyze_text(text, metadata)
            for text, metadata in zip(texts, metadata_list)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch analysis error: {result}")
                valid_results.append(self._empty_analysis())
            else:
                valid_results.append(result)
        
        return valid_results
    
    def update_entity_network(self, entities: List[Dict], relationships: List[Dict]):
        """Update entity relationship network"""
        # Build entity network for future network analysis
        for entity in entities:
            entity_text = entity['text'].lower()
            self.entity_network[entity_text] = self.entity_network.get(entity_text, set())
        
        # Add relationships
        for rel in relationships:
            subject = rel['subject'].lower()
            obj = rel['object'].lower()
            self.entity_network[subject].add(obj)
            self.entity_network[obj].add(subject)
    
    def get_network_analysis(self, entity_name: str) -> Dict[str, Any]:
        """Get network analysis for a specific entity"""
        entity_lower = entity_name.lower()
        
        if entity_lower not in self.entity_network:
            return {'entity': entity_name, 'connections': [], 'centrality': 0.0}
        
        connections = list(self.entity_network[entity_lower])
        
        # Simple centrality measure
        centrality = len(connections) / max(len(self.entity_network), 1)
        
        return {
            'entity': entity_name,
            'connections': connections,
            'centrality': centrality,
            'connection_count': len(connections)
        }
