"""
OECD Data Ingestion Service
Downloads and processes OECD Anti-Bribery Convention reports
"""

import os
import sys
import sqlite3
import requests
import logging
import csv
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import io

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

class OECDDataIngestionService:
    """
    Service for downloading and processing OECD Anti-Bribery Convention reports
    """
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
        # Database paths
        self.project_root = Path(__file__).parent.parent.parent
        self.data_folder = self.project_root / "data"
        self.pdf_folder = self.data_folder / "pdfs" / "oecd_reports"
        self.db_path = self.data_folder / "oecd_reports.db"
        
        # Create directories
        self.pdf_folder.mkdir(parents=True, exist_ok=True)
        self.data_folder.mkdir(parents=True, exist_ok=True)
        
        # Setup database
        self._setup_database()
        
        self.logger.info("OECD Data Ingestion Service initialized")
    
    def _setup_database(self):
        """Setup the OECD reports database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # OECD Reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS oecd_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country TEXT NOT NULL,
                report_type TEXT NOT NULL,
                phase INTEGER NOT NULL,
                year INTEGER NOT NULL,
                month TEXT NOT NULL,
                pdf_url TEXT NOT NULL,
                citation TEXT,
                local_pdf_path TEXT,
                file_size INTEGER,
                download_date TIMESTAMP,
                processing_status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(country, report_type, phase, year, month)
            )
        ''')
        
        # Extracted entities from OECD reports
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS oecd_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER,
                entity_text TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                confidence REAL DEFAULT 0.8,
                context TEXT,
                page_reference TEXT,
                extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES oecd_reports (id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_oecd_country ON oecd_reports(country)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_oecd_phase ON oecd_reports(phase)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_oecd_year ON oecd_reports(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_oecd_entities_type ON oecd_entities(entity_type)')
        
        conn.commit()
        conn.close()
        
        self.logger.info("OECD database setup completed")
    
    def parse_csv_data(self, csv_data: str) -> List[Dict[str, Any]]:
        """Parse CSV data into structured records"""
        records = []
        
        try:
            # Use StringIO to read CSV data
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            
            for row in csv_reader:
                record = {
                    'country': row['Country'].strip(),
                    'report_type': row['Report_Type'].strip(),
                    'phase': int(row['Phase']),
                    'year': int(row['Year']),
                    'month': row['Month'].strip(),
                    'pdf_url': row['PDF_URL'].strip(),
                    'citation': row['Citation'].strip()
                }
                records.append(record)
                
        except Exception as e:
            self.logger.error(f"Error parsing CSV data: {e}")
            return []
        
        self.logger.info(f"Parsed {len(records)} OECD report records")
        return records
    
    def insert_records(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Insert records into database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            inserted = 0
            skipped = 0
            
            for record in records:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO oecd_reports 
                        (country, report_type, phase, year, month, pdf_url, citation)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        record['country'],
                        record['report_type'],
                        record['phase'],
                        record['year'],
                        record['month'],
                        record['pdf_url'],
                        record['citation']
                    ))
                    
                    if cursor.rowcount > 0:
                        inserted += 1
                    else:
                        skipped += 1
                        
                except Exception as e:
                    self.logger.warning(f"Error inserting record for {record['country']}: {e}")
                    skipped += 1
            
            conn.commit()
            conn.close()
            
            result = {
                "success": True,
                "total_records": len(records),
                "inserted": inserted,
                "skipped": skipped
            }
            
            self.logger.info(f"Database insertion completed: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Database insertion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_records": len(records),
                "inserted": 0,
                "skipped": len(records)
            }
    
    def download_pdf(self, report_id: int, pdf_url: str, country: str, year: int, month: str) -> bool:
        """Download a single PDF file"""
        try:
            # Generate filename
            safe_country = "".join(c for c in country if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_country}_{year}_{month}.pdf"
            local_path = self.pdf_folder / filename
            
            # Skip if already downloaded
            if local_path.exists():
                self.logger.debug(f"PDF already exists: {filename}")
                return True
            
            # Download PDF
            self.logger.info(f"Downloading PDF: {filename}")
            response = requests.get(pdf_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Save PDF
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Update database with local path
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE oecd_reports 
                SET local_pdf_path = ?, file_size = ?, download_date = ?, processing_status = 'downloaded'
                WHERE id = ?
            ''', (str(local_path), local_path.stat().st_size, datetime.now(), report_id))
            conn.commit()
            conn.close()
            
            self.logger.info(f"Successfully downloaded: {filename} ({local_path.stat().st_size} bytes)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download PDF {pdf_url}: {e}")
            
            # Update status to failed
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE oecd_reports 
                    SET processing_status = 'download_failed'
                    WHERE id = ?
                ''', (report_id,))
                conn.commit()
                conn.close()
            except:
                pass
            
            return False
    
    def download_all_pdfs(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Download all PDFs from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get records that need downloading
            query = '''
                SELECT id, country, year, month, pdf_url 
                FROM oecd_reports 
                WHERE processing_status = 'pending' OR processing_status = 'download_failed'
                ORDER BY year DESC, month
            '''
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            records = cursor.fetchall()
            conn.close()
            
            if not records:
                return {
                    "success": True,
                    "message": "No PDFs to download",
                    "downloaded": 0,
                    "failed": 0
                }
            
            downloaded = 0
            failed = 0
            
            self.logger.info(f"Starting download of {len(records)} PDFs")
            
            for record in records:
                report_id, country, year, month, pdf_url = record
                
                success = self.download_pdf(report_id, pdf_url, country, year, month)
                if success:
                    downloaded += 1
                else:
                    failed += 1
                
                # Log progress every 5 downloads
                if (downloaded + failed) % 5 == 0:
                    self.logger.info(f"Progress: {downloaded} downloaded, {failed} failed")
            
            result = {
                "success": True,
                "total_records": len(records),
                "downloaded": downloaded,
                "failed": failed,
                "success_rate": (downloaded / len(records)) * 100 if records else 0
            }
            
            self.logger.info(f"Download completed: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Download process failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "downloaded": 0,
                "failed": 0
            }
    
    def process_with_ocr(self, report_id: int) -> bool:
        """Process a downloaded PDF with OCR and entity extraction"""
        try:
            # Import OCR service
            from services.ocr.ocr_service import OCRService
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get report details
            cursor.execute('''
                SELECT local_pdf_path, country, report_type 
                FROM oecd_reports 
                WHERE id = ? AND processing_status = 'downloaded'
            ''', (report_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            local_pdf_path, country, report_type = result
            
            if not local_pdf_path or not Path(local_pdf_path).exists():
                return False
            
            # Initialize OCR service
            ocr_service = OCRService()
            
            # Extract text using OCR
            self.logger.info(f"Processing PDF with OCR: {Path(local_pdf_path).name}")
            ocr_result = ocr_service.extract_text_from_pdf(local_pdf_path)
            
            if not ocr_result["success"]:
                self.logger.warning(f"OCR failed for {local_pdf_path}: {ocr_result.get('error')}")
                return False
            
            # Extract entities using regex patterns
            entities = self._extract_compliance_entities(ocr_result["text"], country, report_type)
            
            # Save entities to database
            for entity in entities:
                cursor.execute('''
                    INSERT INTO oecd_entities 
                    (report_id, entity_text, entity_type, confidence, context)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    report_id,
                    entity['text'],
                    entity['type'],
                    entity['confidence'],
                    entity['context']
                ))
            
            # Update report status
            cursor.execute('''
                UPDATE oecd_reports 
                SET processing_status = 'processed'
                WHERE id = ?
            ''', (report_id,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Successfully processed PDF: {len(entities)} entities extracted")
            return True
            
        except Exception as e:
            self.logger.error(f"OCR processing failed for report {report_id}: {e}")
            return False
    
    def _extract_compliance_entities(self, text: str, country: str, report_type: str) -> List[Dict[str, Any]]:
        """Extract compliance-related entities from text"""
        import re
        
        entities = []
        
        # Define entity extraction patterns
        patterns = {
            'organization': r'\b(?:Ministry|Department|Agency|Commission|Authority|Bureau|Bank|Company|Corporation|Ltd|LLC|Inc)\s+[A-Z][a-zA-Z\s&.-]{2,50}',
            'person_name': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',
            'amount': r'\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|million|billion)\b',
            'date': r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'case_number': r'\b(?:case|file|reference|investigation)\s*[#:]?\s*[A-Z0-9-]{5,20}\b',
            'bribery_keyword': r'\b(?:bribery|corruption|kickback|embezzlement|fraud|misconduct|FCPA|anti-corruption|money laundering)\b',
            'recommendation': r'\b(?:recommend|recommendation|should|must|shall)\s+[a-zA-Z\s,]{10,100}',
            'jurisdiction': r'\b(?:court|tribunal|prosecutor|prosecution|judicial|magistrate|jurisdiction)\b'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity_text = match.group().strip()
                
                # Skip very short matches
                if len(entity_text) < 3:
                    continue
                
                # Get context
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].replace('\n', ' ').strip()
                
                # Calculate confidence based on context and entity type
                confidence = 0.8
                if entity_type == 'bribery_keyword':
                    confidence = 0.95
                elif entity_type in ['amount', 'date']:
                    confidence = 0.9
                elif country.lower() in entity_text.lower():
                    confidence = 0.9
                
                entity = {
                    'text': entity_text,
                    'type': entity_type,
                    'confidence': confidence,
                    'context': context
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
        
        return unique_entities
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get OECD data statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Report statistics
            cursor.execute("SELECT COUNT(*) FROM oecd_reports")
            total_reports = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM oecd_reports WHERE processing_status = 'downloaded'")
            downloaded_reports = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM oecd_reports WHERE processing_status = 'processed'")
            processed_reports = cursor.fetchone()[0]
            
            # Entity statistics
            cursor.execute("SELECT COUNT(*) FROM oecd_entities")
            total_entities = cursor.fetchone()[0]
            
            # Country breakdown
            cursor.execute('''
                SELECT country, COUNT(*) 
                FROM oecd_reports 
                GROUP BY country 
                ORDER BY COUNT(*) DESC 
                LIMIT 10
            ''')
            country_breakdown = dict(cursor.fetchall())
            
            # Phase breakdown
            cursor.execute('''
                SELECT phase, COUNT(*) 
                FROM oecd_reports 
                GROUP BY phase 
                ORDER BY phase
            ''')
            phase_breakdown = dict(cursor.fetchall())
            
            # Entity type breakdown
            cursor.execute('''
                SELECT entity_type, COUNT(*) 
                FROM oecd_entities 
                GROUP BY entity_type 
                ORDER BY COUNT(*) DESC
            ''')
            entity_breakdown = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "reports": {
                    "total": total_reports,
                    "downloaded": downloaded_reports,
                    "processed": processed_reports,
                    "download_rate": (downloaded_reports / total_reports) * 100 if total_reports > 0 else 0,
                    "processing_rate": (processed_reports / total_reports) * 100 if total_reports > 0 else 0
                },
                "entities": {
                    "total": total_entities,
                    "types": entity_breakdown
                },
                "breakdowns": {
                    "countries": country_breakdown,
                    "phases": phase_breakdown
                },
                "database_path": str(self.db_path),
                "pdf_folder": str(self.pdf_folder)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {"error": str(e)}
    
    def search_reports(self, country: str = None, phase: int = None, year: int = None) -> List[Dict[str, Any]]:
        """Search OECD reports"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM oecd_reports WHERE 1=1"
            params = []
            
            if country:
                query += " AND country LIKE ?"
                params.append(f"%{country}%")
            
            if phase:
                query += " AND phase = ?"
                params.append(phase)
            
            if year:
                query += " AND year = ?"
                params.append(year)
            
            query += " ORDER BY year DESC, month"
            
            cursor.execute(query, params)
            
            columns = [description[0] for description in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            conn.close()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OECD Data Ingestion Service")
    parser.add_argument("--csv-data", help="CSV data to import")
    parser.add_argument("--download", action="store_true", help="Download all PDFs")
    parser.add_argument("--download-limit", type=int, help="Limit number of downloads")
    parser.add_argument("--process-ocr", action="store_true", help="Process PDFs with OCR")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--search-country", help="Search by country")
    parser.add_argument("--search-phase", type=int, help="Search by phase")
    parser.add_argument("--search-year", type=int, help="Search by year")
    
    args = parser.parse_args()
    
    service = OECDDataIngestionService()
    
    if args.csv_data:
        print("📥 Parsing and importing CSV data...")
        records = service.parse_csv_data(args.csv_data)
        if records:
            result = service.insert_records(records)
            print(f"✅ Import completed: {result}")
        else:
            print("❌ No records to import")
    
    elif args.download:
        print("📥 Starting PDF downloads...")
        result = service.download_all_pdfs(limit=args.download_limit)
        print(f"📊 Download Results:")
        print(f"   📄 Total records: {result.get('total_records', 0)}")
        print(f"   ✅ Downloaded: {result.get('downloaded', 0)}")
        print(f"   ❌ Failed: {result.get('failed', 0)}")
        if 'success_rate' in result:
            print(f"   📈 Success rate: {result['success_rate']:.1f}%")
    
    elif args.process_ocr:
        print("🔍 Processing PDFs with OCR...")
        # Get downloaded reports
        import sqlite3
        conn = sqlite3.connect(service.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM oecd_reports WHERE processing_status = 'downloaded'")
        report_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        processed = 0
        for report_id in report_ids:
            if service.process_with_ocr(report_id):
                processed += 1
            if processed % 5 == 0:
                print(f"   Processed: {processed}/{len(report_ids)}")
        
        print(f"✅ OCR processing completed: {processed}/{len(report_ids)} successful")
    
    elif args.stats:
        stats = service.get_statistics()
        print("📊 OECD Data Statistics:")
        print(f"   📄 Total reports: {stats['reports']['total']}")
        print(f"   📥 Downloaded: {stats['reports']['downloaded']} ({stats['reports']['download_rate']:.1f}%)")
        print(f"   🔍 Processed: {stats['reports']['processed']} ({stats['reports']['processing_rate']:.1f}%)")
        print(f"   🏷️  Total entities: {stats['entities']['total']}")
        
        print("\n   🌍 Top countries:")
        for country, count in list(stats['breakdowns']['countries'].items())[:5]:
            print(f"     {country}: {count}")
        
        print(f"\n   📂 Database: {stats['database_path']}")
        print(f"   📁 PDF folder: {stats['pdf_folder']}")
    
    elif args.search_country or args.search_phase or args.search_year:
        results = service.search_reports(
            country=args.search_country,
            phase=args.search_phase,
            year=args.search_year
        )
        
        print(f"🔍 Search Results: {len(results)} reports found")
        for result in results[:10]:  # Show top 10
            print(f"   📄 {result['country']} - {result['report_type']} (Phase {result['phase']}, {result['year']})")
            print(f"      Status: {result['processing_status']}")
            if result['local_pdf_path']:
                print(f"      Local file: {Path(result['local_pdf_path']).name}")
            print()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
