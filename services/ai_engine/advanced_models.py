"""
Advanced AI Models for Compliant.one
Anomaly detection, predictive analytics, and enhanced network analysis
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import networkx as nx
from typing import Dict, List, Any, Tuple, Optional
import logging
from datetime import datetime, timedelta
import pickle
import json

logger = logging.getLogger(__name__)

class AnomalyDetectionEngine:
    """Advanced anomaly detection for compliance and risk monitoring"""
    
    def __init__(self, contamination=0.1):
        self.contamination = contamination
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def train_on_historical_data(self, data: pd.DataFrame, features: List[str]) -> Dict[str, Any]:
        """
        Train anomaly detection model on historical data
        
        Args:
            data: Historical transaction/activity data
            features: List of feature columns to use for training
            
        Returns:
            Training results and model performance metrics
        """
        try:
            logger.info("Training anomaly detection model")
            
            # Prepare training data
            X = data[features].fillna(0)
            X_scaled = self.scaler.fit_transform(X)
            
            # Train isolation forest
            self.isolation_forest.fit(X_scaled)
            self.is_trained = True
            
            # Generate predictions for evaluation
            predictions = self.isolation_forest.predict(X_scaled)
            anomaly_scores = self.isolation_forest.score_samples(X_scaled)
            
            # Calculate statistics
            n_anomalies = np.sum(predictions == -1)
            anomaly_rate = n_anomalies / len(predictions)
            
            results = {
                'model_trained': True,
                'training_samples': len(X),
                'features_used': features,
                'anomalies_detected': int(n_anomalies),
                'anomaly_rate': float(anomaly_rate),
                'mean_anomaly_score': float(np.mean(anomaly_scores)),
                'std_anomaly_score': float(np.std(anomaly_scores)),
                'training_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Anomaly detection model trained successfully: {anomaly_rate:.2%} anomaly rate")
            return results
            
        except Exception as e:
            logger.error(f"Error training anomaly detection model: {e}")
            return {'error': str(e), 'model_trained': False}
    
    def detect_anomalies(self, data: pd.DataFrame, features: List[str]) -> pd.DataFrame:
        """
        Detect anomalies in new data
        
        Args:
            data: New data to analyze for anomalies
            features: Feature columns to use (must match training features)
            
        Returns:
            DataFrame with anomaly predictions and scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before detecting anomalies")
        
        try:
            # Prepare data
            X = data[features].fillna(0)
            X_scaled = self.scaler.transform(X)
            
            # Predict anomalies
            predictions = self.isolation_forest.predict(X_scaled)
            scores = self.isolation_forest.score_samples(X_scaled)
            
            # Add results to dataframe
            result_df = data.copy()
            result_df['is_anomaly'] = predictions == -1
            result_df['anomaly_score'] = scores
            result_df['risk_level'] = pd.cut(
                scores, 
                bins=[-np.inf, -0.1, 0.0, 0.1, np.inf],
                labels=['Critical', 'High', 'Medium', 'Low']
            )
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            raise

class PredictiveAnalyticsEngine:
    """Predictive analytics for risk forecasting and trend analysis"""
    
    def __init__(self):
        self.risk_predictor = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight='balanced'
        )
        self.scaler = StandardScaler()
        self.feature_importance = {}
        self.is_trained = False
        
    def train_risk_predictor(self, training_data: pd.DataFrame, target_column: str, 
                           feature_columns: List[str]) -> Dict[str, Any]:
        """
        Train predictive model for risk assessment
        
        Args:
            training_data: Historical data with known risk outcomes
            target_column: Column containing risk labels (0=low, 1=high)
            feature_columns: Features to use for prediction
            
        Returns:
            Training results and model performance
        """
        try:
            logger.info("Training predictive risk model")
            
            # Prepare data
            X = training_data[feature_columns].fillna(0)
            y = training_data[target_column]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.risk_predictor.fit(X_train_scaled, y_train)
            self.is_trained = True
            
            # Evaluate model
            train_predictions = self.risk_predictor.predict(X_train_scaled)
            test_predictions = self.risk_predictor.predict(X_test_scaled)
            
            train_accuracy = accuracy_score(y_train, train_predictions)
            test_accuracy = accuracy_score(y_test, test_predictions)
            
            # Feature importance
            self.feature_importance = dict(zip(
                feature_columns,
                self.risk_predictor.feature_importances_
            ))
            
            results = {
                'model_trained': True,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'train_accuracy': float(train_accuracy),
                'test_accuracy': float(test_accuracy),
                'feature_importance': self.feature_importance,
                'classification_report': classification_report(y_test, test_predictions, output_dict=True),
                'training_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Risk predictor trained: {test_accuracy:.2%} accuracy")
            return results
            
        except Exception as e:
            logger.error(f"Error training risk predictor: {e}")
            return {'error': str(e), 'model_trained': False}
    
    def predict_risk(self, data: pd.DataFrame, feature_columns: List[str]) -> pd.DataFrame:
        """
        Predict risk levels for new data
        
        Args:
            data: New data to analyze
            feature_columns: Features to use (must match training features)
            
        Returns:
            DataFrame with risk predictions and probabilities
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            # Prepare data
            X = data[feature_columns].fillna(0)
            X_scaled = self.scaler.transform(X)
            
            # Make predictions
            risk_predictions = self.risk_predictor.predict(X_scaled)
            risk_probabilities = self.risk_predictor.predict_proba(X_scaled)
            
            # Add results to dataframe
            result_df = data.copy()
            result_df['predicted_risk'] = risk_predictions
            result_df['risk_probability'] = risk_probabilities[:, 1]  # Probability of high risk
            result_df['risk_category'] = np.where(
                result_df['risk_probability'] > 0.8, 'Critical',
                np.where(result_df['risk_probability'] > 0.6, 'High',
                        np.where(result_df['risk_probability'] > 0.4, 'Medium', 'Low'))
            )
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error predicting risk: {e}")
            raise
    
    def forecast_trends(self, time_series_data: pd.DataFrame, target_column: str, 
                       periods: int = 30) -> Dict[str, Any]:
        """
        Forecast trends in risk metrics
        
        Args:
            time_series_data: Time series data with date index
            target_column: Column to forecast
            periods: Number of periods to forecast
            
        Returns:
            Forecast results with confidence intervals
        """
        try:
            # Simple trend forecasting using moving averages and linear extrapolation
            data = time_series_data[target_column].dropna()
            
            # Calculate moving averages
            ma_7 = data.rolling(window=7).mean()
            ma_30 = data.rolling(window=30).mean()
            
            # Calculate trend
            recent_trend = (ma_7.iloc[-1] - ma_7.iloc[-7]) / 7 if len(ma_7) >= 7 else 0
            
            # Generate forecast
            last_value = data.iloc[-1]
            forecast_values = []
            
            for i in range(1, periods + 1):
                forecast_value = last_value + (recent_trend * i)
                forecast_values.append(forecast_value)
            
            # Calculate confidence intervals (simplified)
            std_dev = data.std()
            confidence_interval = 1.96 * std_dev  # 95% confidence
            
            forecast_dates = pd.date_range(
                start=data.index[-1] + pd.Timedelta(days=1),
                periods=periods,
                freq='D'
            )
            
            forecast_results = {
                'forecast_dates': forecast_dates.strftime('%Y-%m-%d').tolist(),
                'forecast_values': forecast_values,
                'upper_bound': [v + confidence_interval for v in forecast_values],
                'lower_bound': [v - confidence_interval for v in forecast_values],
                'trend_direction': 'increasing' if recent_trend > 0 else 'decreasing',
                'trend_strength': abs(recent_trend),
                'confidence_interval': float(confidence_interval),
                'forecast_timestamp': datetime.now().isoformat()
            }
            
            return forecast_results
            
        except Exception as e:
            logger.error(f"Error forecasting trends: {e}")
            return {'error': str(e)}

class NetworkAnalysisEngine:
    """Enhanced network analysis for relationship mapping and risk propagation"""
    
    def __init__(self):
        self.network = nx.Graph()
        self.entity_risk_scores = {}
        
    def build_network_from_data(self, relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build network graph from relationship data
        
        Args:
            relationships: List of relationship dictionaries with 'source', 'target', 'type', 'weight'
            
        Returns:
            Network statistics and metrics
        """
        try:
            logger.info("Building network graph from relationship data")
            
            # Clear existing network
            self.network.clear()
            
            # Add edges from relationships
            for rel in relationships:
                source = rel.get('source')
                target = rel.get('target')
                rel_type = rel.get('type', 'unknown')
                weight = rel.get('weight', 1.0)
                
                if source and target:
                    self.network.add_edge(
                        source, target,
                        relationship_type=rel_type,
                        weight=weight
                    )
            
            # Calculate network metrics
            n_nodes = self.network.number_of_nodes()
            n_edges = self.network.number_of_edges()
            density = nx.density(self.network)
            
            # Calculate centrality measures
            centrality_metrics = {}
            if n_nodes > 0:
                centrality_metrics = {
                    'betweenness_centrality': nx.betweenness_centrality(self.network),
                    'closeness_centrality': nx.closeness_centrality(self.network),
                    'degree_centrality': nx.degree_centrality(self.network),
                    'eigenvector_centrality': nx.eigenvector_centrality(self.network, max_iter=1000)
                }
            
            # Identify communities
            communities = list(nx.connected_components(self.network))
            
            network_stats = {
                'nodes': n_nodes,
                'edges': n_edges,
                'density': float(density),
                'communities': len(communities),
                'largest_community_size': len(max(communities, key=len)) if communities else 0,
                'centrality_metrics': centrality_metrics,
                'build_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Network built: {n_nodes} nodes, {n_edges} edges")
            return network_stats
            
        except Exception as e:
            logger.error(f"Error building network: {e}")
            return {'error': str(e)}
    
    def calculate_risk_propagation(self, initial_risks: Dict[str, float], 
                                 propagation_factor: float = 0.5,
                                 iterations: int = 10) -> Dict[str, float]:
        """
        Calculate risk propagation through network
        
        Args:
            initial_risks: Initial risk scores for entities
            propagation_factor: Factor controlling risk propagation strength
            iterations: Number of propagation iterations
            
        Returns:
            Final risk scores after propagation
        """
        try:
            logger.info("Calculating risk propagation through network")
            
            # Initialize risk scores
            current_risks = {}
            for node in self.network.nodes():
                current_risks[node] = initial_risks.get(node, 0.0)
            
            # Propagate risk through iterations
            for iteration in range(iterations):
                new_risks = current_risks.copy()
                
                for node in self.network.nodes():
                    neighbors = list(self.network.neighbors(node))
                    
                    if neighbors:
                        # Calculate average neighbor risk
                        neighbor_risks = [current_risks[neighbor] for neighbor in neighbors]
                        avg_neighbor_risk = np.mean(neighbor_risks)
                        
                        # Propagate risk
                        propagated_risk = propagation_factor * avg_neighbor_risk
                        new_risks[node] = max(current_risks[node], propagated_risk)
                
                current_risks = new_risks
            
            self.entity_risk_scores = current_risks
            logger.info(f"Risk propagation completed after {iterations} iterations")
            return current_risks
            
        except Exception as e:
            logger.error(f"Error calculating risk propagation: {e}")
            return {}
    
    def identify_high_risk_clusters(self, risk_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Identify clusters of high-risk entities
        
        Args:
            risk_threshold: Minimum risk score to consider high-risk
            
        Returns:
            List of high-risk clusters with metadata
        """
        try:
            high_risk_entities = {
                entity: risk for entity, risk in self.entity_risk_scores.items()
                if risk >= risk_threshold
            }
            
            if not high_risk_entities:
                return []
            
            # Create subgraph of high-risk entities
            high_risk_subgraph = self.network.subgraph(high_risk_entities.keys())
            
            # Find connected components (clusters)
            clusters = []
            for component in nx.connected_components(high_risk_subgraph):
                if len(component) > 1:  # Only consider clusters with multiple entities
                    cluster_risks = [self.entity_risk_scores[entity] for entity in component]
                    
                    cluster_info = {
                        'entities': list(component),
                        'size': len(component),
                        'avg_risk_score': np.mean(cluster_risks),
                        'max_risk_score': np.max(cluster_risks),
                        'total_connections': high_risk_subgraph.subgraph(component).number_of_edges(),
                        'risk_density': np.mean(cluster_risks) * len(component)
                    }
                    clusters.append(cluster_info)
            
            # Sort by risk density (combination of risk and cluster size)
            clusters.sort(key=lambda x: x['risk_density'], reverse=True)
            
            logger.info(f"Identified {len(clusters)} high-risk clusters")
            return clusters
            
        except Exception as e:
            logger.error(f"Error identifying high-risk clusters: {e}")
            return []
    
    def get_entity_network_metrics(self, entity: str) -> Dict[str, Any]:
        """
        Get network metrics for a specific entity
        
        Args:
            entity: Entity name to analyze
            
        Returns:
            Network metrics for the entity
        """
        try:
            if entity not in self.network.nodes():
                return {'error': f'Entity {entity} not found in network'}
            
            # Calculate metrics
            degree = self.network.degree(entity)
            neighbors = list(self.network.neighbors(entity))
            
            # Centrality measures
            betweenness = nx.betweenness_centrality(self.network).get(entity, 0)
            closeness = nx.closeness_centrality(self.network).get(entity, 0)
            eigenvector = nx.eigenvector_centrality(self.network, max_iter=1000).get(entity, 0)
            
            # Risk-related metrics
            current_risk = self.entity_risk_scores.get(entity, 0)
            neighbor_risks = [self.entity_risk_scores.get(neighbor, 0) for neighbor in neighbors]
            avg_neighbor_risk = np.mean(neighbor_risks) if neighbor_risks else 0
            
            metrics = {
                'entity': entity,
                'degree': degree,
                'neighbors': neighbors,
                'betweenness_centrality': float(betweenness),
                'closeness_centrality': float(closeness),
                'eigenvector_centrality': float(eigenvector),
                'current_risk_score': float(current_risk),
                'neighbor_count': len(neighbors),
                'avg_neighbor_risk': float(avg_neighbor_risk),
                'risk_influence': float(current_risk * degree),  # Risk weighted by connections
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting entity network metrics: {e}")
            return {'error': str(e)}

class AdvancedModelManager:
    """Centralized manager for all advanced AI models"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.anomaly_detector = AnomalyDetectionEngine()
        self.predictive_engine = PredictiveAnalyticsEngine()
        self.network_analyzer = NetworkAnalysisEngine()
        self.model_performance = {}
        
    def train_all_models(self, training_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Train all advanced AI models
        
        Args:
            training_data: Dictionary containing training datasets for each model
            
        Returns:
            Training results for all models
        """
        results = {
            'training_started': datetime.now().isoformat(),
            'models': {}
        }
        
        # Train anomaly detection
        if 'anomaly_data' in training_data:
            logger.info("Training anomaly detection model")
            anomaly_features = self.config.get('anomaly_features', [])
            results['models']['anomaly_detection'] = self.anomaly_detector.train_on_historical_data(
                training_data['anomaly_data'], anomaly_features
            )
        
        # Train risk predictor
        if 'risk_data' in training_data:
            logger.info("Training risk prediction model")
            risk_features = self.config.get('risk_features', [])
            risk_target = self.config.get('risk_target', 'high_risk')
            results['models']['risk_prediction'] = self.predictive_engine.train_risk_predictor(
                training_data['risk_data'], risk_target, risk_features
            )
        
        # Build network
        if 'network_data' in training_data:
            logger.info("Building network analysis model")
            relationships = training_data['network_data'].to_dict('records')
            results['models']['network_analysis'] = self.network_analyzer.build_network_from_data(
                relationships
            )
        
        results['training_completed'] = datetime.now().isoformat()
        self.model_performance = results
        
        logger.info("All advanced models trained successfully")
        return results
    
    def analyze_entity_comprehensive(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive analysis of an entity using all advanced models
        
        Args:
            entity_data: Entity data and context
            
        Returns:
            Comprehensive analysis results
        """
        entity_name = entity_data.get('name', 'Unknown')
        logger.info(f"Running comprehensive analysis for entity: {entity_name}")
        
        analysis_results = {
            'entity_name': entity_name,
            'analysis_timestamp': datetime.now().isoformat(),
            'anomaly_analysis': {},
            'risk_prediction': {},
            'network_analysis': {},
            'overall_assessment': {}
        }
        
        try:
            # Anomaly detection
            if hasattr(self.anomaly_detector, 'is_trained') and self.anomaly_detector.is_trained:
                # Convert entity data to DataFrame for analysis
                entity_df = pd.DataFrame([entity_data])
                anomaly_features = self.config.get('anomaly_features', [])
                
                if all(feature in entity_df.columns for feature in anomaly_features):
                    anomaly_results = self.anomaly_detector.detect_anomalies(entity_df, anomaly_features)
                    analysis_results['anomaly_analysis'] = {
                        'is_anomaly': bool(anomaly_results['is_anomaly'].iloc[0]),
                        'anomaly_score': float(anomaly_results['anomaly_score'].iloc[0]),
                        'risk_level': str(anomaly_results['risk_level'].iloc[0])
                    }
            
            # Risk prediction
            if hasattr(self.predictive_engine, 'is_trained') and self.predictive_engine.is_trained:
                entity_df = pd.DataFrame([entity_data])
                risk_features = self.config.get('risk_features', [])
                
                if all(feature in entity_df.columns for feature in risk_features):
                    risk_results = self.predictive_engine.predict_risk(entity_df, risk_features)
                    analysis_results['risk_prediction'] = {
                        'predicted_risk': int(risk_results['predicted_risk'].iloc[0]),
                        'risk_probability': float(risk_results['risk_probability'].iloc[0]),
                        'risk_category': str(risk_results['risk_category'].iloc[0])
                    }
            
            # Network analysis
            if entity_name in self.network_analyzer.network.nodes():
                network_metrics = self.network_analyzer.get_entity_network_metrics(entity_name)
                analysis_results['network_analysis'] = network_metrics
            
            # Overall assessment
            risk_score = analysis_results.get('risk_prediction', {}).get('risk_probability', 0)
            anomaly_score = abs(analysis_results.get('anomaly_analysis', {}).get('anomaly_score', 0))
            network_influence = analysis_results.get('network_analysis', {}).get('risk_influence', 0)
            
            overall_risk = (risk_score * 0.4) + (anomaly_score * 0.3) + (min(network_influence, 1.0) * 0.3)
            
            analysis_results['overall_assessment'] = {
                'overall_risk_score': float(overall_risk),
                'risk_category': 'Critical' if overall_risk > 0.8 else 
                               'High' if overall_risk > 0.6 else 
                               'Medium' if overall_risk > 0.4 else 'Low',
                'recommendation': self._generate_recommendation(overall_risk, analysis_results)
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            analysis_results['error'] = str(e)
        
        return analysis_results
    
    def _generate_recommendation(self, risk_score: float, analysis_results: Dict[str, Any]) -> str:
        """Generate recommendation based on analysis results"""
        if risk_score > 0.8:
            return "IMMEDIATE ATTENTION REQUIRED - High risk entity requiring enhanced due diligence"
        elif risk_score > 0.6:
            return "ENHANCED MONITORING - Elevated risk requiring additional scrutiny"
        elif risk_score > 0.4:
            return "STANDARD MONITORING - Moderate risk, continue regular monitoring"
        else:
            return "LOW RISK - Standard compliance procedures sufficient"
