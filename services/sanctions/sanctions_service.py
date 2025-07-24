"""
Sanctions Screening Service
Provides sanctions list checking and watchlist screening functionality
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Union
import requests
import logging
from pathlib import Path

class SanctionsService:
    """Comprehensive sanctions screening service"""
    
    def __init__(self, config=None, db_path: str = "sanctions.db"):
        self.config = config
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self.init_database()
        
        # Load sanctions lists
        self.sanctions_lists = self._load_sanctions_lists()
        
        # API endpoints for real-time screening
        self.api_endpoints = {
            'ofac': 'https://api.trade.gov/consolidated_screening_list/search',
            'un': 'https://scsanctions.un.org/fop/fop',
            'eu': 'https://webgate.ec.europa.eu/fsd/fsf'
        }
    
    def init_database(self):
        """Initialize sanctions database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sanctions entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sanctions_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_name TEXT,
                entity_type TEXT,
                name TEXT,
                aliases TEXT,
                address TEXT,
                country TEXT,
                program TEXT,
                list_date DATE,
                score REAL,
                status TEXT DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Screening results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS screening_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_name TEXT,
                query_type TEXT,
                match_found BOOLEAN,
                match_score REAL,
                matched_entity TEXT,
                list_name TEXT,
                risk_level TEXT,
                screening_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        """)
        
        # PEP (Politically Exposed Persons) table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pep_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                aliases TEXT,
                position TEXT,
                country TEXT,
                classification TEXT,
                risk_level TEXT,
                source TEXT,
                last_updated DATE,
                status TEXT DEFAULT 'active'
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Load initial data if database is empty
        self._populate_initial_data()
    
    def _load_sanctions_lists(self) -> Dict:
        """Load sanctions lists configuration"""
        return {
            'ofac_sdn': {
                'name': 'OFAC Specially Designated Nationals',
                'source': 'US Treasury OFAC',
                'type': 'sanctions',
                'risk_weight': 5.0
            },
            'ofac_consolidated': {
                'name': 'OFAC Consolidated Screening List',
                'source': 'US Treasury OFAC',
                'type': 'sanctions',
                'risk_weight': 4.5
            },
            'un_sanctions': {
                'name': 'UN Security Council Sanctions',
                'source': 'United Nations',
                'type': 'sanctions',
                'risk_weight': 5.0
            },
            'eu_sanctions': {
                'name': 'EU Consolidated List',
                'source': 'European Union',
                'type': 'sanctions',
                'risk_weight': 4.5
            },
            'pep_list': {
                'name': 'Politically Exposed Persons',
                'source': 'Various',
                'type': 'pep',
                'risk_weight': 3.5
            },
            'denied_persons': {
                'name': 'Denied Persons List',
                'source': 'US Commerce BIS',
                'type': 'export_control',
                'risk_weight': 4.0
            }
        }
    
    def _populate_initial_data(self):
        """Populate database with sample sanctions data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM sanctions_entities")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Sample sanctions entities (mock data for demonstration)
        sample_entities = [
            {
                'list_name': 'OFAC SDN',
                'entity_type': 'Individual',
                'name': 'John Doe Sanctions Test',
                'aliases': 'J. Doe, Johnny Doe',
                'address': '123 Sanctions St, Blocked City',
                'country': 'Sanctioned Country',
                'program': 'Counter Terrorism',
                'list_date': '2023-01-15',
                'score': 5.0
            },
            {
                'list_name': 'UN Sanctions',
                'entity_type': 'Entity',
                'name': 'Blocked Corporation Ltd',
                'aliases': 'BC Ltd, Blocked Corp',
                'address': '456 Embargo Ave',
                'country': 'Restricted Territory',
                'program': 'Arms Embargo',
                'list_date': '2022-11-20',
                'score': 4.8
            },
            {
                'list_name': 'EU Sanctions',
                'entity_type': 'Individual',
                'name': 'Maria Sanctions Example',
                'aliases': 'M. Example, Maria S.',
                'address': 'Unknown',
                'country': 'EU Sanctioned Region',
                'program': 'Human Rights Violations',
                'list_date': '2023-03-10',
                'score': 4.5
            }
        ]
        
        for entity in sample_entities:
            cursor.execute("""
                INSERT INTO sanctions_entities 
                (list_name, entity_type, name, aliases, address, country, program, list_date, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity['list_name'], entity['entity_type'], entity['name'],
                entity['aliases'], entity['address'], entity['country'],
                entity['program'], entity['list_date'], entity['score']
            ))
        
        # Sample PEP entities
        sample_peps = [
            {
                'name': 'Political Figure Example',
                'aliases': 'P.F. Example, Pol Figure',
                'position': 'Senior Government Official',
                'country': 'Example Country',
                'classification': 'Foreign PEP',
                'risk_level': 'HIGH',
                'source': 'Government Records',
                'last_updated': '2023-06-15'
            },
            {
                'name': 'Executive Branch Official',
                'aliases': 'E.B. Official',
                'position': 'Ministry Director',
                'country': 'Sample Nation',
                'classification': 'Domestic PEP',
                'risk_level': 'MEDIUM',
                'source': 'Public Records',
                'last_updated': '2023-05-20'
            }
        ]
        
        for pep in sample_peps:
            cursor.execute("""
                INSERT INTO pep_entities 
                (name, aliases, position, country, classification, risk_level, source, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pep['name'], pep['aliases'], pep['position'], pep['country'],
                pep['classification'], pep['risk_level'], pep['source'], pep['last_updated']
            ))
        
        conn.commit()
        conn.close()
        
        self.logger.info("Populated sanctions database with sample data")
    
    def screen_entity(self, name: str, entity_type: str = "individual", 
                     threshold: float = 0.8) -> Dict:
        """
        Screen an entity against sanctions lists
        
        Args:
            name: Entity name to screen
            entity_type: Type of entity (individual, organization)
            threshold: Matching threshold (0.0-1.0)
        
        Returns:
            Screening result dictionary
        """
        try:
            matches = []
            
            # Screen against local database
            local_matches = self._screen_local_database(name, threshold)
            matches.extend(local_matches)
            
            # Screen against PEP database
            pep_matches = self._screen_pep_database(name, threshold)
            matches.extend(pep_matches)
            
            # Determine overall risk
            max_score = max([m['score'] for m in matches]) if matches else 0.0
            risk_level = self._calculate_risk_level(max_score)
            
            # Save screening result
            result = {
                'query_name': name,
                'query_type': entity_type,
                'match_found': len(matches) > 0,
                'matches': matches,
                'highest_score': max_score,
                'risk_level': risk_level,
                'total_matches': len(matches),
                'screening_date': datetime.now().isoformat(),
                'status': 'completed'
            }
            
            self._save_screening_result(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error screening entity {name}: {str(e)}")
            return {
                'query_name': name,
                'query_type': entity_type,
                'match_found': False,
                'matches': [],
                'highest_score': 0.0,
                'risk_level': 'UNKNOWN',
                'total_matches': 0,
                'screening_date': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }
    
    def _screen_local_database(self, name: str, threshold: float) -> List[Dict]:
        """Screen against local sanctions database"""
        matches = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Search by name and aliases
        search_terms = [f"%{name.lower()}%"]
        
        cursor.execute("""
            SELECT * FROM sanctions_entities 
            WHERE LOWER(name) LIKE ? OR LOWER(aliases) LIKE ?
            AND status = 'active'
        """, (search_terms[0], search_terms[0]))
        
        for row in cursor.fetchall():
            # Calculate similarity score (simplified)
            score = self._calculate_similarity_score(name.lower(), row[3].lower())
            
            if score >= threshold:
                matches.append({
                    'entity_id': row[0],
                    'list_name': row[1],
                    'entity_type': row[2],
                    'matched_name': row[3],
                    'aliases': row[4],
                    'address': row[5],
                    'country': row[6],
                    'program': row[7],
                    'score': round(score, 3),
                    'risk_weight': row[9],
                    'match_type': 'sanctions'
                })
        
        conn.close()
        return matches
    
    def _screen_pep_database(self, name: str, threshold: float) -> List[Dict]:
        """Screen against PEP database"""
        matches = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM pep_entities 
            WHERE LOWER(name) LIKE ? OR LOWER(aliases) LIKE ?
            AND status = 'active'
        """, (f"%{name.lower()}%", f"%{name.lower()}%"))
        
        for row in cursor.fetchall():
            score = self._calculate_similarity_score(name.lower(), row[1].lower())
            
            if score >= threshold:
                matches.append({
                    'entity_id': row[0],
                    'matched_name': row[1],
                    'aliases': row[2],
                    'position': row[3],
                    'country': row[4],
                    'classification': row[5],
                    'risk_level': row[6],
                    'score': round(score, 3),
                    'match_type': 'pep'
                })
        
        conn.close()
        return matches
    
    def _calculate_similarity_score(self, query: str, target: str) -> float:
        """Calculate similarity score between two strings"""
        # Simple similarity calculation (can be enhanced with fuzzy matching)
        query_words = set(query.lower().split())
        target_words = set(target.lower().split())
        
        if not query_words or not target_words:
            return 0.0
        
        intersection = query_words.intersection(target_words)
        union = query_words.union(target_words)
        
        jaccard_score = len(intersection) / len(union)
        
        # Boost score for exact matches
        if query.lower() in target.lower() or target.lower() in query.lower():
            jaccard_score += 0.3
        
        return min(jaccard_score, 1.0)
    
    def _calculate_risk_level(self, score: float) -> str:
        """Calculate risk level based on score"""
        if score >= 0.9:
            return "CRITICAL"
        elif score >= 0.7:
            return "HIGH"
        elif score >= 0.5:
            return "MEDIUM"
        elif score >= 0.3:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _save_screening_result(self, result: Dict):
        """Save screening result to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO screening_results 
            (query_name, query_type, match_found, match_score, matched_entity, 
             list_name, risk_level, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result['query_name'],
            result['query_type'],
            result['match_found'],
            result['highest_score'],
            result['matches'][0]['matched_name'] if result['matches'] else None,
            result['matches'][0]['list_name'] if result['matches'] else None,
            result['risk_level'],
            json.dumps(result['matches'])
        ))
        
        conn.commit()
        conn.close()
    
    def bulk_screen(self, entities: List[Dict]) -> List[Dict]:
        """Screen multiple entities in bulk"""
        results = []
        
        for entity in entities:
            name = entity.get('name', '')
            entity_type = entity.get('type', 'individual')
            
            if name:
                result = self.screen_entity(name, entity_type)
                result['original_entity'] = entity
                results.append(result)
        
        return results
    
    def get_screening_history(self, limit: int = 100) -> List[Dict]:
        """Get recent screening history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM screening_results 
            ORDER BY screening_date DESC 
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'query_name': row[1],
                'query_type': row[2],
                'match_found': bool(row[3]),
                'match_score': row[4],
                'matched_entity': row[5],
                'list_name': row[6],
                'risk_level': row[7],
                'screening_date': row[8],
                'details': json.loads(row[9]) if row[9] else []
            })
        
        conn.close()
        return results
    
    def get_sanctions_statistics(self) -> Dict:
        """Get sanctions database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count entities by list
        cursor.execute("""
            SELECT list_name, COUNT(*) 
            FROM sanctions_entities 
            WHERE status = 'active'
            GROUP BY list_name
        """)
        list_counts = dict(cursor.fetchall())
        
        # Count PEPs
        cursor.execute("SELECT COUNT(*) FROM pep_entities WHERE status = 'active'")
        pep_count = cursor.fetchone()[0]
        
        # Recent screening activity
        cursor.execute("""
            SELECT COUNT(*) FROM screening_results 
            WHERE DATE(screening_date) = DATE('now')
        """)
        today_screenings = cursor.fetchone()[0]
        
        # High-risk matches today
        cursor.execute("""
            SELECT COUNT(*) FROM screening_results 
            WHERE DATE(screening_date) = DATE('now')
            AND risk_level IN ('HIGH', 'CRITICAL')
            AND match_found = 1
        """)
        high_risk_today = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'sanctions_lists': list_counts,
            'total_sanctions_entities': sum(list_counts.values()),
            'pep_entities': pep_count,
            'screenings_today': today_screenings,
            'high_risk_matches_today': high_risk_today,
            'last_updated': datetime.now().isoformat()
        }
    
    def update_sanctions_list(self, list_name: str, entities: List[Dict]) -> bool:
        """Update a specific sanctions list"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Mark existing entities as inactive
            cursor.execute("""
                UPDATE sanctions_entities 
                SET status = 'inactive' 
                WHERE list_name = ?
            """, (list_name,))
            
            # Insert new entities
            for entity in entities:
                cursor.execute("""
                    INSERT INTO sanctions_entities 
                    (list_name, entity_type, name, aliases, address, country, program, list_date, score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    list_name,
                    entity.get('entity_type', 'Unknown'),
                    entity.get('name', ''),
                    entity.get('aliases', ''),
                    entity.get('address', ''),
                    entity.get('country', ''),
                    entity.get('program', ''),
                    entity.get('list_date', datetime.now().date()),
                    entity.get('score', 4.0)
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Updated sanctions list {list_name} with {len(entities)} entities")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update sanctions list {list_name}: {str(e)}")
            return False
    
    def export_screening_results(self, format_type: str = "json") -> str:
        """Export screening results"""
        results = self.get_screening_history(1000)  # Get recent results
        
        if format_type.lower() == "json":
            return json.dumps(results, indent=2)
        elif format_type.lower() == "csv":
            # Convert to CSV format
            import csv
            from io import StringIO
            
            output = StringIO()
            if results:
                writer = csv.DictWriter(output, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            
            return output.getvalue()
        else:
            return json.dumps(results, indent=2)
    
    def health_check(self) -> Dict:
        """Perform health check on sanctions service"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test database connectivity
            cursor.execute("SELECT COUNT(*) FROM sanctions_entities")
            sanctions_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM pep_entities")
            pep_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'status': 'healthy',
                'database_accessible': True,
                'sanctions_entities': sanctions_count,
                'pep_entities': pep_count,
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'database_accessible': False,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
