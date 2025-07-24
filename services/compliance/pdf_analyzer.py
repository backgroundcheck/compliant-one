"""
PDF Compliance Analysis Service
Analyzes PDF documents for compliance risks, regulatory mentions, and sanctions screening
"""

import os
import sys
import re
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

# PDF processing imports
try:
    import PyPDF2
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# NLP and analysis imports
try:
    import nltk
    from collections import Counter
    import spacy
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

class PDFComplianceAnalyzer:
    """Comprehensive PDF compliance analysis engine"""
    
    def __init__(self, db_path: str = "compliance_analysis.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self.init_database()
        
        # Compliance keywords and patterns
        self.compliance_patterns = self._load_compliance_patterns()
        
        # Risk scoring weights
        self.risk_weights = {
            'sanctions': 5.0,
            'aml_cft': 4.5,
            'pci_dss': 4.0,
            'gdpr': 4.0,
            'regulatory': 3.5,
            'financial': 3.0,
            'data_privacy': 3.5,
            'cybersecurity': 4.0
        }
    
    def init_database(self):
        """Initialize compliance analysis database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analysis results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compliance_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT UNIQUE,
                analysis_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_documents INTEGER,
                processed_documents INTEGER,
                compliance_issues INTEGER,
                high_risk_items INTEGER,
                avg_risk_score REAL,
                frameworks TEXT,
                status TEXT
            )
        """)
        
        # Document findings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT,
                document_path TEXT,
                document_name TEXT,
                file_size INTEGER,
                page_count INTEGER,
                word_count INTEGER,
                compliance_framework TEXT,
                finding_type TEXT,
                finding_description TEXT,
                risk_level TEXT,
                risk_score REAL,
                page_number INTEGER,
                confidence_score REAL,
                FOREIGN KEY (analysis_id) REFERENCES compliance_analysis(analysis_id)
            )
        """)
        
        # Entity extraction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extracted_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT,
                document_name TEXT,
                entity_type TEXT,
                entity_text TEXT,
                entity_label TEXT,
                confidence_score REAL,
                context TEXT,
                FOREIGN KEY (analysis_id) REFERENCES compliance_analysis(analysis_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_compliance_patterns(self) -> Dict[str, List[str]]:
        """Load compliance detection patterns"""
        return {
            'sanctions': [
                r'sanctioned?\s+(?:entity|individual|person|organization)',
                r'OFAC\s+(?:list|sanctions?)',
                r'blocked?\s+person',
                r'designated?\s+national',
                r'specially\s+designated\s+national',
                r'embargo(?:ed)?',
                r'export\s+control',
                r'denied?\s+person',
                r'restricted?\s+(?:party|entity)',
                r'watchlist',
                r'PEP\s+(?:list|screening)',
                r'politically\s+exposed\s+person'
            ],
            'aml_cft': [
                r'anti[- ]money\s+laundering',
                r'AML\s+(?:compliance|policy|procedure)',
                r'know\s+your\s+customer',
                r'KYC\s+(?:compliance|policy|procedure)',
                r'customer\s+due\s+diligence',
                r'CDD\s+(?:procedure|requirement)',
                r'suspicious\s+(?:activity|transaction)',
                r'SAR\s+(?:filing|report)',
                r'cash\s+transaction\s+report',
                r'CTR\s+(?:filing|requirement)',
                r'beneficial\s+owner(?:ship)?',
                r'ultimate\s+beneficial\s+owner',
                r'UBO\s+(?:identification|verification)',
                r'source\s+of\s+(?:funds|wealth)',
                r'enhanced\s+due\s+diligence',
                r'EDD\s+(?:procedure|requirement)',
                r'correspondent\s+banking',
                r'wire\s+transfer\s+rule',
                r'travel\s+rule',
                r'FATF\s+(?:recommendation|guidance)',
                r'FinCEN\s+(?:guidance|requirement)'
            ],
            'gdpr': [
                r'general\s+data\s+protection\s+regulation',
                r'GDPR\s+(?:compliance|requirement)',
                r'data\s+subject\s+rights?',
                r'right\s+to\s+(?:erasure|portability|rectification)',
                r'data\s+protection\s+officer',
                r'DPO\s+(?:appointment|designation)',
                r'lawful\s+basis\s+for\s+processing',
                r'consent\s+(?:management|withdrawal)',
                r'data\s+breach\s+notification',
                r'supervisory\s+authority',
                r'privacy\s+by\s+design',
                r'data\s+protection\s+impact\s+assessment',
                r'DPIA\s+(?:requirement|conduct)',
                r'cross[- ]border\s+(?:transfer|processing)',
                r'adequacy\s+decision',
                r'binding\s+corporate\s+rules',
                r'BCR\s+(?:approval|implementation)',
                r'standard\s+contractual\s+clauses',
                r'SCC\s+(?:implementation|use)'
            ],
            'pci_dss': [
                r'payment\s+card\s+industry',
                r'PCI\s+DSS\s+(?:compliance|requirement)',
                r'cardholder\s+data\s+environment',
                r'CDE\s+(?:security|protection)',
                r'primary\s+account\s+number',
                r'PAN\s+(?:protection|encryption)',
                r'sensitive\s+authentication\s+data',
                r'SAD\s+(?:protection|prohibition)',
                r'payment\s+application\s+data\s+security',
                r'PA[- ]DSS\s+(?:compliance|validation)',
                r'qualified\s+security\s+assessor',
                r'QSA\s+(?:assessment|validation)',
                r'approved\s+scanning\s+vendor',
                r'ASV\s+(?:scan|vulnerability)',
                r'compensating\s+control',
                r'network\s+segmentation',
                r'penetration\s+test(?:ing)?',
                r'vulnerability\s+(?:scan|assessment)',
                r'security\s+policy\s+(?:framework|procedure)'
            ],
            'sox': [
                r'sarbanes[- ]oxley\s+act',
                r'SOX\s+(?:compliance|requirement)',
                r'section\s+(?:302|404|906)',
                r'internal\s+control(?:s)?\s+over\s+financial\s+reporting',
                r'ICFR\s+(?:assessment|testing)',
                r'material\s+weakness(?:es)?',
                r'significant\s+deficienc(?:y|ies)',
                r'control\s+deficienc(?:y|ies)',
                r'management\s+assessment',
                r'auditor\s+attestation',
                r'COSO\s+(?:framework|guidance)',
                r'entity[- ]level\s+control',
                r'process[- ]level\s+control',
                r'IT\s+general\s+control',
                r'ITGC\s+(?:testing|assessment)',
                r'application\s+control',
                r'automated\s+control',
                r'manual\s+control'
            ],
            'financial_crime': [
                r'financial\s+crime',
                r'fraud\s+(?:detection|prevention)',
                r'market\s+manipulation',
                r'insider\s+(?:trading|dealing)',
                r'market\s+abuse',
                r'trade\s+surveillance',
                r'transaction\s+monitoring',
                r'TM\s+(?:system|alert)',
                r'typology\s+(?:analysis|detection)',
                r'red\s+flag\s+(?:indicator|alert)',
                r'threshold\s+(?:monitoring|breach)',
                r'risk\s+scoring\s+(?:model|engine)',
                r'false\s+positive\s+(?:rate|reduction)',
                r'investigation\s+(?:procedure|workflow)',
                r'case\s+management\s+(?:system|procedure)'
            ],
            'cybersecurity': [
                r'cyber\s*security\s+(?:framework|policy)',
                r'information\s+security\s+(?:management|policy)',
                r'ISO\s+27001\s+(?:compliance|certification)',
                r'NIST\s+(?:cybersecurity\s+)?framework',
                r'security\s+incident\s+(?:response|management)',
                r'SIEM\s+(?:system|monitoring)',
                r'vulnerability\s+(?:management|assessment)',
                r'penetration\s+test(?:ing)?',
                r'security\s+awareness\s+(?:training|program)',
                r'access\s+control\s+(?:policy|management)',
                r'multi[- ]factor\s+authentication',
                r'MFA\s+(?:implementation|requirement)',
                r'encryption\s+(?:policy|requirement)',
                r'data\s+loss\s+prevention',
                r'DLP\s+(?:solution|policy)',
                r'endpoint\s+(?:protection|security)',
                r'network\s+security\s+(?:architecture|policy)',
                r'security\s+operations\s+center',
                r'SOC\s+(?:monitoring|operations)'
            ]
        }
    
    def analyze_pdf_collection(self, 
                             pdf_directory: str,
                             analysis_type: str = "Full Compliance Scan",
                             frameworks: List[str] = None,
                             max_documents: int = 1000,
                             analysis_depth: int = 3) -> Dict:
        """
        Analyze a collection of PDF documents for compliance issues
        
        Args:
            pdf_directory: Path to directory containing PDF files
            analysis_type: Type of analysis to perform
            frameworks: List of compliance frameworks to check
            max_documents: Maximum number of documents to analyze
            analysis_depth: Depth of analysis (1-5)
        
        Returns:
            Analysis results dictionary
        """
        if not PDF_AVAILABLE:
            raise ImportError("PDF processing libraries not available. Install PyPDF2 and PyMuPDF.")
        
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        frameworks = frameworks or ['aml_cft', 'sanctions', 'gdpr']
        
        self.logger.info(f"Starting compliance analysis {analysis_id}")
        
        # Get PDF files
        pdf_files = []
        if os.path.exists(pdf_directory):
            pdf_files = [
                os.path.join(pdf_directory, f) 
                for f in os.listdir(pdf_directory) 
                if f.lower().endswith('.pdf')
            ][:max_documents]
        
        total_documents = len(pdf_files)
        
        # Initialize analysis record
        self._save_analysis_record(analysis_id, analysis_type, total_documents, frameworks)
        
        # Process documents
        processed_documents = 0
        total_findings = []
        total_entities = []
        risk_scores = []
        
        for pdf_file in pdf_files:
            try:
                document_result = self._analyze_single_pdf(
                    pdf_file, analysis_id, frameworks, analysis_depth
                )
                
                if document_result:
                    total_findings.extend(document_result['findings'])
                    total_entities.extend(document_result['entities'])
                    if document_result['risk_score'] > 0:
                        risk_scores.append(document_result['risk_score'])
                    
                    processed_documents += 1
                    
            except Exception as e:
                self.logger.error(f"Failed to analyze {pdf_file}: {str(e)}")
        
        # Calculate final statistics
        compliance_issues = len([f for f in total_findings if f['risk_level'] in ['HIGH', 'MEDIUM']])
        high_risk_items = len([f for f in total_findings if f['risk_level'] == 'HIGH'])
        avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0
        
        # Update analysis record
        self._update_analysis_record(
            analysis_id, processed_documents, compliance_issues, 
            high_risk_items, avg_risk_score
        )
        
        # Prepare results
        analysis_result = {
            'analysis_id': analysis_id,
            'type': analysis_type,
            'timestamp': datetime.now().isoformat(),
            'frameworks': frameworks,
            'stats': {
                'total_documents': total_documents,
                'documents_processed': processed_documents,
                'compliance_issues': compliance_issues,
                'high_risk_items': high_risk_items,
                'avg_risk_score': round(avg_risk_score, 2)
            },
            'findings': self._summarize_findings(total_findings)[:10],  # Top 10 findings
            'entities': self._summarize_entities(total_entities)[:20],  # Top 20 entities
            'risk_breakdown': self._calculate_risk_breakdown(total_findings),
            'framework_coverage': self._calculate_framework_coverage(total_findings, frameworks)
        }
        
        self.logger.info(f"Completed analysis {analysis_id}: {processed_documents}/{total_documents} documents processed")
        
        return analysis_result
    
    def _analyze_single_pdf(self, pdf_path: str, analysis_id: str, 
                           frameworks: List[str], depth: int) -> Optional[Dict]:
        """Analyze a single PDF document"""
        try:
            # Extract text from PDF
            text_content = self._extract_pdf_text(pdf_path)
            if not text_content or len(text_content.strip()) < 100:
                return None
            
            # Get document metadata
            file_size = os.path.getsize(pdf_path)
            document_name = os.path.basename(pdf_path)
            word_count = len(text_content.split())
            
            # Extract page count
            page_count = self._get_pdf_page_count(pdf_path)
            
            # Analyze compliance patterns
            findings = []
            overall_risk_score = 0.0
            
            for framework in frameworks:
                if framework in self.compliance_patterns:
                    framework_findings = self._detect_compliance_issues(
                        text_content, framework, document_name
                    )
                    findings.extend(framework_findings)
                    
                    # Calculate risk contribution
                    framework_risk = sum(f['risk_score'] for f in framework_findings)
                    overall_risk_score += framework_risk * self.risk_weights.get(framework, 1.0)
            
            # Extract entities (simplified)
            entities = self._extract_entities(text_content, document_name)
            
            # Save findings to database
            self._save_document_findings(
                analysis_id, pdf_path, document_name, file_size, 
                page_count, word_count, findings
            )
            
            self._save_extracted_entities(analysis_id, document_name, entities)
            
            return {
                'document_name': document_name,
                'findings': findings,
                'entities': entities,
                'risk_score': min(overall_risk_score, 10.0),  # Cap at 10
                'word_count': word_count,
                'page_count': page_count
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing {pdf_path}: {str(e)}")
            return None
    
    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text content from PDF"""
        text_content = ""
        
        try:
            # Try PyMuPDF first (better text extraction)
            if 'fitz' in sys.modules:
                doc = fitz.open(pdf_path)
                for page in doc:
                    text_content += page.get_text()
                doc.close()
            else:
                # Fallback to PyPDF2
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text_content += page.extract_text()
                        
        except Exception as e:
            self.logger.error(f"Failed to extract text from {pdf_path}: {str(e)}")
            
        return text_content
    
    def _get_pdf_page_count(self, pdf_path: str) -> int:
        """Get number of pages in PDF"""
        try:
            if 'fitz' in sys.modules:
                doc = fitz.open(pdf_path)
                page_count = doc.page_count
                doc.close()
                return page_count
            else:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    return len(pdf_reader.pages)
        except:
            return 0
    
    def _detect_compliance_issues(self, text: str, framework: str, 
                                 document_name: str) -> List[Dict]:
        """Detect compliance issues in text using patterns"""
        findings = []
        patterns = self.compliance_patterns.get(framework, [])
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Calculate risk score based on context
                context = text[max(0, match.start()-100):match.end()+100]
                risk_score = self._calculate_risk_score(match.group(), context, framework)
                risk_level = self._get_risk_level(risk_score)
                
                finding = {
                    'framework': framework,
                    'type': framework.upper().replace('_', '/'),
                    'description': f"Potential {framework.replace('_', ' ').title()} compliance issue detected",
                    'matched_text': match.group(),
                    'context': context,
                    'risk_level': risk_level,
                    'risk_score': risk_score,
                    'confidence_score': 0.8,  # Base confidence
                    'document': document_name,
                    'position': match.start()
                }
                findings.append(finding)
        
        return findings
    
    def _calculate_risk_score(self, matched_text: str, context: str, framework: str) -> float:
        """Calculate risk score for a finding"""
        base_score = 2.0
        
        # Adjust based on framework importance
        framework_multiplier = self.risk_weights.get(framework, 1.0) / 3.0
        
        # Adjust based on context keywords
        high_risk_keywords = ['violation', 'breach', 'non-compliance', 'failure', 'risk', 'alert']
        medium_risk_keywords = ['requirement', 'must', 'shall', 'mandatory', 'critical']
        
        context_lower = context.lower()
        
        for keyword in high_risk_keywords:
            if keyword in context_lower:
                base_score += 1.5
                
        for keyword in medium_risk_keywords:
            if keyword in context_lower:
                base_score += 0.8
        
        # Adjust based on matched text specificity
        if len(matched_text.split()) > 3:
            base_score += 0.5
            
        return min(base_score * framework_multiplier, 5.0)
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level"""
        if risk_score >= 4.0:
            return "HIGH"
        elif risk_score >= 2.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _extract_entities(self, text: str, document_name: str) -> List[Dict]:
        """Extract named entities from text (simplified)"""
        entities = []
        
        # Simple entity patterns
        entity_patterns = {
            'PERSON': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            'ORGANIZATION': r'\b[A-Z][A-Z\s&]{2,30}\b',
            'MONEY': r'\$[\d,]+(?:\.\d{2})?|\b\d+\s*(?:USD|EUR|GBP|million|billion)\b',
            'DATE': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
        }
        
        for entity_type, pattern in entity_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append({
                    'type': entity_type,
                    'text': match.group().strip(),
                    'label': entity_type,
                    'confidence': 0.7,
                    'context': text[max(0, match.start()-50):match.end()+50],
                    'document': document_name
                })
        
        return entities[:50]  # Limit to top 50 entities per document
    
    def _save_analysis_record(self, analysis_id: str, analysis_type: str, 
                             total_documents: int, frameworks: List[str]):
        """Save analysis record to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO compliance_analysis 
            (analysis_id, analysis_type, total_documents, frameworks, status)
            VALUES (?, ?, ?, ?, ?)
        """, (analysis_id, analysis_type, total_documents, json.dumps(frameworks), 'running'))
        
        conn.commit()
        conn.close()
    
    def _update_analysis_record(self, analysis_id: str, processed_documents: int,
                               compliance_issues: int, high_risk_items: int, 
                               avg_risk_score: float):
        """Update analysis record with results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE compliance_analysis 
            SET processed_documents = ?, compliance_issues = ?, 
                high_risk_items = ?, avg_risk_score = ?, status = 'completed'
            WHERE analysis_id = ?
        """, (processed_documents, compliance_issues, high_risk_items, 
              avg_risk_score, analysis_id))
        
        conn.commit()
        conn.close()
    
    def _save_document_findings(self, analysis_id: str, document_path: str,
                               document_name: str, file_size: int, page_count: int,
                               word_count: int, findings: List[Dict]):
        """Save document findings to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for finding in findings:
            cursor.execute("""
                INSERT INTO document_findings 
                (analysis_id, document_path, document_name, file_size, page_count, 
                 word_count, compliance_framework, finding_type, finding_description,
                 risk_level, risk_score, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id, document_path, document_name, file_size, page_count,
                word_count, finding['framework'], finding['type'], 
                finding['description'], finding['risk_level'], finding['risk_score'],
                finding['confidence_score']
            ))
        
        conn.commit()
        conn.close()
    
    def _save_extracted_entities(self, analysis_id: str, document_name: str, 
                                entities: List[Dict]):
        """Save extracted entities to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for entity in entities:
            cursor.execute("""
                INSERT INTO extracted_entities 
                (analysis_id, document_name, entity_type, entity_text, 
                 entity_label, confidence_score, context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id, document_name, entity['type'], entity['text'],
                entity['label'], entity['confidence'], entity['context']
            ))
        
        conn.commit()
        conn.close()
    
    def _summarize_findings(self, findings: List[Dict]) -> List[Dict]:
        """Summarize and prioritize findings"""
        # Sort by risk score
        sorted_findings = sorted(findings, key=lambda x: x['risk_score'], reverse=True)
        
        # Group similar findings
        summarized = []
        seen_types = set()
        
        for finding in sorted_findings:
            finding_key = f"{finding['framework']}_{finding['type']}"
            if finding_key not in seen_types:
                summarized.append(finding)
                seen_types.add(finding_key)
        
        return summarized
    
    def _summarize_entities(self, entities: List[Dict]) -> List[Dict]:
        """Summarize extracted entities"""
        # Count entity occurrences
        entity_counts = Counter()
        entity_details = {}
        
        for entity in entities:
            key = f"{entity['type']}:{entity['text']}"
            entity_counts[key] += 1
            if key not in entity_details:
                entity_details[key] = entity
        
        # Return most frequent entities
        summarized = []
        for (entity_key, count) in entity_counts.most_common(20):
            entity = entity_details[entity_key].copy()
            entity['frequency'] = count
            summarized.append(entity)
        
        return summarized
    
    def _calculate_risk_breakdown(self, findings: List[Dict]) -> Dict:
        """Calculate risk breakdown by framework and level"""
        breakdown = {}
        
        for finding in findings:
            framework = finding['framework']
            risk_level = finding['risk_level']
            
            if framework not in breakdown:
                breakdown[framework] = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            
            breakdown[framework][risk_level] += 1
        
        return breakdown
    
    def _calculate_framework_coverage(self, findings: List[Dict], 
                                    frameworks: List[str]) -> Dict:
        """Calculate coverage percentage for each framework"""
        coverage = {}
        
        for framework in frameworks:
            framework_findings = [f for f in findings if f['framework'] == framework]
            # Simple coverage calculation based on findings count
            coverage[framework] = min(len(framework_findings) * 10, 100)  # Cap at 100%
        
        return coverage
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict]:
        """Get recent analysis history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM compliance_analysis 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'analysis_id': row[1],
                'type': row[2],
                'timestamp': row[3],
                'total_documents': row[4],
                'processed_documents': row[5],
                'compliance_issues': row[6],
                'high_risk_items': row[7],
                'avg_risk_score': row[8],
                'frameworks': json.loads(row[9]) if row[9] else [],
                'status': row[10]
            })
        
        conn.close()
        return results
    
    def get_analysis_details(self, analysis_id: str) -> Optional[Dict]:
        """Get detailed analysis results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get analysis record
        cursor.execute("""
            SELECT * FROM compliance_analysis WHERE analysis_id = ?
        """, (analysis_id,))
        
        analysis_row = cursor.fetchone()
        if not analysis_row:
            conn.close()
            return None
        
        # Get findings
        cursor.execute("""
            SELECT * FROM document_findings WHERE analysis_id = ?
            ORDER BY risk_score DESC
        """, (analysis_id,))
        
        findings = []
        for row in cursor.fetchall():
            findings.append({
                'document_name': row[3],
                'framework': row[7],
                'type': row[8],
                'description': row[9],
                'risk_level': row[10],
                'risk_score': row[11],
                'confidence_score': row[13]
            })
        
        # Get entities
        cursor.execute("""
            SELECT * FROM extracted_entities WHERE analysis_id = ?
            ORDER BY confidence_score DESC
        """, (analysis_id,))
        
        entities = []
        for row in cursor.fetchall():
            entities.append({
                'document_name': row[2],
                'type': row[3],
                'text': row[4],
                'label': row[5],
                'confidence': row[6]
            })
        
        conn.close()
        
        return {
            'analysis_id': analysis_row[1],
            'type': analysis_row[2],
            'timestamp': analysis_row[3],
            'stats': {
                'total_documents': analysis_row[4],
                'processed_documents': analysis_row[5],
                'compliance_issues': analysis_row[6],
                'high_risk_items': analysis_row[7],
                'avg_risk_score': analysis_row[8]
            },
            'frameworks': json.loads(analysis_row[9]) if analysis_row[9] else [],
            'status': analysis_row[10],
            'findings': findings,
            'entities': entities
        }
    
    def get_sanctions_statistics(self) -> Dict:
        """Get analysis statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count total analyses
            cursor.execute("SELECT COUNT(*) FROM compliance_analysis")
            total_analyses = cursor.fetchone()[0]
            
            # Count findings by framework
            cursor.execute("""
                SELECT compliance_framework, COUNT(*) 
                FROM document_findings 
                GROUP BY compliance_framework
            """)
            framework_counts = dict(cursor.fetchall())
            
            # Count entities
            cursor.execute("SELECT COUNT(*) FROM extracted_entities")
            total_entities = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_analyses': total_analyses,
                'total_sanctions_entities': sum(framework_counts.values()),
                'framework_breakdown': framework_counts,
                'extracted_entities': total_entities,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'total_analyses': 0,
                'total_sanctions_entities': 0,
                'framework_breakdown': {},
                'extracted_entities': 0,
                'error': str(e)
            }
