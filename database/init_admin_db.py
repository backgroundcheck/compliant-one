"""
Database initialization script for Compliant.one Admin Dashboard
"""

import sqlite3
import os
from pathlib import Path

def initialize_admin_database():
    """Initialize the admin database with required tables"""
    
    # Ensure database directory exists
    db_dir = Path("database")
    db_dir.mkdir(exist_ok=True)
    
    db_path = db_dir / "data_sources.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create data sources table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            source_url TEXT,
            api_key TEXT,
            api_endpoint TEXT,
            status TEXT DEFAULT 'inactive',
            last_updated TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            config TEXT,
            description TEXT
        )
    ''')
    
    # Create uploaded files table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploaded_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_size INTEGER,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_date TIMESTAMP,
            status TEXT DEFAULT 'uploaded',
            records_count INTEGER DEFAULT 0,
            error_message TEXT
        )
    ''')
    
    # Create processed data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER,
            file_id INTEGER,
            data_type TEXT NOT NULL,
            entity_name TEXT,
            entity_id TEXT,
            risk_score REAL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_id) REFERENCES data_sources(id),
            FOREIGN KEY (file_id) REFERENCES uploaded_files(id)
        )
    ''')
    
    # Insert sample data sources
    sample_sources = [
        ('OFAC SDN List', 'API', 'Sanctions', 'https://www.treasury.gov/ofac/downloads/sdn.xml', '', 'https://api.treasury.gov/ofac/sdn', 'Sample OFAC sanctions list'),
        ('UN Consolidated List', 'API', 'Sanctions', 'https://www.un.org/securitycouncil/content/un-sc-consolidated-list', '', 'https://scsanctions.un.org/resources/xml/en/consolidated.xml', 'UN Security Council sanctions list'),
        ('World-Check Database', 'API', 'PEP', '', '[API_KEY_REQUIRED]', 'https://api.worldcheck.com/v1', 'Refinitiv World-Check API for PEP and sanctions screening'),
        ('Companies House UK', 'API', 'Beneficial Ownership', 'https://find-and-update.company-information.service.gov.uk/', '[API_KEY_REQUIRED]', 'https://api.company-information.service.gov.uk', 'UK corporate registry for beneficial ownership'),
        ('Google News API', 'API', 'Adverse Media', '', '[API_KEY_REQUIRED]', 'https://newsapi.org/v2/everything', 'News aggregation for adverse media monitoring')
    ]
    
    for source in sample_sources:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO data_sources 
                (name, type, category, source_url, api_key, api_endpoint, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', source)
        except sqlite3.IntegrityError:
            # Source already exists
            pass
    
    conn.commit()
    conn.close()
    
    print("✅ Admin database initialized successfully!")
    print(f"📊 Database location: {db_path}")
    
    # Create required directories
    required_dirs = [
        "data/uploads",
        "data/processed", 
        "logs"
    ]
    
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {dir_path}")

if __name__ == "__main__":
    initialize_admin_database()
