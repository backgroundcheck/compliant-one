#!/usr/bin/env python3
"""
Batch PDF Processor for Compliant.one Platform
Processes all PDF files in data folder and extracts entities to searchable database
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import re
from collections import Counter

# Add project root to path (this file lives at the project root)
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.logger import get_logger

# Try to import OCR service
try:
    from services.ocr.ocr_service import OCRService
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("OCR service not available - install dependencies for scanned PDF support")

class BatchPDFProcessor:
    """
    Batch processor for all PDFs in data folder
    """
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize OCR service if available
        self.ocr_service = None
        if OCR_AVAILABLE:
            try:
                self.ocr_service = OCRService()
                self.logger.info("OCR service initialized for scanned PDF support")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OCR service: {e}")
        # Paths
        # Use repository root (directory containing this file)
        self.project_root = Path(__file__).parent
        self.data_folder = self.project_root / "data"
        self.pdf_folders = [
            self.data_folder / "pdfs" / "downloaded_pdfs",
            self.data_folder / "documents",
            self.data_folder / "uploads",
        ]

        # Database paths
        self.main_db = self.data_folder / "entities.db"
        self.legacy_db = self.data_folder / "legacy_data" / "documents.db"

        # Entity extraction patterns
        self.entity_patterns = {
            'person_name': r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',
            'organization': r'\b(?:Ltd|LLC|Inc|Corp|Company|Bank|Institute|Commission|Authority|Bureau|Agency)\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            'amount': r'\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|PKR)\b',
            'case_number': r'\b(?:case|file|ref|reference)\s*[#:]?\s*[A-Z0-9-]{5,20}\b',
            'court_case': r'\b(?:civil|criminal)\s+case\s+no[.:]?\s*[A-Z0-9/-]{5,20}\b',
            'license': r'\b(?:license|permit|registration)\s+no[.:]?\s*[A-Z0-9-]{5,20}\b',
            'account': r'\b\d{10,18}\b',
            'corruption_keyword': r'\b(?:corruption|bribery|kickback|embezzlement|fraud|misconduct)\b',
            'sanctions_keyword': r'\b(?:OFAC|SDN|sanctions|blacklist|watchlist|embargo)\b',
        }

        self._setup_database()
        self.logger.info("Batch PDF processor initialized")
    
    def _setup_database(self):
        """Setup the entities database"""
        os.makedirs(self.data_folder, exist_ok=True)
        
        conn = sqlite3.connect(self.main_db)
        cursor = conn.cursor()
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                file_size INTEGER,
                file_hash TEXT UNIQUE,
                processed_date TIMESTAMP,
                page_count INTEGER,
                entity_count INTEGER,
                processing_status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Entities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                entity_text TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                confidence REAL DEFAULT 0.8,
                context TEXT,
                page_reference TEXT,
                extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES processed_documents (id)
            )
        ''')
        
        # Search index table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entity_search_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_text_lower TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                document_id INTEGER,
                source_file TEXT,
                FOREIGN KEY (document_id) REFERENCES processed_documents (id)
            )
        ''')
        
        # Statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_files INTEGER,
                processed_files INTEGER,
                total_entities INTEGER,
                processing_time_seconds INTEGER
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_type ON extracted_entities(entity_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_text ON extracted_entities(entity_text)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_text ON entity_search_index(entity_text_lower)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_type ON entity_search_index(entity_type)')
        
        conn.commit()
        conn.close()
        
        self.logger.info("Database setup completed")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def _extract_text_simple(self, file_path: Path) -> str:
        """Extract text using basic methods and OCR fallback"""
        text = ""
        
        try:
            # Try PyPDF2 first (already in requirements)
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    try:
                        page_text = page.extract_text()
                        text += page_text + "\n"
                    except Exception as e:
                        self.logger.warning(f"Error extracting page from {file_path}: {e}")
                        continue
            
            # If we got very little text, try OCR
            if len(text.strip()) < 100 and self.ocr_service:
                self.logger.info(f"Text extraction yielded little content, trying OCR for {file_path.name}")
                try:
                    ocr_result = self.ocr_service.extract_text_from_pdf(file_path)
                    if ocr_result["success"] and len(ocr_result["text"]) > len(text):
                        text = ocr_result["text"]
                        self.logger.info(f"OCR extracted {len(text)} characters from {file_path.name}")
                except Exception as e:
                    self.logger.warning(f"OCR fallback failed for {file_path}: {e}")
                        
        except ImportError:
            self.logger.warning("PyPDF2 not available, trying OCR if available")
            if self.ocr_service:
                try:
                    ocr_result = self.ocr_service.extract_text_from_pdf(file_path)
                    if ocr_result["success"]:
                        text = ocr_result["text"]
                        self.logger.info(f"OCR extracted {len(text)} characters from {file_path.name}")
                except Exception as e:
                    self.logger.error(f"OCR extraction failed for {file_path}: {e}")
            
        except Exception as e:
            self.logger.error(f"Text extraction failed for {file_path}: {e}")
            
            # Try OCR as last resort
            if self.ocr_service:
                try:
                    ocr_result = self.ocr_service.extract_text_from_pdf(file_path)
                    if ocr_result["success"]:
                        text = ocr_result["text"]
                        self.logger.info(f"OCR fallback successful for {file_path.name}")
                except Exception as ocr_e:
                    self.logger.error(f"OCR fallback also failed for {file_path}: {ocr_e}")
        
        return text
    
    def _extract_entities(self, text: str, file_name: str) -> List[Dict[str, Any]]:
        """Extract entities from text using regex patterns"""
        entities = []
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity_text = match.group().strip()
                
                # Skip very short matches
                if len(entity_text) < 3:
                    continue
                
                # Get context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].replace('\n', ' ').strip()
                
                entity = {
                    'text': entity_text,
                    'type': entity_type,
                    'confidence': 0.8,
                    'context': context,
                    'start_pos': match.start(),
                    'end_pos': match.end()
                }
                entities.append(entity)
        
        # Deduplicate entities
        unique_entities = []
        seen = set()
        
        for entity in entities:
            key = (entity['text'].lower(), entity['type'])
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        self.logger.debug(f"Extracted {len(unique_entities)} unique entities from {file_name}")
        return unique_entities
    
    def _is_file_processed(self, file_path: Path) -> bool:
        """Check if file is already processed"""
        file_hash = self._calculate_file_hash(file_path)
        if not file_hash:
            return False
        
        conn = sqlite3.connect(self.main_db)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM processed_documents WHERE file_hash = ?", (file_hash,))
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def process_single_pdf(self, file_path: Path) -> bool:
        """Process a single PDF file"""
        try:
            # Check if already processed
            if self._is_file_processed(file_path):
                self.logger.info(f"Skipping already processed file: {file_path.name}")
                return True
            
            self.logger.info(f"Processing: {file_path.name}")
            
            # Extract text
            text = self._extract_text_simple(file_path)
            
            if not text or len(text.strip()) < 100:
                self.logger.warning(f"No meaningful text extracted from {file_path.name}")
                return False
            
            # Extract entities
            entities = self._extract_entities(text, file_path.name)
            
            # Save to database
            conn = sqlite3.connect(self.main_db)
            cursor = conn.cursor()
            
            # Insert document record
            file_hash = self._calculate_file_hash(file_path)
            cursor.execute('''
                INSERT INTO processed_documents 
                (file_path, file_name, file_size, file_hash, processed_date, page_count, entity_count, processing_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'completed')
            ''', (
                str(file_path), file_path.name, file_path.stat().st_size,
                file_hash, datetime.now(), text.count('\f') + 1, len(entities)
            ))
            
            document_id = cursor.lastrowid
            
            # Insert entities
            for entity in entities:
                cursor.execute('''
                    INSERT INTO extracted_entities 
                    (document_id, entity_text, entity_type, confidence, context)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    document_id, entity['text'], entity['type'], 
                    entity['confidence'], entity['context']
                ))
                
                # Insert into search index
                cursor.execute('''
                    INSERT INTO entity_search_index 
                    (entity_text_lower, entity_type, document_id, source_file)
                    VALUES (?, ?, ?, ?)
                ''', (
                    entity['text'].lower(), entity['type'], document_id, file_path.name
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Successfully processed {file_path.name}: {len(entities)} entities")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            return False
    
    def find_all_pdfs(self) -> List[Path]:
        """Find all PDF files in data folders"""
        pdf_files = []
        
        for folder in self.pdf_folders:
            if folder.exists():
                # Search recursively
                pdf_files.extend(folder.rglob("*.pdf"))
                pdf_files.extend(folder.rglob("*.PDF"))
        
        # Remove duplicates
        pdf_files = list(set(pdf_files))
        
        self.logger.info(f"Found {len(pdf_files)} PDF files")
        return pdf_files
    
    def process_all_pdfs(self) -> Dict[str, Any]:
        """Process all PDF files"""
        start_time = datetime.now()
        
        pdf_files = self.find_all_pdfs()
        
        if not pdf_files:
            self.logger.warning("No PDF files found")
            return {"processed": 0, "failed": 0, "total": 0}
        
        processed = 0
        failed = 0
        
        self.logger.info(f"Starting to process {len(pdf_files)} PDF files")
        
        for i, pdf_file in enumerate(pdf_files, 1):
            try:
                success = self.process_single_pdf(pdf_file)
                if success:
                    processed += 1
                else:
                    failed += 1
                
                # Log progress every 50 files
                if i % 50 == 0:
                    progress = (i / len(pdf_files)) * 100
                    self.logger.info(f"Progress: {progress:.1f}% ({processed} processed, {failed} failed)")
                    
            except Exception as e:
                self.logger.error(f"Failed to process {pdf_file}: {e}")
                failed += 1
        
        # Save statistics
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        conn = sqlite3.connect(self.main_db)
        cursor = conn.cursor()
        
        # Get total entities
        cursor.execute("SELECT COUNT(*) FROM extracted_entities")
        total_entities = cursor.fetchone()[0]
        
        # Save stats
        cursor.execute('''
            INSERT INTO processing_stats 
            (total_files, processed_files, total_entities, processing_time_seconds)
            VALUES (?, ?, ?, ?)
        ''', (len(pdf_files), processed, total_entities, int(processing_time)))
        
        conn.commit()
        conn.close()
        
        results = {
            "processed": processed,
            "failed": failed,
            "total": len(pdf_files),
            "success_rate": (processed / len(pdf_files)) * 100 if pdf_files else 0,
            "processing_time": processing_time,
            "total_entities": total_entities
        }
        
        self.logger.info(f"Processing complete: {results}")
        return results
    
    def search_entities(self, query: str, entity_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Search for entities"""
        conn = sqlite3.connect(self.main_db)
        cursor = conn.cursor()
        
        if entity_type:
            sql = '''
                SELECT e.entity_text, e.entity_type, e.confidence, e.context, d.file_name
                FROM extracted_entities e
                JOIN processed_documents d ON e.document_id = d.id
                WHERE e.entity_text LIKE ? AND e.entity_type = ?
                ORDER BY e.confidence DESC LIMIT ?
            '''
            cursor.execute(sql, (f"%{query}%", entity_type, limit))
        else:
            sql = '''
                SELECT e.entity_text, e.entity_type, e.confidence, e.context, d.file_name
                FROM extracted_entities e
                JOIN processed_documents d ON e.document_id = d.id
                WHERE e.entity_text LIKE ?
                ORDER BY e.confidence DESC LIMIT ?
            '''
            cursor.execute(sql, (f"%{query}%", limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "entity": row[0],
                "type": row[1],
                "confidence": row[2],
                "context": row[3],
                "file": row[4]
            }
            for row in results
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        conn = sqlite3.connect(self.main_db)
        cursor = conn.cursor()
        
        # Document stats
        cursor.execute("SELECT COUNT(*), SUM(entity_count) FROM processed_documents")
        doc_stats = cursor.fetchone()
        
        # Entity type distribution
        cursor.execute('''
            SELECT entity_type, COUNT(*) 
            FROM extracted_entities 
            GROUP BY entity_type 
            ORDER BY COUNT(*) DESC
        ''')
        entity_types = cursor.fetchall()
        
        # Latest processing stats
        cursor.execute('''
            SELECT total_files, processed_files, total_entities, processing_time_seconds
            FROM processing_stats 
            ORDER BY stat_date DESC LIMIT 1
        ''')
        latest_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            "documents_processed": doc_stats[0] or 0,
            "total_entities": doc_stats[1] or 0,
            "entity_types": dict(entity_types),
            "latest_run": {
                "total_files": latest_stats[0] if latest_stats else 0,
                "processed_files": latest_stats[1] if latest_stats else 0,
                "entities_extracted": latest_stats[2] if latest_stats else 0,
                "processing_time": latest_stats[3] if latest_stats else 0
            } if latest_stats else None,
            "database_path": str(self.main_db)
        }
    
    def export_entities_csv(self, output_path: str = None) -> str:
        """Export entities to CSV"""
        import csv
        
        if output_path is None:
            output_path = self.data_folder / f"extracted_entities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        conn = sqlite3.connect(self.main_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT e.entity_text, e.entity_type, e.confidence, e.context, d.file_name
            FROM extracted_entities e
            JOIN processed_documents d ON e.document_id = d.id
            ORDER BY e.entity_type, e.entity_text
        ''')
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Entity', 'Type', 'Confidence', 'Context', 'Source_File'])
            
            for row in cursor.fetchall():
                writer.writerow(row)
        
        conn.close()
        
        self.logger.info(f"Entities exported to: {output_path}")
        return str(output_path)

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch PDF Processor for Compliant.one")
    parser.add_argument("--process", action="store_true", help="Process all PDF files")
    parser.add_argument("--search", help="Search for entities")
    parser.add_argument("--type", help="Filter by entity type")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--export", action="store_true", help="Export entities to CSV")
    
    args = parser.parse_args()
    
    processor = BatchPDFProcessor()
    
    if args.process:
        print("🔄 Starting PDF processing...")
        results = processor.process_all_pdfs()
        print(f"\n✅ Processing Results:")
        print(f"   📄 Total files: {results['total']}")
        print(f"   ✅ Processed: {results['processed']}")
        print(f"   ❌ Failed: {results['failed']}")
        print(f"   📊 Success rate: {results['success_rate']:.1f}%")
        print(f"   ⏱️  Processing time: {results['processing_time']:.1f} seconds")
        print(f"   🔍 Total entities: {results['total_entities']}")
    
    elif args.search:
        results = processor.search_entities(args.search, args.type)
        print(f"\n🔍 Search Results for '{args.search}':")
        for result in results[:20]:  # Show top 20
            print(f"   Entity: {result['entity']}")
            print(f"   Type: {result['type']}")
            print(f"   File: {result['file']}")
            print(f"   Context: {result['context'][:80]}...")
            print("-" * 80)
    
    elif args.stats:
        stats = processor.get_statistics()
        print("\n📊 Processing Statistics:")
        print(f"   Documents processed: {stats['documents_processed']}")
        print(f"   Total entities: {stats['total_entities']}")
        print("\n   Entity types:")
        for entity_type, count in list(stats['entity_types'].items())[:10]:
            print(f"     {entity_type}: {count}")
        
        if stats['latest_run']:
            print(f"\n   Latest processing run:")
            print(f"     Files processed: {stats['latest_run']['processed_files']}/{stats['latest_run']['total_files']}")
            print(f"     Entities extracted: {stats['latest_run']['entities_extracted']}")
            print(f"     Processing time: {stats['latest_run']['processing_time']} seconds")
    
    elif args.export:
        output_file = processor.export_entities_csv()
        print(f"✅ Entities exported to: {output_file}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
