"""
Geospatial Risk Mapping Service
Phase 3: Visual representation of geographical compliance risks
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import math
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class GeographicRiskFactor:
    """Geographic risk factor data model"""
    country_code: str
    country_name: str
    risk_category: str  # sanctions, fatf_non_compliant, high_risk, tax_haven
    risk_level: float  # 0.0 to 1.0
    risk_sources: List[str]
    last_updated: datetime
    additional_data: Optional[Dict[str, Any]] = None

@dataclass
class RiskLocation:
    """Risk location with coordinates"""
    latitude: float
    longitude: float
    country_code: str
    city: Optional[str] = None
    risk_score: float = 0.0
    risk_factors: List[str] = None
    
    def __post_init__(self):
        if self.risk_factors is None:
            self.risk_factors = []

@dataclass
class RiskConnection:
    """Risk connection between locations"""
    source_location: RiskLocation
    target_location: RiskLocation
    connection_type: str  # transaction, ownership, correspondence
    risk_score: float
    transaction_volume: Optional[float] = None
    connection_frequency: Optional[int] = None

class GeospatialRiskMapper:
    """Advanced geospatial risk mapping and visualization service"""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.risk_factors = {}
        self.risk_locations = {}
        self.risk_connections = []
        
        # Initialize geographic risk data
        self._initialize_geographic_risks()
        self._load_country_coordinates()
    
    def _initialize_geographic_risks(self):
        """Initialize geographic risk factors based on international lists"""
        
        # FATF High-Risk Jurisdictions
        fatf_high_risk = [
            {"code": "AF", "name": "Afghanistan", "risk": 0.95},
            {"code": "MM", "name": "Myanmar", "risk": 0.90},
            {"code": "KP", "name": "North Korea", "risk": 1.0},
            {"code": "IR", "name": "Iran", "risk": 0.95},
            {"code": "PK", "name": "Pakistan", "risk": 0.75},
            {"code": "UG", "name": "Uganda", "risk": 0.70},
            {"code": "YE", "name": "Yemen", "risk": 0.85}
        ]
        
        # OFAC Sanctioned Countries
        ofac_sanctioned = [
            {"code": "IR", "name": "Iran", "risk": 1.0},
            {"code": "KP", "name": "North Korea", "risk": 1.0},
            {"code": "SY", "name": "Syria", "risk": 0.95},
            {"code": "CU", "name": "Cuba", "risk": 0.80},
            {"code": "BY", "name": "Belarus", "risk": 0.75},
            {"code": "RU", "name": "Russia", "risk": 0.90},  # Partial sanctions
            {"code": "UA", "name": "Ukraine (Certain Regions)", "risk": 0.85}
        ]
        
        # EU High-Risk Third Countries
        eu_high_risk = [
            {"code": "AF", "name": "Afghanistan", "risk": 0.95},
            {"code": "BS", "name": "Bahamas", "risk": 0.60},
            {"code": "BW", "name": "Botswana", "risk": 0.55},
            {"code": "KH", "name": "Cambodia", "risk": 0.70},
            {"code": "GH", "name": "Ghana", "risk": 0.65},
            {"code": "IS", "name": "Iceland", "risk": 0.40},
            {"code": "MU", "name": "Mauritius", "risk": 0.50},
            {"code": "MM", "name": "Myanmar", "risk": 0.90},
            {"code": "NI", "name": "Nicaragua", "risk": 0.70},
            {"code": "KP", "name": "North Korea", "risk": 1.0},
            {"code": "PK", "name": "Pakistan", "risk": 0.75},
            {"code": "PA", "name": "Panama", "risk": 0.65},
            {"code": "SY", "name": "Syria", "risk": 0.95},
            {"code": "UG", "name": "Uganda", "risk": 0.70},
            {"code": "AE", "name": "United Arab Emirates", "risk": 0.45},
            {"code": "YE", "name": "Yemen", "risk": 0.85},
            {"code": "ZW", "name": "Zimbabwe", "risk": 0.75}
        ]
        
        # Tax Havens and Offshore Financial Centers
        tax_havens = [
            {"code": "AD", "name": "Andorra", "risk": 0.60},
            {"code": "BH", "name": "Bahrain", "risk": 0.55},
            {"code": "BB", "name": "Barbados", "risk": 0.50},
            {"code": "BZ", "name": "Belize", "risk": 0.65},
            {"code": "BM", "name": "Bermuda", "risk": 0.55},
            {"code": "VG", "name": "British Virgin Islands", "risk": 0.70},
            {"code": "KY", "name": "Cayman Islands", "risk": 0.60},
            {"code": "CY", "name": "Cyprus", "risk": 0.50},
            {"code": "GI", "name": "Gibraltar", "risk": 0.45},
            {"code": "GG", "name": "Guernsey", "risk": 0.40},
            {"code": "HK", "name": "Hong Kong", "risk": 0.45},
            {"code": "IM", "name": "Isle of Man", "risk": 0.40},
            {"code": "JE", "name": "Jersey", "risk": 0.40},
            {"code": "LB", "name": "Lebanon", "risk": 0.70},
            {"code": "LI", "name": "Liechtenstein", "risk": 0.45},
            {"code": "LU", "name": "Luxembourg", "risk": 0.35},
            {"code": "MC", "name": "Monaco", "risk": 0.50},
            {"code": "NR", "name": "Nauru", "risk": 0.80},
            {"code": "PA", "name": "Panama", "risk": 0.65},
            {"code": "SM", "name": "San Marino", "risk": 0.45},
            {"code": "SC", "name": "Seychelles", "risk": 0.65},
            {"code": "SG", "name": "Singapore", "risk": 0.30},
            {"code": "CH", "name": "Switzerland", "risk": 0.35},
            {"code": "TC", "name": "Turks and Caicos", "risk": 0.60},
            {"code": "VU", "name": "Vanuatu", "risk": 0.75}
        ]
        
        # Consolidate all risk factors
        all_countries = {}
        
        for country_list, category in [
            (fatf_high_risk, "fatf_high_risk"),
            (ofac_sanctioned, "sanctions"),
            (eu_high_risk, "eu_high_risk"),
            (tax_havens, "tax_haven")
        ]:
            for country in country_list:
                code = country["code"]
                if code not in all_countries:
                    all_countries[code] = {
                        "country_code": code,
                        "country_name": country["name"],
                        "max_risk": country["risk"],
                        "categories": [category],
                        "sources": []
                    }
                else:
                    all_countries[code]["categories"].append(category)
                    all_countries[code]["max_risk"] = max(
                        all_countries[code]["max_risk"], 
                        country["risk"]
                    )
        
        # Create GeographicRiskFactor objects
        for code, data in all_countries.items():
            self.risk_factors[code] = GeographicRiskFactor(
                country_code=code,
                country_name=data["country_name"],
                risk_category=", ".join(data["categories"]),
                risk_level=data["max_risk"],
                risk_sources=data["categories"],
                last_updated=datetime.now()
            )
        
        self.logger.info(f"Initialized geographic risk data for {len(self.risk_factors)} countries")
    
    def _load_country_coordinates(self):
        """Load country coordinates for mapping"""
        # Coordinates for major financial centers and risk countries
        country_coordinates = {
            # High-risk countries
            "AF": {"lat": 33.93911, "lng": 67.709953, "city": "Kabul"},
            "MM": {"lat": 16.8661, "lng": 96.1951, "city": "Yangon"},
            "KP": {"lat": 39.0392, "lng": 125.7625, "city": "Pyongyang"},
            "IR": {"lat": 35.6892, "lng": 51.3890, "city": "Tehran"},
            "SY": {"lat": 33.5138, "lng": 36.2765, "city": "Damascus"},
            "CU": {"lat": 23.1136, "lng": -82.3666, "city": "Havana"},
            "BY": {"lat": 53.9045, "lng": 27.5615, "city": "Minsk"},
            "RU": {"lat": 55.7558, "lng": 37.6176, "city": "Moscow"},
            "YE": {"lat": 15.3694, "lng": 44.1910, "city": "Sanaa"},
            "PK": {"lat": 33.6844, "lng": 73.0479, "city": "Islamabad"},
            
            # Tax havens and offshore centers
            "KY": {"lat": 19.3133, "lng": -81.2546, "city": "George Town"},
            "VG": {"lat": 18.4207, "lng": -64.6399, "city": "Road Town"},
            "BM": {"lat": 32.2942, "lng": -64.7839, "city": "Hamilton"},
            "BS": {"lat": 25.0343, "lng": -77.3963, "city": "Nassau"},
            "PA": {"lat": 8.5380, "lng": -80.7821, "city": "Panama City"},
            "BZ": {"lat": 17.5010, "lng": -88.1962, "city": "Belize City"},
            "AD": {"lat": 42.5063, "lng": 1.5218, "city": "Andorra la Vella"},
            "MC": {"lat": 43.7384, "lng": 7.4246, "city": "Monaco"},
            "LI": {"lat": 47.1660, "lng": 9.5554, "city": "Vaduz"},
            "SM": {"lat": 43.9424, "lng": 12.4578, "city": "San Marino"},
            "CY": {"lat": 35.1856, "lng": 33.3823, "city": "Nicosia"},
            "MT": {"lat": 35.8997, "lng": 14.5146, "city": "Valletta"},
            "LU": {"lat": 49.6117, "lng": 6.1319, "city": "Luxembourg"},
            "CH": {"lat": 46.9480, "lng": 7.4474, "city": "Bern"},
            "SG": {"lat": 1.3521, "lng": 103.8198, "city": "Singapore"},
            "HK": {"lat": 22.3193, "lng": 114.1694, "city": "Hong Kong"},
            "AE": {"lat": 25.2048, "lng": 55.2708, "city": "Dubai"},
            "BH": {"lat": 26.0667, "lng": 50.5577, "city": "Manama"},
            "GI": {"lat": 36.1408, "lng": -5.3536, "city": "Gibraltar"},
            
            # Major financial centers for reference
            "US": {"lat": 40.7128, "lng": -74.0060, "city": "New York"},
            "GB": {"lat": 51.5074, "lng": -0.1278, "city": "London"},
            "DE": {"lat": 50.1109, "lng": 8.6821, "city": "Frankfurt"},
            "JP": {"lat": 35.6762, "lng": 139.6503, "city": "Tokyo"},
            "FR": {"lat": 48.8566, "lng": 2.3522, "city": "Paris"},
            "CA": {"lat": 43.6532, "lng": -79.3832, "city": "Toronto"},
            "AU": {"lat": -33.8688, "lng": 151.2093, "city": "Sydney"},
            "NL": {"lat": 52.3676, "lng": 4.9041, "city": "Amsterdam"},
            "IT": {"lat": 45.4642, "lng": 9.1900, "city": "Milan"},
            "ES": {"lat": 40.4168, "lng": -3.7038, "city": "Madrid"},
            "SE": {"lat": 59.3293, "lng": 18.0686, "city": "Stockholm"},
            "DK": {"lat": 55.6761, "lng": 12.5683, "city": "Copenhagen"},
            "NO": {"lat": 59.9139, "lng": 10.7522, "city": "Oslo"},
            "FI": {"lat": 60.1699, "lng": 24.9384, "city": "Helsinki"},
            "IE": {"lat": 53.3498, "lng": -6.2603, "city": "Dublin"},
            "BE": {"lat": 50.8503, "lng": 4.3517, "city": "Brussels"},
            "AT": {"lat": 48.2082, "lng": 16.3738, "city": "Vienna"},
            "BR": {"lat": -23.5505, "lng": -46.6333, "city": "São Paulo"},
            "MX": {"lat": 19.4326, "lng": -99.1332, "city": "Mexico City"},
            "IN": {"lat": 19.0760, "lng": 72.8777, "city": "Mumbai"},
            "CN": {"lat": 31.2304, "lng": 121.4737, "city": "Shanghai"},
            "KR": {"lat": 37.5665, "lng": 126.9780, "city": "Seoul"},
            "ZA": {"lat": -26.2041, "lng": 28.0473, "city": "Johannesburg"}
        }
        
        # Create RiskLocation objects
        for country_code, coords in country_coordinates.items():
            risk_score = 0.0
            risk_factors = []
            
            if country_code in self.risk_factors:
                risk_score = self.risk_factors[country_code].risk_level
                risk_factors = self.risk_factors[country_code].risk_sources
            
            self.risk_locations[country_code] = RiskLocation(
                latitude=coords["lat"],
                longitude=coords["lng"],
                country_code=country_code,
                city=coords.get("city"),
                risk_score=risk_score,
                risk_factors=risk_factors
            )
        
        self.logger.info(f"Loaded coordinates for {len(self.risk_locations)} locations")
    
    def generate_risk_heatmap_data(self) -> Dict[str, Any]:
        """Generate data for risk heatmap visualization"""
        heatmap_data = {
            "type": "heatmap",
            "data": [],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_locations": len(self.risk_locations),
                "risk_categories": list(set([
                    category for rf in self.risk_factors.values()
                    for category in rf.risk_sources
                ]))
            }
        }
        
        for country_code, location in self.risk_locations.items():
            if location.risk_score > 0:
                heatmap_data["data"].append({
                    "lat": location.latitude,
                    "lng": location.longitude,
                    "intensity": location.risk_score,
                    "country_code": country_code,
                    "city": location.city,
                    "risk_factors": location.risk_factors,
                    "risk_level": self._get_risk_level_label(location.risk_score)
                })
        
        return heatmap_data
    
    def generate_choropleth_data(self) -> Dict[str, Any]:
        """Generate data for choropleth map visualization"""
        choropleth_data = {
            "type": "choropleth",
            "data": {},
            "color_scale": [
                {"value": 0.0, "color": "#00ff00", "label": "Low Risk"},
                {"value": 0.3, "color": "#ffff00", "label": "Medium Risk"},
                {"value": 0.6, "color": "#ff8000", "label": "High Risk"},
                {"value": 0.9, "color": "#ff0000", "label": "Critical Risk"}
            ],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "countries_with_data": len(self.risk_factors)
            }
        }
        
        for country_code, risk_factor in self.risk_factors.items():
            choropleth_data["data"][country_code] = {
                "country_name": risk_factor.country_name,
                "risk_score": risk_factor.risk_level,
                "risk_category": risk_factor.risk_category,
                "risk_sources": risk_factor.risk_sources,
                "color_intensity": risk_factor.risk_level,
                "risk_level": self._get_risk_level_label(risk_factor.risk_level)
            }
        
        return choropleth_data
    
    def generate_network_visualization(self, transaction_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate network visualization of risk connections"""
        network_data = {
            "type": "network",
            "nodes": [],
            "edges": [],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "layout": "force_directed"
            }
        }
        
        # Add nodes for all risk locations
        for country_code, location in self.risk_locations.items():
            node_size = max(10, location.risk_score * 50)
            node_color = self._get_risk_color(location.risk_score)
            
            network_data["nodes"].append({
                "id": country_code,
                "label": location.city or country_code,
                "x": location.longitude,
                "y": location.latitude,
                "size": node_size,
                "color": node_color,
                "risk_score": location.risk_score,
                "risk_factors": location.risk_factors,
                "type": "country"
            })
        
        # Add edges based on transaction data (if provided)
        if transaction_data:
            self._add_transaction_connections(network_data, transaction_data)
        else:
            # Add example high-risk connections
            self._add_example_risk_connections(network_data)
        
        return network_data
    
    def _add_transaction_connections(self, network_data: Dict[str, Any], transaction_data: List[Dict[str, Any]]):
        """Add transaction-based connections to network"""
        country_connections = {}
        
        # Aggregate transactions by country pairs
        for transaction in transaction_data:
            source_country = transaction.get("source_country")
            dest_country = transaction.get("destination_country")
            amount = transaction.get("amount", 0)
            
            if source_country and dest_country and source_country != dest_country:
                connection_key = tuple(sorted([source_country, dest_country]))
                
                if connection_key not in country_connections:
                    country_connections[connection_key] = {
                        "volume": 0,
                        "count": 0,
                        "max_amount": 0
                    }
                
                country_connections[connection_key]["volume"] += amount
                country_connections[connection_key]["count"] += 1
                country_connections[connection_key]["max_amount"] = max(
                    country_connections[connection_key]["max_amount"], amount
                )
        
        # Create edges for significant connections
        for (source, target), data in country_connections.items():
            if data["volume"] > 100000 or data["count"] > 10:  # Significant threshold
                
                # Calculate risk score for connection
                source_risk = self.risk_locations.get(source, RiskLocation(0, 0, source)).risk_score
                target_risk = self.risk_locations.get(target, RiskLocation(0, 0, target)).risk_score
                connection_risk = max(source_risk, target_risk)
                
                edge_width = min(max(math.log10(data["volume"]) - 3, 1), 10)
                edge_color = self._get_risk_color(connection_risk)
                
                network_data["edges"].append({
                    "source": source,
                    "target": target,
                    "weight": edge_width,
                    "color": edge_color,
                    "transaction_volume": data["volume"],
                    "transaction_count": data["count"],
                    "risk_score": connection_risk,
                    "type": "transaction_flow"
                })
    
    def _add_example_risk_connections(self, network_data: Dict[str, Any]):
        """Add example high-risk connections for demonstration"""
        example_connections = [
            ("RU", "BY", 0.8),  # Russia-Belarus
            ("IR", "SY", 0.9),  # Iran-Syria
            ("KP", "CN", 0.7),  # North Korea-China
            ("PA", "KY", 0.6),  # Panama-Cayman Islands
            ("VG", "BM", 0.5),  # BVI-Bermuda
            ("CH", "LI", 0.4),  # Switzerland-Liechtenstein
            ("SG", "HK", 0.3),  # Singapore-Hong Kong
            ("AE", "BH", 0.4),  # UAE-Bahrain
        ]
        
        for source, target, risk_score in example_connections:
            if source in self.risk_locations and target in self.risk_locations:
                edge_color = self._get_risk_color(risk_score)
                edge_width = risk_score * 8
                
                network_data["edges"].append({
                    "source": source,
                    "target": target,
                    "weight": edge_width,
                    "color": edge_color,
                    "risk_score": risk_score,
                    "type": "risk_connection"
                })
    
    def _get_risk_level_label(self, risk_score: float) -> str:
        """Get risk level label from score"""
        if risk_score >= 0.9:
            return "Critical"
        elif risk_score >= 0.7:
            return "High"
        elif risk_score >= 0.4:
            return "Medium"
        elif risk_score >= 0.2:
            return "Low"
        else:
            return "Minimal"
    
    def _get_risk_color(self, risk_score: float) -> str:
        """Get color code for risk score"""
        if risk_score >= 0.9:
            return "#8B0000"  # Dark Red
        elif risk_score >= 0.7:
            return "#FF0000"  # Red
        elif risk_score >= 0.5:
            return "#FF4500"  # Orange Red
        elif risk_score >= 0.3:
            return "#FFA500"  # Orange
        elif risk_score >= 0.1:
            return "#FFFF00"  # Yellow
        else:
            return "#00FF00"  # Green
    
    def get_country_risk_profile(self, country_code: str) -> Optional[Dict[str, Any]]:
        """Get detailed risk profile for specific country"""
        if country_code not in self.risk_factors:
            return None
        
        risk_factor = self.risk_factors[country_code]
        location = self.risk_locations.get(country_code)
        
        profile = {
            "country_code": country_code,
            "country_name": risk_factor.country_name,
            "risk_score": risk_factor.risk_level,
            "risk_level": self._get_risk_level_label(risk_factor.risk_level),
            "risk_categories": risk_factor.risk_sources,
            "risk_category_description": risk_factor.risk_category,
            "last_updated": risk_factor.last_updated.isoformat(),
            "coordinates": None,
            "compliance_recommendations": self._get_compliance_recommendations(risk_factor.risk_level)
        }
        
        if location:
            profile["coordinates"] = {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "city": location.city
            }
        
        return profile
    
    def _get_compliance_recommendations(self, risk_score: float) -> List[str]:
        """Get compliance recommendations based on risk score"""
        recommendations = []
        
        if risk_score >= 0.9:
            recommendations.extend([
                "Enhanced Due Diligence (EDD) required",
                "Senior management approval for all transactions",
                "Continuous monitoring and reporting",
                "Consider business relationship restrictions",
                "Detailed source of funds verification"
            ])
        elif risk_score >= 0.7:
            recommendations.extend([
                "Enhanced Due Diligence (EDD) recommended",
                "Increased transaction monitoring",
                "Regular periodic reviews",
                "Additional documentation requirements"
            ])
        elif risk_score >= 0.4:
            recommendations.extend([
                "Standard Customer Due Diligence (CDD)",
                "Regular monitoring and reviews",
                "Transaction pattern analysis"
            ])
        else:
            recommendations.extend([
                "Standard Customer Due Diligence (CDD)",
                "Regular monitoring as per policy"
            ])
        
        return recommendations
    
    def generate_risk_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive risk analytics"""
        analytics = {
            "overview": {
                "total_countries_monitored": len(self.risk_factors),
                "total_locations_mapped": len(self.risk_locations),
                "high_risk_countries": len([rf for rf in self.risk_factors.values() if rf.risk_level >= 0.7]),
                "sanctioned_countries": len([rf for rf in self.risk_factors.values() if "sanctions" in rf.risk_sources]),
                "tax_havens": len([rf for rf in self.risk_factors.values() if "tax_haven" in rf.risk_sources])
            },
            "risk_distribution": {},
            "regional_analysis": {},
            "risk_trends": {},
            "compliance_recommendations": {}
        }
        
        # Risk distribution analysis
        risk_ranges = {
            "critical": (0.9, 1.0),
            "high": (0.7, 0.9),
            "medium": (0.4, 0.7),
            "low": (0.2, 0.4),
            "minimal": (0.0, 0.2)
        }
        
        for range_name, (min_risk, max_risk) in risk_ranges.items():
            count = len([
                rf for rf in self.risk_factors.values()
                if min_risk <= rf.risk_level < max_risk
            ])
            analytics["risk_distribution"][range_name] = count
        
        # Regional analysis (simplified by continent)
        regional_mapping = {
            "Europe": ["AD", "BY", "CH", "CY", "DE", "DK", "ES", "FI", "FR", "GB", "GI", "IE", "IT", "LI", "LU", "MC", "MT", "NL", "NO", "RU", "SE", "SM"],
            "Asia": ["AF", "CN", "HK", "IN", "IR", "JP", "KP", "KR", "MM", "PK", "SG", "SY"],
            "Americas": ["BB", "BM", "BR", "BS", "BZ", "CA", "CU", "KY", "MX", "NI", "PA", "TC", "US", "VG"],
            "Middle East": ["AE", "BH", "LB", "YE"],
            "Africa": ["GH", "SC", "UG", "ZA", "ZW"],
            "Oceania": ["AU", "NR", "VU"]
        }
        
        for region, countries in regional_mapping.items():
            region_risks = [
                self.risk_factors[code].risk_level for code in countries
                if code in self.risk_factors
            ]
            if region_risks:
                analytics["regional_analysis"][region] = {
                    "average_risk": sum(region_risks) / len(region_risks),
                    "max_risk": max(region_risks),
                    "countries_monitored": len(region_risks),
                    "high_risk_countries": len([r for r in region_risks if r >= 0.7])
                }
        
        return analytics
    
    def export_risk_data(self, format: str = "json") -> Dict[str, Any]:
        """Export risk data in specified format"""
        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "format": format,
                "version": "1.0",
                "total_countries": len(self.risk_factors),
                "total_locations": len(self.risk_locations)
            },
            "risk_factors": {},
            "risk_locations": {},
            "visualizations": {
                "heatmap": self.generate_risk_heatmap_data(),
                "choropleth": self.generate_choropleth_data(),
                "network": self.generate_network_visualization()
            },
            "analytics": self.generate_risk_analytics()
        }
        
        # Export risk factors
        for code, rf in self.risk_factors.items():
            export_data["risk_factors"][code] = asdict(rf)
            # Convert datetime to string for JSON serialization
            export_data["risk_factors"][code]["last_updated"] = rf.last_updated.isoformat()
        
        # Export risk locations
        for code, location in self.risk_locations.items():
            export_data["risk_locations"][code] = asdict(location)
        
        return export_data
    
    # Test-compatible API methods
    async def generate_risk_heatmap(self, coordinates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate risk heatmap data from coordinates"""
        heatmap_data = {
            "coordinates": [],
            "bounds": {"north": -90, "south": 90, "east": -180, "west": 180},
            "risk_levels": {"low": 0, "medium": 0, "high": 0, "critical": 0}
        }
        
        for coord in coordinates:
            lat = coord.get("lat", 0)
            lng = coord.get("lng", 0)
            risk_score = coord.get("risk_score", 0)
            
            # Add to heatmap
            heatmap_data["coordinates"].append({
                "lat": lat,
                "lng": lng,
                "risk_score": risk_score,
                "intensity": risk_score
            })
            
            # Update bounds
            heatmap_data["bounds"]["north"] = max(heatmap_data["bounds"]["north"], lat)
            heatmap_data["bounds"]["south"] = min(heatmap_data["bounds"]["south"], lat)
            heatmap_data["bounds"]["east"] = max(heatmap_data["bounds"]["east"], lng)
            heatmap_data["bounds"]["west"] = min(heatmap_data["bounds"]["west"], lng)
            
            # Count risk levels
            if risk_score < 0.3:
                heatmap_data["risk_levels"]["low"] += 1
            elif risk_score < 0.6:
                heatmap_data["risk_levels"]["medium"] += 1
            elif risk_score < 0.8:
                heatmap_data["risk_levels"]["high"] += 1
            else:
                heatmap_data["risk_levels"]["critical"] += 1
        
        return heatmap_data
    
    async def generate_choropleth_data(self, countries: List[str]) -> Dict[str, Any]:
        """Generate choropleth mapping data for countries"""
        country_data = []
        risk_values = []
        
        for country_code in countries:
            if country_code in self.risk_factors:
                risk_factor = self.risk_factors[country_code]
                country_data.append({
                    "country_code": country_code,
                    "country_name": risk_factor.country_name,
                    "risk_score": risk_factor.risk_level,
                    "risk_category": risk_factor.risk_category,
                    "risk_sources": risk_factor.risk_sources
                })
                risk_values.append(risk_factor.risk_level)
        
        # Generate color scale
        if risk_values:
            min_risk = min(risk_values)
            max_risk = max(risk_values)
            color_scale = [
                {"value": min_risk, "color": "#00ff00"},
                {"value": (min_risk + max_risk) / 2, "color": "#ffff00"},
                {"value": max_risk, "color": "#ff0000"}
            ]
        else:
            color_scale = []
        
        return {
            "country_data": country_data,
            "color_scale": color_scale,
            "risk_range": {"min": min(risk_values) if risk_values else 0, "max": max(risk_values) if risk_values else 1}
        }
    
    async def create_network_visualization(self, connections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create network visualization data"""
        nodes = set()
        edges = []
        
        for connection in connections:
            source = connection.get("source")
            target = connection.get("target")
            risk_level = connection.get("risk_level", 0)
            volume = connection.get("transaction_volume", 0)
            
            nodes.add(source)
            nodes.add(target)
            
            edges.append({
                "source": source,
                "target": target,
                "risk_level": risk_level,
                "volume": volume,
                "width": min(volume / 100000, 10),  # Scale line width by volume
                "color": self._get_risk_color(risk_level)
            })
        
        node_list = []
        for node in nodes:
            node_risk = 0
            node_connections = len([e for e in edges if e["source"] == node or e["target"] == node])
            
            # Calculate node risk based on connections
            for edge in edges:
                if edge["source"] == node or edge["target"] == node:
                    node_risk = max(node_risk, edge["risk_level"])
            
            node_list.append({
                "id": node,
                "label": node,
                "risk_score": node_risk,
                "connections": node_connections,
                "size": min(node_connections * 3 + 5, 20),
                "color": self._get_risk_color(node_risk)
            })
        
        return {
            "nodes": node_list,
            "edges": edges,
            "network_stats": {
                "total_nodes": len(node_list),
                "total_edges": len(edges),
                "high_risk_connections": len([e for e in edges if e["risk_level"] > 0.7])
            }
        }
    
    async def analyze_geographic_risks(self, countries: List[str] = None, 
                                     coordinates: List[Dict[str, Any]] = None,
                                     connections: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Comprehensive geographic risk analysis"""
        analysis_result = {
            "overall_risk_score": 0.0,
            "high_risk_areas": [],
            "risk_breakdown": {},
            "recommendations": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Analyze countries
        if countries:
            country_risks = []
            for country_code in countries:
                if country_code in self.risk_factors:
                    risk_factor = self.risk_factors[country_code]
                    country_risks.append(risk_factor.risk_level)
                    
                    if risk_factor.risk_level > 0.7:
                        analysis_result["high_risk_areas"].append({
                            "type": "country",
                            "identifier": country_code,
                            "name": risk_factor.country_name,
                            "risk_score": risk_factor.risk_level
                        })
            
            if country_risks:
                analysis_result["risk_breakdown"]["country_average"] = sum(country_risks) / len(country_risks)
                analysis_result["overall_risk_score"] += analysis_result["risk_breakdown"]["country_average"] * 0.4
        
        # Analyze coordinates
        if coordinates:
            coord_risks = [coord.get("risk_score", 0) for coord in coordinates]
            if coord_risks:
                analysis_result["risk_breakdown"]["coordinate_average"] = sum(coord_risks) / len(coord_risks)
                analysis_result["overall_risk_score"] += analysis_result["risk_breakdown"]["coordinate_average"] * 0.3
        
        # Analyze connections
        if connections:
            connection_risks = [conn.get("risk_level", 0) for conn in connections]
            if connection_risks:
                analysis_result["risk_breakdown"]["connection_average"] = sum(connection_risks) / len(connection_risks)
                analysis_result["overall_risk_score"] += analysis_result["risk_breakdown"]["connection_average"] * 0.3
        
        # Generate recommendations
        if analysis_result["overall_risk_score"] > 0.7:
            analysis_result["recommendations"].append("Implement enhanced due diligence for all transactions")
            analysis_result["recommendations"].append("Increase monitoring frequency for high-risk areas")
        
        if len(analysis_result["high_risk_areas"]) > 0:
            analysis_result["recommendations"].append("Review and update risk assessment procedures")
        
        return analysis_result
    
    def _get_risk_color(self, risk_score: float) -> str:
        """Get color based on risk score"""
        if risk_score < 0.3:
            return "#00ff00"  # Green
        elif risk_score < 0.6:
            return "#ffff00"  # Yellow
        elif risk_score < 0.8:
            return "#ff8800"  # Orange
        else:
            return "#ff0000"  # Red


class GeospatialRiskService:
    """Service wrapper for geospatial risk mapping"""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.mapper = GeospatialRiskMapper()
        self.service_status = "operational"
    
    def get_risk_heatmap(self) -> Dict[str, Any]:
        """Get risk heatmap data for visualization"""
        try:
            return self.mapper.generate_risk_heatmap_data()
        except Exception as e:
            self.logger.error(f"Failed to generate risk heatmap: {e}")
            return {"error": str(e)}
    
    def get_risk_choropleth(self) -> Dict[str, Any]:
        """Get choropleth map data for visualization"""
        try:
            return self.mapper.generate_choropleth_data()
        except Exception as e:
            self.logger.error(f"Failed to generate choropleth data: {e}")
            return {"error": str(e)}
    
    def get_risk_network(self, transaction_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Get network visualization data"""
        try:
            return self.mapper.generate_network_visualization(transaction_data)
        except Exception as e:
            self.logger.error(f"Failed to generate network visualization: {e}")
            return {"error": str(e)}
    
    def get_country_profile(self, country_code: str) -> Dict[str, Any]:
        """Get country risk profile"""
        try:
            profile = self.mapper.get_country_risk_profile(country_code)
            if profile:
                return {"success": True, "data": profile}
            else:
                return {"success": False, "error": "Country not found in risk database"}
        except Exception as e:
            self.logger.error(f"Failed to get country profile: {e}")
            return {"success": False, "error": str(e)}
    
    def get_risk_analytics(self) -> Dict[str, Any]:
        """Get comprehensive risk analytics"""
        try:
            return self.mapper.generate_risk_analytics()
        except Exception as e:
            self.logger.error(f"Failed to generate risk analytics: {e}")
            return {"error": str(e)}
    
    def export_data(self, format: str = "json") -> Dict[str, Any]:
        """Export all risk data"""
        try:
            return self.mapper.export_risk_data(format)
        except Exception as e:
            self.logger.error(f"Failed to export risk data: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for geospatial risk service"""
        try:
            return {
                "status": self.service_status,
                "countries_monitored": len(self.mapper.risk_factors),
                "locations_mapped": len(self.mapper.risk_locations),
                "last_updated": datetime.now().isoformat(),
                "capabilities": [
                    "Risk heatmap generation",
                    "Choropleth mapping",
                    "Network visualization",
                    "Country risk profiling",
                    "Risk analytics"
                ]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
