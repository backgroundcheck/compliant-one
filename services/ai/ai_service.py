"""
AI Service Architecture for Compliant-One Platform
Core AI/ML infrastructure supporting advanced compliance automation
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import asyncio
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod

# Optional AI/ML imports with fallbacks
try:
    import sklearn
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import DBSCAN
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import torch
    import transformers
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

class AIServiceBase(ABC):
    """Base class for all AI services"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_initialized = False
        self.model = None
        
    @abstractmethod
    async def initialize(self):
        """Initialize the AI service"""
        pass
    
    @abstractmethod
    async def process(self, data: Any) -> Dict:
        """Process data through the AI service"""
        pass
    
    def get_status(self) -> Dict:
        """Get service status"""
        return {
            'service': self.__class__.__name__,
            'initialized': self.is_initialized,
            'model_loaded': self.model is not None,
            'config': self.config
        }

class AnomalyDetectionService(AIServiceBase):
    """AI-powered anomaly detection for compliance risks"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.scaler = None
        self.anomaly_threshold = config.get('anomaly_threshold', 0.1) if config else 0.1
        self.feature_columns = [
            'transaction_amount', 'transaction_frequency', 'risk_score',
            'sanctions_hits', 'adverse_media_score', 'network_centrality'
        ]
    
    async def initialize(self):
        """Initialize anomaly detection models"""
        try:
            if not SKLEARN_AVAILABLE:
                self.logger.warning("scikit-learn not available, using mock anomaly detection")
                self.model = MockAnomalyDetector()
            else:
                # Initialize Isolation Forest for anomaly detection
                self.model = IsolationForest(
                    contamination=self.anomaly_threshold,
                    random_state=42,
                    n_estimators=100
                )
                self.scaler = StandardScaler()
            
            self.is_initialized = True
            self.logger.info("Anomaly detection service initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize anomaly detection: {e}")
            self.model = MockAnomalyDetector()
            self.is_initialized = True
    
    async def process(self, data: Union[Dict, pd.DataFrame]) -> Dict:
        """Detect anomalies in compliance data"""
        try:
            if isinstance(data, dict):
                # Single record
                features = self._extract_features([data])
            elif isinstance(data, pd.DataFrame):
                # Multiple records
                features = self._extract_features(data.to_dict('records'))
            else:
                features = self._extract_features(data)
            
            if len(features) == 0:
                return {'anomalies': [], 'total_processed': 0}
            
            # Detect anomalies
            anomaly_scores = await self._detect_anomalies(features)
            
            # Process results
            results = []
            for i, (record, score, is_anomaly) in enumerate(zip(data if isinstance(data, list) else [data], anomaly_scores['scores'], anomaly_scores['predictions'])):
                if is_anomaly:
                    results.append({
                        'record_id': i,
                        'anomaly_score': float(score),
                        'anomaly_type': self._classify_anomaly_type(record, score),
                        'risk_level': self._calculate_risk_level(score),
                        'explanation': self._generate_explanation(record, score),
                        'timestamp': datetime.now().isoformat(),
                        'data': record
                    })
            
            return {
                'anomalies': results,
                'total_processed': len(features),
                'anomaly_rate': len(results) / len(features) if len(features) > 0 else 0,
                'model_info': {
                    'threshold': self.anomaly_threshold,
                    'features_used': self.feature_columns
                }
            }
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return {'error': str(e), 'anomalies': []}
    
    def _extract_features(self, data: List[Dict]) -> np.ndarray:
        """Extract numerical features from data"""
        if not SKLEARN_AVAILABLE:
            return np.random.random((len(data), len(self.feature_columns)))
        
        features = []
        for record in data:
            feature_vector = []
            for col in self.feature_columns:
                value = record.get(col, 0)
                if isinstance(value, (int, float)):
                    feature_vector.append(float(value))
                else:
                    # Convert non-numeric to numeric
                    feature_vector.append(self._convert_to_numeric(value))
            features.append(feature_vector)
        
        return np.array(features)
    
    def _convert_to_numeric(self, value: Any) -> float:
        """Convert various data types to numeric values"""
        if value is None:
            return 0.0
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, str):
            # Simple string to numeric conversion
            return float(len(value)) / 10.0
        return 0.0
    
    async def _detect_anomalies(self, features: np.ndarray) -> Dict:
        """Run anomaly detection on features"""
        if not SKLEARN_AVAILABLE or isinstance(self.model, MockAnomalyDetector):
            # Mock detection for demo
            predictions = np.random.choice([0, 1], size=len(features), p=[0.9, 0.1])
            scores = np.random.random(len(features))
            return {'predictions': predictions == 1, 'scores': scores}
        
        # Scale features
        if self.scaler is None:
            features_scaled = self.scaler.fit_transform(features)
        else:
            features_scaled = self.scaler.transform(features)
        
        # Detect anomalies
        predictions = self.model.predict(features_scaled)  # -1 for anomaly, 1 for normal
        scores = self.model.decision_function(features_scaled)
        
        # Convert to boolean (True for anomaly)
        is_anomaly = predictions == -1
        
        return {'predictions': is_anomaly, 'scores': scores}
    
    def _classify_anomaly_type(self, record: Dict, score: float) -> str:
        """Classify the type of anomaly detected"""
        # Simple rule-based classification
        if record.get('sanctions_hits', 0) > 0:
            return 'sanctions_risk'
        elif record.get('adverse_media_score', 0) > 0.7:
            return 'adverse_media_risk'
        elif record.get('transaction_amount', 0) > 100000:
            return 'high_value_transaction'
        elif score < -0.5:
            return 'severe_anomaly'
        else:
            return 'general_anomaly'
    
    def _calculate_risk_level(self, score: float) -> str:
        """Calculate risk level based on anomaly score"""
        if score < -0.7:
            return 'CRITICAL'
        elif score < -0.4:
            return 'HIGH'
        elif score < -0.2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_explanation(self, record: Dict, score: float) -> str:
        """Generate human-readable explanation for the anomaly"""
        explanations = []
        
        if record.get('sanctions_hits', 0) > 0:
            explanations.append(f"Sanctions match detected ({record['sanctions_hits']} hits)")
        
        if record.get('adverse_media_score', 0) > 0.5:
            explanations.append(f"High adverse media score ({record['adverse_media_score']:.2f})")
        
        if record.get('transaction_amount', 0) > 50000:
            explanations.append(f"Large transaction amount ({record['transaction_amount']:,})")
        
        if not explanations:
            explanations.append(f"Statistical anomaly detected (score: {score:.3f})")
        
        return "; ".join(explanations)

class PredictiveAnalyticsService(AIServiceBase):
    """Predictive analytics for risk forecasting"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.forecast_horizon = config.get('forecast_horizon', 30) if config else 30  # days
        self.confidence_threshold = config.get('confidence_threshold', 0.8) if config else 0.8
    
    async def initialize(self):
        """Initialize predictive models"""
        try:
            if not SKLEARN_AVAILABLE:
                self.logger.warning("scikit-learn not available, using mock predictions")
                self.model = MockPredictiveModel()
            else:
                # Initialize Random Forest for risk prediction
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                    max_depth=10
                )
            
            self.is_initialized = True
            self.logger.info("Predictive analytics service initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize predictive analytics: {e}")
            self.model = MockPredictiveModel()
            self.is_initialized = True
    
    async def process(self, data: Dict) -> Dict:
        """Generate risk predictions"""
        try:
            prediction_type = data.get('type', 'risk_forecast')
            
            if prediction_type == 'risk_forecast':
                return await self._generate_risk_forecast(data)
            elif prediction_type == 'trend_analysis':
                return await self._analyze_trends(data)
            elif prediction_type == 'entity_risk':
                return await self._predict_entity_risk(data)
            else:
                return {'error': f'Unknown prediction type: {prediction_type}'}
                
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            return {'error': str(e)}
    
    async def _generate_risk_forecast(self, data: Dict) -> Dict:
        """Generate risk forecast for the specified horizon"""
        # Mock implementation for demonstration
        base_risk = data.get('current_risk_score', 0.5)
        
        forecast_points = []
        for day in range(1, self.forecast_horizon + 1):
            # Simple trend simulation
            trend_factor = 1 + (np.random.random() - 0.5) * 0.1
            predicted_risk = min(1.0, max(0.0, base_risk * trend_factor))
            confidence = max(0.5, 1.0 - (day / self.forecast_horizon) * 0.5)
            
            forecast_points.append({
                'day': day,
                'date': (datetime.now() + timedelta(days=day)).isoformat()[:10],
                'predicted_risk': round(predicted_risk, 3),
                'confidence': round(confidence, 3),
                'risk_level': self._risk_score_to_level(predicted_risk)
            })
        
        return {
            'forecast': forecast_points,
            'summary': {
                'horizon_days': self.forecast_horizon,
                'average_risk': round(np.mean([p['predicted_risk'] for p in forecast_points]), 3),
                'trend': self._calculate_trend(forecast_points),
                'high_risk_days': len([p for p in forecast_points if p['predicted_risk'] > 0.7])
            }
        }
    
    async def _analyze_trends(self, data: Dict) -> Dict:
        """Analyze historical trends and patterns"""
        historical_data = data.get('historical_data', [])
        
        if not historical_data:
            return {'error': 'No historical data provided'}
        
        # Simple trend analysis
        risk_scores = [item.get('risk_score', 0) for item in historical_data]
        
        if len(risk_scores) < 2:
            return {'error': 'Insufficient data for trend analysis'}
        
        # Calculate basic statistics
        trend_slope = (risk_scores[-1] - risk_scores[0]) / len(risk_scores)
        volatility = np.std(risk_scores) if len(risk_scores) > 1 else 0
        
        return {
            'trend_analysis': {
                'direction': 'increasing' if trend_slope > 0.01 else 'decreasing' if trend_slope < -0.01 else 'stable',
                'slope': round(trend_slope, 4),
                'volatility': round(volatility, 3),
                'current_level': risk_scores[-1] if risk_scores else 0,
                'average_level': round(np.mean(risk_scores), 3),
                'data_points': len(risk_scores)
            },
            'patterns': self._identify_patterns(risk_scores)
        }
    
    async def _predict_entity_risk(self, data: Dict) -> Dict:
        """Predict future risk for a specific entity"""
        entity_data = data.get('entity_data', {})
        
        # Extract features for prediction
        features = {
            'sanctions_history': entity_data.get('sanctions_hits', 0),
            'adverse_media_count': entity_data.get('adverse_media_count', 0),
            'transaction_volume': entity_data.get('transaction_volume', 0),
            'jurisdiction_risk': entity_data.get('jurisdiction_risk', 0.5),
            'business_type_risk': entity_data.get('business_type_risk', 0.5)
        }
        
        # Simple rule-based prediction (would be ML model in production)
        risk_factors = []
        total_risk = 0
        
        if features['sanctions_history'] > 0:
            risk_factors.append('Previous sanctions exposure')
            total_risk += 0.4
        
        if features['adverse_media_count'] > 5:
            risk_factors.append('High adverse media coverage')
            total_risk += 0.3
        
        if features['transaction_volume'] > 1000000:
            risk_factors.append('High transaction volume')
            total_risk += 0.2
        
        if features['jurisdiction_risk'] > 0.7:
            risk_factors.append('High-risk jurisdiction')
            total_risk += 0.3
        
        predicted_risk = min(1.0, total_risk)
        
        return {
            'entity_prediction': {
                'predicted_risk_score': round(predicted_risk, 3),
                'risk_level': self._risk_score_to_level(predicted_risk),
                'confidence': 0.85,  # Mock confidence
                'risk_factors': risk_factors,
                'recommendation': self._generate_recommendation(predicted_risk),
                'features_analyzed': features
            }
        }
    
    def _risk_score_to_level(self, score: float) -> str:
        """Convert risk score to categorical level"""
        if score >= 0.8:
            return 'CRITICAL'
        elif score >= 0.6:
            return 'HIGH'
        elif score >= 0.4:
            return 'MEDIUM'
        elif score >= 0.2:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _calculate_trend(self, forecast_points: List[Dict]) -> str:
        """Calculate overall trend from forecast points"""
        if len(forecast_points) < 2:
            return 'unknown'
        
        first_half_avg = np.mean([p['predicted_risk'] for p in forecast_points[:len(forecast_points)//2]])
        second_half_avg = np.mean([p['predicted_risk'] for p in forecast_points[len(forecast_points)//2:]])
        
        if second_half_avg > first_half_avg * 1.05:
            return 'increasing'
        elif second_half_avg < first_half_avg * 0.95:
            return 'decreasing'
        else:
            return 'stable'
    
    def _identify_patterns(self, risk_scores: List[float]) -> List[Dict]:
        """Identify patterns in historical risk scores"""
        patterns = []
        
        if len(risk_scores) >= 3:
            # Check for consecutive increases
            increases = 0
            decreases = 0
            for i in range(1, len(risk_scores)):
                if risk_scores[i] > risk_scores[i-1]:
                    increases += 1
                elif risk_scores[i] < risk_scores[i-1]:
                    decreases += 1
            
            if increases > len(risk_scores) * 0.7:
                patterns.append({
                    'type': 'consistent_increase',
                    'description': 'Risk has been consistently increasing',
                    'strength': 'strong' if increases > len(risk_scores) * 0.8 else 'moderate'
                })
            
            if decreases > len(risk_scores) * 0.7:
                patterns.append({
                    'type': 'consistent_decrease',
                    'description': 'Risk has been consistently decreasing',
                    'strength': 'strong' if decreases > len(risk_scores) * 0.8 else 'moderate'
                })
        
        return patterns
    
    def _generate_recommendation(self, risk_score: float) -> str:
        """Generate recommendation based on predicted risk"""
        if risk_score >= 0.8:
            return "Immediate investigation required. Consider enhanced due diligence and potential account restrictions."
        elif risk_score >= 0.6:
            return "Enhanced monitoring recommended. Review transaction patterns and update risk assessment."
        elif risk_score >= 0.4:
            return "Standard monitoring sufficient. Periodic review recommended."
        else:
            return "Low risk profile. Standard compliance procedures apply."

class NetworkAnalysisService(AIServiceBase):
    """Advanced network analysis for relationship mapping"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.max_depth = config.get('max_depth', 3) if config else 3
        self.centrality_threshold = config.get('centrality_threshold', 0.1) if config else 0.1
    
    async def initialize(self):
        """Initialize network analysis capabilities"""
        try:
            # For now, we'll use a simple implementation
            # In production, would use NetworkX or similar
            self.is_initialized = True
            self.logger.info("Network analysis service initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize network analysis: {e}")
            self.is_initialized = True
    
    async def process(self, data: Dict) -> Dict:
        """Analyze network relationships and patterns"""
        try:
            analysis_type = data.get('type', 'relationship_mapping')
            
            if analysis_type == 'relationship_mapping':
                return await self._map_relationships(data)
            elif analysis_type == 'centrality_analysis':
                return await self._analyze_centrality(data)
            elif analysis_type == 'suspicious_patterns':
                return await self._detect_suspicious_patterns(data)
            else:
                return {'error': f'Unknown analysis type: {analysis_type}'}
                
        except Exception as e:
            self.logger.error(f"Network analysis failed: {e}")
            return {'error': str(e)}
    
    async def _map_relationships(self, data: Dict) -> Dict:
        """Map entity relationships and connections"""
        entity_id = data.get('entity_id')
        relationships = data.get('relationships', [])
        
        # Build relationship map
        relationship_map = {
            'center_entity': entity_id,
            'direct_connections': [],
            'indirect_connections': [],
            'relationship_types': {},
            'risk_propagation': {}
        }
        
        # Process direct relationships
        for rel in relationships:
            if rel.get('source') == entity_id or rel.get('target') == entity_id:
                connected_entity = rel.get('target') if rel.get('source') == entity_id else rel.get('source')
                relationship_map['direct_connections'].append({
                    'entity_id': connected_entity,
                    'relationship_type': rel.get('type', 'unknown'),
                    'strength': rel.get('strength', 0.5),
                    'risk_score': rel.get('risk_score', 0.0)
                })
                
                # Track relationship types
                rel_type = rel.get('type', 'unknown')
                if rel_type not in relationship_map['relationship_types']:
                    relationship_map['relationship_types'][rel_type] = 0
                relationship_map['relationship_types'][rel_type] += 1
        
        # Calculate network statistics
        relationship_map['statistics'] = {
            'total_direct_connections': len(relationship_map['direct_connections']),
            'average_connection_strength': np.mean([c['strength'] for c in relationship_map['direct_connections']]) if relationship_map['direct_connections'] else 0,
            'highest_risk_connection': max([c['risk_score'] for c in relationship_map['direct_connections']], default=0),
            'network_density': len(relationship_map['direct_connections']) / max(1, len(relationships))
        }
        
        return relationship_map
    
    async def _analyze_centrality(self, data: Dict) -> Dict:
        """Analyze entity centrality in the network"""
        entities = data.get('entities', [])
        relationships = data.get('relationships', [])
        
        # Simple centrality calculation
        centrality_scores = {}
        
        for entity in entities:
            entity_id = entity.get('id')
            # Count connections
            connections = len([r for r in relationships if r.get('source') == entity_id or r.get('target') == entity_id])
            
            # Simple degree centrality
            centrality_scores[entity_id] = {
                'degree_centrality': connections / max(1, len(entities) - 1),
                'connection_count': connections,
                'risk_adjusted_centrality': connections * entity.get('risk_score', 0.5)
            }
        
        # Identify high centrality entities
        high_centrality = {
            entity_id: scores for entity_id, scores in centrality_scores.items()
            if scores['degree_centrality'] > self.centrality_threshold
        }
        
        return {
            'centrality_analysis': centrality_scores,
            'high_centrality_entities': high_centrality,
            'network_metrics': {
                'total_entities': len(entities),
                'total_relationships': len(relationships),
                'average_centrality': np.mean([s['degree_centrality'] for s in centrality_scores.values()]) if centrality_scores else 0,
                'max_centrality': max([s['degree_centrality'] for s in centrality_scores.values()], default=0)
            }
        }
    
    async def _detect_suspicious_patterns(self, data: Dict) -> Dict:
        """Detect suspicious patterns in network relationships"""
        relationships = data.get('relationships', [])
        entities = data.get('entities', [])
        
        suspicious_patterns = []
        
        # Pattern 1: Circular relationships (potential shell companies)
        circular_patterns = self._find_circular_relationships(relationships)
        if circular_patterns:
            suspicious_patterns.extend(circular_patterns)
        
        # Pattern 2: Hub entities with many connections to high-risk entities
        hub_patterns = self._find_hub_patterns(relationships, entities)
        if hub_patterns:
            suspicious_patterns.extend(hub_patterns)
        
        # Pattern 3: Isolated clusters (potential money laundering networks)
        cluster_patterns = self._find_isolated_clusters(relationships, entities)
        if cluster_patterns:
            suspicious_patterns.extend(cluster_patterns)
        
        return {
            'suspicious_patterns': suspicious_patterns,
            'pattern_count': len(suspicious_patterns),
            'risk_assessment': self._assess_pattern_risk(suspicious_patterns)
        }
    
    def _find_circular_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """Find circular relationship patterns"""
        patterns = []
        
        # Simple 3-entity circle detection
        entities_graph = {}
        for rel in relationships:
            source = rel.get('source')
            target = rel.get('target')
            
            if source not in entities_graph:
                entities_graph[source] = []
            entities_graph[source].append(target)
        
        # Look for circles of length 3
        for entity_a in entities_graph:
            for entity_b in entities_graph.get(entity_a, []):
                for entity_c in entities_graph.get(entity_b, []):
                    if entity_c in entities_graph.get(entity_a, []):
                        patterns.append({
                            'type': 'circular_relationship',
                            'entities': [entity_a, entity_b, entity_c],
                            'description': 'Circular relationship pattern detected',
                            'risk_level': 'HIGH'
                        })
        
        return patterns
    
    def _find_hub_patterns(self, relationships: List[Dict], entities: List[Dict]) -> List[Dict]:
        """Find hub entities with suspicious connection patterns"""
        patterns = []
        
        # Count connections per entity
        connection_counts = {}
        for rel in relationships:
            source = rel.get('source')
            target = rel.get('target')
            
            connection_counts[source] = connection_counts.get(source, 0) + 1
            connection_counts[target] = connection_counts.get(target, 0) + 1
        
        # Find entities with many connections to high-risk entities
        entity_risk_map = {e.get('id'): e.get('risk_score', 0) for e in entities}
        
        for entity_id, count in connection_counts.items():
            if count > 5:  # Threshold for "many" connections
                connected_entities = []
                for rel in relationships:
                    if rel.get('source') == entity_id:
                        connected_entities.append(rel.get('target'))
                    elif rel.get('target') == entity_id:
                        connected_entities.append(rel.get('source'))
                
                high_risk_connections = sum(1 for e in connected_entities if entity_risk_map.get(e, 0) > 0.7)
                
                if high_risk_connections > 2:
                    patterns.append({
                        'type': 'suspicious_hub',
                        'entity': entity_id,
                        'total_connections': count,
                        'high_risk_connections': high_risk_connections,
                        'description': f'Hub entity with {high_risk_connections} high-risk connections',
                        'risk_level': 'HIGH' if high_risk_connections > 3 else 'MEDIUM'
                    })
        
        return patterns
    
    def _find_isolated_clusters(self, relationships: List[Dict], entities: List[Dict]) -> List[Dict]:
        """Find isolated clusters that might indicate suspicious networks"""
        # This is a simplified implementation
        # In production, would use proper graph clustering algorithms
        patterns = []
        
        # For now, just identify entities with very few external connections
        # but high internal connectivity (potential money laundering rings)
        
        return patterns  # Placeholder for complex clustering logic
    
    def _assess_pattern_risk(self, patterns: List[Dict]) -> Dict:
        """Assess overall risk based on detected patterns"""
        if not patterns:
            return {'overall_risk': 'LOW', 'risk_score': 0.1}
        
        high_risk_patterns = len([p for p in patterns if p.get('risk_level') == 'HIGH'])
        medium_risk_patterns = len([p for p in patterns if p.get('risk_level') == 'MEDIUM'])
        
        risk_score = min(1.0, (high_risk_patterns * 0.3 + medium_risk_patterns * 0.2))
        
        if risk_score > 0.7:
            risk_level = 'CRITICAL'
        elif risk_score > 0.5:
            risk_level = 'HIGH'
        elif risk_score > 0.3:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'overall_risk': risk_level,
            'risk_score': round(risk_score, 3),
            'high_risk_patterns': high_risk_patterns,
            'medium_risk_patterns': medium_risk_patterns,
            'total_patterns': len(patterns)
        }

# Mock classes for when dependencies are not available
class MockAnomalyDetector:
    """Mock anomaly detector for demo purposes"""
    def predict(self, X):
        return np.random.choice([-1, 1], size=len(X), p=[0.1, 0.9])
    
    def decision_function(self, X):
        return np.random.random(len(X)) - 0.5

class MockPredictiveModel:
    """Mock predictive model for demo purposes"""
    def predict(self, X):
        return np.random.random(len(X))
    
    def predict_proba(self, X):
        probs = np.random.random((len(X), 2))
        return probs / probs.sum(axis=1, keepdims=True)

class AIServiceManager:
    """Central manager for all AI services"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.services = {}
        self.logger = logging.getLogger(__name__)
    
    async def initialize_services(self):
        """Initialize all AI services"""
        service_configs = self.config.get('services', {})
        
        # Initialize anomaly detection
        anomaly_config = service_configs.get('anomaly_detection', {})
        self.services['anomaly_detection'] = AnomalyDetectionService(anomaly_config)
        await self.services['anomaly_detection'].initialize()
        
        # Initialize predictive analytics
        predictive_config = service_configs.get('predictive_analytics', {})
        self.services['predictive_analytics'] = PredictiveAnalyticsService(predictive_config)
        await self.services['predictive_analytics'].initialize()
        
        # Initialize network analysis
        network_config = service_configs.get('network_analysis', {})
        self.services['network_analysis'] = NetworkAnalysisService(network_config)
        await self.services['network_analysis'].initialize()
        
        self.logger.info(f"Initialized {len(self.services)} AI services")
    
    async def process_request(self, service_name: str, data: Dict) -> Dict:
        """Route request to appropriate AI service"""
        if service_name not in self.services:
            return {'error': f'Service {service_name} not available'}
        
        service = self.services[service_name]
        if not service.is_initialized:
            return {'error': f'Service {service_name} not initialized'}
        
        return await service.process(data)
    
    def get_service_status(self) -> Dict:
        """Get status of all AI services"""
        status = {
            'total_services': len(self.services),
            'services': {}
        }
        
        for name, service in self.services.items():
            status['services'][name] = service.get_status()
        
        return status
    
    def get_capabilities(self) -> Dict:
        """Get capabilities of all AI services"""
        return {
            'anomaly_detection': {
                'description': 'AI-powered anomaly detection for compliance risks',
                'capabilities': ['statistical_outliers', 'pattern_detection', 'risk_scoring'],
                'available': 'anomaly_detection' in self.services
            },
            'predictive_analytics': {
                'description': 'Predictive analytics for risk forecasting',
                'capabilities': ['risk_forecasting', 'trend_analysis', 'entity_risk_prediction'],
                'available': 'predictive_analytics' in self.services
            },
            'network_analysis': {
                'description': 'Advanced network analysis for relationship mapping',
                'capabilities': ['relationship_mapping', 'centrality_analysis', 'suspicious_pattern_detection'],
                'available': 'network_analysis' in self.services
            }
        }

# Global AI service manager instance
ai_service_manager = AIServiceManager()

async def initialize_ai_services(config: Dict = None):
    """Initialize AI services with configuration"""
    global ai_service_manager
    if config:
        ai_service_manager.config = config
    await ai_service_manager.initialize_services()
    return ai_service_manager

def get_ai_service_manager() -> AIServiceManager:
    """Get the global AI service manager"""
    return ai_service_manager
