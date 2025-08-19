"""
PDF Processing Service for Entity Extraction and Database Ingestion
Processes all PDF files in data folder and extracts searchable entities
"""

import os
import sys
import asyncio
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib
import json
from dataclasses import dataclass, asdict

# PDF processing libraries
try:
    import PyPDF2
    import pdfplumber
except ImportError as e:
    print(f"Basic PDF processing libraries not installed: {e}")
    print("Run: pip install PyPDF2 pdfplumber")

# Try to import pdfminer separately with better error handling
try:
    from pdfminer.high_level import extract_text
    from pdfminer.layout import LAParams
except ImportError as e:
    print(f"pdfminer not available: {e}")
    extract_text = None
    LAParams = None

# NLP and entity extraction
try:
    import spacy
    import re
    from collections import Counter
except ImportError:
    print("NLP libraries not installed. Run: pip install spacy")
    sys.exit(1)

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

@dataclass
class PDFDocument:
    """PDF document metadata"""
    file_path: str
    file_name: str
    file_size: int
    file_hash: str
    processed_date: datetime
    page_count: int
    text_length: int
    extraction_method: str

@dataclass
class ExtractedEntity:
    """Extracted entity from PDF"""
    document_id: str
    entity_text: str
    entity_type: str
    confidence: float
    page_number: int
    context: str
    start_char: int
    end_char: int

class PDFProcessor:
    """
    Comprehensive PDF processing service for entity extraction
    """
    
    def __init__(self, data_folder: str = None):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
        # Set data folder
        if data_folder is None:
            self.data_folder = Path(project_root) / "data"
        else:
            self.data_folder = Path(data_folder)
        
        # Database setup
        self.db_path = self.data_folder / "processed_documents.db"
        
        # Initialize NLP model
        self.nlp = None
        self._init_nlp_model()
        
        # Entity patterns for regex extraction
        self.entity_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            'amount': r'\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|PKR)\b',
            'account': r'\b\d{10,18}\b',
            'swift': r'\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b',
            'case_number': r'\b(?:case|file|ref|reference)\s*[#:]?\s*[A-Z0-9-]{5,20}\b',
            'license': r'\b[A-Z]{2,5}[-\s]?\d{4,10}\b'
        }
        
        self._init_database()
        self.logger.info(f"Initialized PDF processor for folder: {self.data_folder}")
    
    def _init_nlp_model(self):
        """Initialize spaCy NLP model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.logger.info("Loaded spaCy English model")
        except OSError:
            self.logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def _init_database(self):
        """Initialize SQLite database for storing processed documents and entities"""
        os.makedirs(self.data_folder, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                file_size INTEGER,
                file_hash TEXT UNIQUE,
                processed_date TIMESTAMP,
                page_count INTEGER,
                text_length INTEGER,
                extraction_method TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Entities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                entity_text TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                confidence REAL,
                page_number INTEGER,
                context TEXT,
                start_char INTEGER,
                end_char INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        # Full text search table
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS document_fts USING fts5(
                document_id,
                content,
                content='',
                contentless_delete=1
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_text ON entities(entity_text)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(file_hash)')
        
        conn.commit()
        conn.close()
        
        self.logger.info("Database initialized successfully")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _extract_text_pypdf2(self, file_path: Path) -> Tuple[str, int]:
        """Extract text using PyPDF2"""
        text = ""
        page_count = 0
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    try:
                        text += page.extract_text() + "\n"
                    except Exception as e:
                        self.logger.warning(f"Error extracting page: {e}")
                        continue
        except Exception as e:
            self.logger.error(f"PyPDF2 extraction failed for {file_path}: {e}")
            
        return text, page_count
    
    def _extract_text_pdfplumber(self, file_path: Path) -> Tuple[str, int]:
        """Extract text using pdfplumber (better for tables)"""
        text = ""
        page_count = 0
        
        try:
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                
                for page in pdf.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                        
                        # Extract tables if present
                        tables = page.extract_tables()
                        for table in tables:
                            for row in table:
                                if row:
                                    text += " | ".join([cell or "" for cell in row]) + "\n"
                                    
                    except Exception as e:
                        self.logger.warning(f"Error extracting page: {e}")
                        continue
        except Exception as e:
            self.logger.error(f"pdfplumber extraction failed for {file_path}: {e}")
            
        return text, page_count
    
    def _extract_text_pdfminer(self, file_path: Path) -> Tuple[str, int]:
        """Extract text using pdfminer (most robust)"""
        text = ""
        page_count = 0
        
        if extract_text is None:
            return text, page_count
            
        try:
            laparams = LAParams() if LAParams else None
            text = extract_text(str(file_path), laparams=laparams)
            
            # Count pages by opening with PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    page_count = len(pdf_reader.pages)
            except:
                page_count = 1
                
        except Exception as e:
            self.logger.error(f"pdfminer extraction failed for {file_path}: {e}")
            
        return text, page_count
    
    def extract_text_from_pdf(self, file_path: Path) -> Tuple[str, int, str]:
        """Extract text using multiple methods, return best result"""
        methods = [
            ("pdfminer", self._extract_text_pdfminer),
            ("pdfplumber", self._extract_text_pdfplumber),
            ("pypdf2", self._extract_text_pypdf2)
        ]
        
        best_text = ""
        best_pages = 0
        best_method = "none"
        
        for method_name, method_func in methods:
            try:
                text, pages = method_func(file_path)
                if len(text.strip()) > len(best_text.strip()):
                    best_text = text
                    best_pages = pages
                    best_method = method_name
            except Exception as e:
                self.logger.warning(f"{method_name} failed: {e}")
                continue
        
        return best_text, best_pages, best_method
    
    def extract_entities_regex(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using regex patterns"""
        entities = []
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    'text': match.group(),
                    'type': entity_type,
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.8
                })
        
        return entities
    
    def extract_entities_spacy(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using spaCy NLP"""
        entities = []
        
        if self.nlp is None:
            return entities
            
        try:
            doc = self.nlp(text[:1000000])  # Limit text length
            
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'type': ent.label_.lower(),
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': 0.9
                })
        except Exception as e:
            self.logger.error(f"spaCy entity extraction failed: {e}")
            
        return entities
    
    def process_pdf(self, file_path: Path) -> Optional[int]:
        """Process a single PDF file"""
        try:
            # Check if already processed
            file_hash = self._calculate_file_hash(file_path)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM documents WHERE file_hash = ?", (file_hash,))
            existing = cursor.fetchone()
            
            if existing:
                self.logger.info(f"File already processed: {file_path.name}")
                conn.close()
                return existing[0]
            
            # Extract text
            text, page_count, method = self.extract_text_from_pdf(file_path)
            
            if not text.strip():
                self.logger.warning(f"No text extracted from {file_path.name}")
                conn.close()
                return None
            
            # Insert document record
            doc_data = (
                str(file_path), file_path.name, file_path.stat().st_size, file_hash,
                datetime.now(), page_count, len(text), method, 'completed'
            )
            
            cursor.execute('''
                INSERT INTO documents (file_path, file_name, file_size, file_hash, 
                                     processed_date, page_count, text_length, extraction_method, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', doc_data)
            
            doc_id = cursor.lastrowid
            
            # Extract entities
            regex_entities = self.extract_entities_regex(text)
            spacy_entities = self.extract_entities_spacy(text)
            
            all_entities = regex_entities + spacy_entities
            
            # Insert entities
            for entity in all_entities:
                context_start = max(0, entity['start'] - 100)
                context_end = min(len(text), entity['end'] + 100)
                context = text[context_start:context_end]
                
                cursor.execute('''
                    INSERT INTO entities (document_id, entity_text, entity_type, confidence,
                                        page_number, context, start_char, end_char)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (doc_id, entity['text'], entity['type'], entity['confidence'],
                      1, context, entity['start'], entity['end']))
            
            # Insert full text for search
            cursor.execute('''
                INSERT INTO document_fts (document_id, content)
                VALUES (?, ?)
            ''', (doc_id, text))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Processed {file_path.name}: {len(all_entities)} entities extracted")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            return None
    
    def process_all_pdfs(self) -> Dict[str, Any]:
        """Process all PDF files in the data folder"""
        pdf_files = list(self.data_folder.glob("**/*.pdf"))
        
        if not pdf_files:
            self.logger.warning(f"No PDF files found in {self.data_folder}")
            return {'processed': 0, 'failed': 0, 'total': 0}
        
        processed = 0
        failed = 0
        
        for pdf_file in pdf_files:
            self.logger.info(f"Processing: {pdf_file.name}")
            result = self.process_pdf(pdf_file)
            
            if result:
                processed += 1
            else:
                failed += 1
        
        summary = {
            'processed': processed,
            'failed': failed,
            'total': len(pdf_files)
        }
        
        self.logger.info(f"Processing complete: {summary}")
        return summary
    
    def search_entities(self, query: str, entity_type: str = None) -> List[Dict[str, Any]]:
        """Search for entities in processed documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if entity_type:
            cursor.execute('''
                SELECT e.entity_text, e.entity_type, e.confidence, d.file_name, e.context
                FROM entities e
                JOIN documents d ON e.document_id = d.id
                WHERE e.entity_text LIKE ? AND e.entity_type = ?
                ORDER BY e.confidence DESC
            ''', (f"%{query}%", entity_type))
        else:
            cursor.execute('''
                SELECT e.entity_text, e.entity_type, e.confidence, d.file_name, e.context
                FROM entities e
                JOIN documents d ON e.document_id = d.id
                WHERE e.entity_text LIKE ?
                ORDER BY e.confidence DESC
            ''', (f"%{query}%",))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'entity_text': row[0],
                'entity_type': row[1],
                'confidence': row[2],
                'document': row[3],
                'context': row[4]
            })
        
        conn.close()
        return results

if __name__ == "__main__":
    processor = PDFProcessor()
    summary = processor.process_all_pdfs()
    print(f"Processing summary: {summary}")