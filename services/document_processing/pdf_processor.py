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
    # Try different import paths for LAParams based on pdfminer version
    LAParams = None
    try:
        from pdfminer.layout import LAParams
    except ImportError:
        try:
            from pdfminer.pdfinterp import LAParams  
        except ImportError:
            try:
                # from pdfminer.converter import LAParams  # Removed: not available in pdfminer.converter
            except ImportError:
                try:
                    from pdfminer.pdfpage import LAParams
                except ImportError:
                    # Create a simple fallback class if LAParams not found
                    class LAParams:
                        def __init__(self, line_margin=0.5, word_margin=0.1, char_margin=2.0, boxes_flow=0.5):
                            self.line_margin = line_margin
                            self.word_margin = word_margin
                            self.char_margin = char_margin
                            self.boxes_flow = boxes_flow
except ImportError as e:
    print(f"pdfminer not available: {e}")
    print("Run: pip install pdfminer.six")
    # Set fallback variables
    extract_text = None
    LAParams = None

# NLP and entity extraction
try:
    import spacy
    import re
    from collections import Counter
except ImportError:
    print("NLP libraries not installed. Run: pip install spacy")
    print("Also run: python -m spacy download en_core_web_sm")
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
            'account': r'\b\d{10,18}\b',  # Bank account numbers
            'swift': r'\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b',  # SWIFT codes
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
    def _extract_text_pdfminer(self, file_path: Path) -> Tuple[str, int]:
        """Extract text using pdfminer (most robust)"""
        if extract_text is None or LAParams is None:
            self.logger.warning("pdfminer not available, skipping pdfminer extraction")
            return "", 0
            
        try:
            laparams = LAParams(
                line_margin=0.5,
                word_margin=0.1,
                char_margin=2.0,
                boxes_flow=0.5
            )
            text = extract_text(str(file_path), laparams=laparams)
            
            # Estimate page count (rough approximation)
            page_count = max(1, text.count('\f') + 1)
            
            return text, page_count
        except Exception as e:
            self.logger.error(f"pdfminer extraction failed for {file_path}: {e}")
            return "", 0
        except Exception as e:
            self.logger.error(f"pdfminer extraction failed for {file_path}: {e}")
            return "", 0
    
    def extract_text_from_pdf(self, file_path: Path) -> Tuple[str, int, str]:
        """Extract text from PDF using multiple methods"""
        methods = [
            ("pdfplumber", self._extract_text_pdfplumber),
            ("pdfminer", self._extract_text_pdfminer),
            ("pypdf2", self._extract_text_pypdf2)
        ]
        
        for method_name, method_func in methods:
            try:
                text, page_count = method_func(file_path)
                if text and len(text.strip()) > 100:  # Minimum viable text
                    self.logger.debug(f"Successfully extracted text using {method_name}")
                    return text, page_count, method_name
            except Exception as e:
                self.logger.warning(f"Method {method_name} failed: {e}")
                continue
        
        self.logger.error(f"All extraction methods failed for {file_path}")
        return "", 0, "failed"
    
    def extract_entities_regex(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using regex patterns"""
        entities = []
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity = {
                    'text': match.group().strip(),
                    'type': entity_type,
                    'confidence': 0.8,  # Regex confidence
                    'start': match.start(),
                    'end': match.end(),
                    'context': text[max(0, match.start()-50):match.end()+50]
                }
                entities.append(entity)
        
        return entities
    
    def extract_entities_spacy(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using spaCy NLP"""
        entities = []
        
        if not self.nlp:
            return entities
        
        try:
            # Process text in chunks to avoid memory issues
            chunk_size = 1000000  # 1MB chunks
            
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                doc = self.nlp(chunk)
                
                for ent in doc.ents:
                    entity = {
                        'text': ent.text.strip(),
                        'type': ent.label_.lower(),
                        'confidence': 0.9,  # spaCy confidence
                        'start': ent.start_char + i,
                        'end': ent.end_char + i,
                        'context': text[max(0, ent.start_char + i - 50):ent.end_char + i + 50]
                    }
                    entities.append(entity)
                    
        except Exception as e:
            self.logger.warning(f"spaCy entity extraction failed: {e}")
        
        return entities
    
    def extract_custom_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract domain-specific entities for compliance"""
        entities = []
        
        # Compliance-specific patterns
        compliance_patterns = {
            'corruption_case': r'\b(?:corruption|bribery|kickback|embezzlement)\s+case\s+[A-Z0-9-]{3,20}\b',
            'sanctions_list': r'\b(?:OFAC|SDN|sanctions|blacklist|watchlist)\b',
            'investigation_id': r'\b(?:investigation|inquiry|probe)\s+[#:]?\s*[A-Z0-9-]{5,20}\b',
            'regulatory_code': r'\b[A-Z]{2,5}[-\s]?\d{3,8}[-\s]?[A-Z0-9]{0,5}\b',
            'court_case': r'\b(?:civil|criminal)\s+case\s+no[.:]?\s*[A-Z0-9/-]{5,20}\b',
            'license_number': r'\b(?:license|permit|registration)\s+no[.:]?\s*[A-Z0-9-]{5,20}\b'
        }
        
        for entity_type, pattern in compliance_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity = {
                    'text': match.group().strip(),
                    'type': entity_type,
                    'confidence': 0.85,
                    'start': match.start(),
                    'end': match.end(),
                    'context': text[max(0, match.start()-50):match.end()+50]
                }
                entities.append(entity)
        
        return entities
    
    def process_pdf_file(self, file_path: Path) -> bool:
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
                return True
            
            self.logger.info(f"Processing PDF: {file_path.name}")
            
            # Extract text
            text, page_count, method = self.extract_text_from_pdf(file_path)
            
            if not text:
                self.logger.error(f"No text extracted from {file_path.name}")
                conn.close()
                return False
            
            # Create document record
            doc_data = PDFDocument(
                file_path=str(file_path),
                file_name=file_path.name,
                file_size=file_path.stat().st_size,
                file_hash=file_hash,
                processed_date=datetime.now(),
                page_count=page_count,
                text_length=len(text),
                extraction_method=method
            )
            
            # Insert document
            cursor.execute('''
                INSERT INTO documents 
                (file_path, file_name, file_size, file_hash, processed_date, 
                 page_count, text_length, extraction_method, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'completed')
            ''', (
                doc_data.file_path, doc_data.file_name, doc_data.file_size,
                doc_data.file_hash, doc_data.processed_date, doc_data.page_count,
                doc_data.text_length, doc_data.extraction_method
            ))
            
            document_id = cursor.lastrowid
            
            # Extract entities using all methods
            all_entities = []
            all_entities.extend(self.extract_entities_regex(text))
            all_entities.extend(self.extract_entities_spacy(text))
            all_entities.extend(self.extract_custom_entities(text))
            
            # Deduplicate entities
            unique_entities = []
            seen = set()
            
            for entity in all_entities:
                key = (entity['text'].lower(), entity['type'])
                if key not in seen:
                    seen.add(key)
                    unique_entities.append(entity)
            
            # Insert entities
            for entity in unique_entities:
                cursor.execute('''
                    INSERT INTO entities 
                    (document_id, entity_text, entity_type, confidence, page_number, 
                     context, start_char, end_char)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    document_id, entity['text'], entity['type'], entity['confidence'],
                    1, entity['context'], entity['start'], entity['end']
                ))
            
            # Insert full text for search
            cursor.execute('''
                INSERT INTO document_fts (document_id, content) VALUES (?, ?)
            ''', (document_id, text))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Successfully processed {file_path.name}: "
                           f"{len(unique_entities)} entities extracted")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            return False
    
    def find_pdf_files(self) -> List[Path]:
        """Find all PDF files in data folder"""
        pdf_files = []
        
        # Search in main data folder and subdirectories
        for root, dirs, files in os.walk(self.data_folder):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(Path(root) / file)
        
        self.logger.info(f"Found {len(pdf_files)} PDF files")
        return pdf_files
    
    async def process_all_pdfs(self, max_workers: int = 4) -> Dict[str, Any]:
        """Process all PDF files in parallel"""
        pdf_files = self.find_pdf_files()
        
        if not pdf_files:
            self.logger.warning("No PDF files found")
            return {"processed": 0, "failed": 0, "total": 0}
        
        self.logger.info(f"Starting to process {len(pdf_files)} PDF files")
        
        processed = 0
        failed = 0
        
        # Process files in batches to avoid overwhelming the system
        batch_size = max_workers
        
        for i in range(0, len(pdf_files), batch_size):
            batch = pdf_files[i:i + batch_size]
            
            # Process batch
            for pdf_file in batch:
                try:
                    success = self.process_pdf_file(pdf_file)
                    if success:
                        processed += 1
                    else:
                        failed += 1
                except Exception as e:
                    self.logger.error(f"Failed to process {pdf_file}: {e}")
                    failed += 1
            
            # Log progress
            progress = ((i + len(batch)) / len(pdf_files)) * 100
            self.logger.info(f"Progress: {progress:.1f}% ({processed} processed, {failed} failed)")
        
        results = {
            "processed": processed,
            "failed": failed,
            "total": len(pdf_files),
            "success_rate": (processed / len(pdf_files)) * 100 if pdf_files else 0
        }
        
        self.logger.info(f"Processing complete: {results}")
        return results
    
    def search_entities(self, query: str, entity_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Search for entities in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = '''
            SELECT e.entity_text, e.entity_type, e.confidence, e.context,
                   d.file_name, d.file_path
            FROM entities e
            JOIN documents d ON e.document_id = d.id
            WHERE e.entity_text LIKE ?
        '''
        params = [f"%{query}%"]
        
        if entity_type:
            sql += " AND e.entity_type = ?"
            params.append(entity_type)
        
        sql += " ORDER BY e.confidence DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "entity_text": row[0],
                "entity_type": row[1],
                "confidence": row[2],
                "context": row[3],
                "file_name": row[4],
                "file_path": row[5]
            }
            for row in results
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Document stats
        cursor.execute("SELECT COUNT(*), SUM(page_count), SUM(text_length) FROM documents")
        doc_stats = cursor.fetchone()
        
        # Entity stats
        cursor.execute("""
            SELECT entity_type, COUNT(*) 
            FROM entities 
            GROUP BY entity_type 
            ORDER BY COUNT(*) DESC
        """)
        entity_types = cursor.fetchall()
        
        # Processing methods
        cursor.execute("""
            SELECT extraction_method, COUNT(*) 
            FROM documents 
            GROUP BY extraction_method
        """)
        methods = cursor.fetchall()
        
        conn.close()
        
        return {
            "documents": {
                "total": doc_stats[0] or 0,
                "total_pages": doc_stats[1] or 0,
                "total_text_length": doc_stats[2] or 0
            },
            "entities": {
                "by_type": dict(entity_types),
                "total": sum(count for _, count in entity_types)
            },
            "extraction_methods": dict(methods),
            "database_path": str(self.db_path)
        }

# CLI interface
async def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PDF Processing Service")
    parser.add_argument("--data-folder", help="Path to data folder", default=None)
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum parallel workers")
    parser.add_argument("--search", help="Search for entities")
    parser.add_argument("--entity-type", help="Filter by entity type")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    args = parser.parse_args()
    
    processor = PDFProcessor(args.data_folder)
    
    if args.stats:
        stats = processor.get_statistics()
        print("\n=== PDF Processing Statistics ===")
        print(f"Documents: {stats['documents']['total']}")
        print(f"Total Pages: {stats['documents']['total_pages']}")
        print(f"Total Entities: {stats['entities']['total']}")
        print("\nEntity Types:")
        for entity_type, count in stats['entities']['by_type'].items():
            print(f"  {entity_type}: {count}")
        print("\nExtraction Methods:")
        for method, count in stats['extraction_methods'].items():
            print(f"  {method}: {count}")
    
    elif args.search:
        results = processor.search_entities(args.search, args.entity_type)
        print(f"\n=== Search Results for '{args.search}' ===")
        for result in results[:20]:  # Show top 20
            print(f"Entity: {result['entity_text']}")
            print(f"Type: {result['entity_type']}")
            print(f"File: {result['file_name']}")
            print(f"Context: {result['context'][:100]}...")
            print("-" * 50)
    
    else:
        print("Starting PDF processing...")
        results = await processor.process_all_pdfs(args.max_workers)
        print(f"\nProcessing Results:")
        print(f"  Processed: {results['processed']}")
        print(f"  Failed: {results['failed']}")
        print(f"  Success Rate: {results['success_rate']:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())
