#!/usr/bin/env python3
"""
Sanctions Data Extraction Script
Extracts and processes sanctions data from various sources
"""

import sys
from pathlib import Path
from datetime import datetime
import logging
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Optional: PostgreSQL integration (requires psycopg2 installation)
try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("PostgreSQL support not available. Install psycopg2 for database functionality.")

# Use project logger
from utils.logger import get_logger

logger = get_logger(__name__)

def extract_sanctions_data():
    """Extract sanctions data from OCR and other sources"""
    
    logger.info("Starting sanctions data extraction...")
    
    # Sample OCR data (replace with full OCR text or file parsing)
    ocr_data = [
        {"page": 5, "list_name": "List of Individuals Detained by the Department of Defense", "authority": "Department of Defense", "country": "United States"},
        {"page": 7, "list_name": "Most Wanted Terrorists", "authority": "Department of Justice, Federal Bureau of Investigation", "country": "United States"},
        {"page": 7, "list_name": "The FBI's Ten Most Wanted Fugitives", "authority": "Department of Justice, Federal Bureau of Investigation", "country": "United States"},
        {"page": 9, "list_name": "Most Wanted by Delocona County Sheriff's Office", "authority": "Delocona County Sheriff's Office", "country": "United States"},
        {"page": 11, "list_name": "Kentucky State Police Most Wanted List", "authority": "Kentucky State Police", "country": "United States"},
        {"page": 18, "list_name": "Wanted Persons", "authority": "Ministry of Interior, Sofia Directorate of Interior", "country": "Bulgaria"},
        {"page": 18, "list_name": "Wanted Persons", "authority": "General Commissioner of National Police", "country": "Cambodia"},
        {"page": 18, "list_name": "Casual Trade Orders", "authority": "Canadian regulatory authorities", "country": "Canada"},
        {"page": 31, "list_name": "Bush List 15", "authority": "Swiss Financial Market Supervisory Authority (FINMA)", "country": "Switzerland"},
        {"page": 31, "list_name": "Bush List 18", "authority": "Swiss Financial Market Supervisory Authority (FINMA)", "country": "Switzerland"},
    ]
    
    # Process data
    processed_data = []
    seen = set()
    
    for entry in ocr_data:
        list_key = (entry["list_name"], entry["authority"], entry["country"])
        if list_key not in seen:
            seen.add(list_key)
            processed_entry = {
                "list_name": entry["list_name"],
                "authority": entry["authority"],
                "country": entry["country"],
                "page": entry.get("page"),
                "created_at": datetime.now().isoformat()
            }
            processed_data.append(processed_entry)
    
    logger.info(f"Processed {len(processed_data)} unique sanctions entries")
    
    # Save to JSON if no database
    if not POSTGRES_AVAILABLE:
        output_file = Path("data/sanctions_extracted.json")
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(processed_data, f, indent=2)
        
        logger.info(f"Sanctions data saved to {output_file}")
    
    return processed_data

def store_in_database(data):
    """Store extracted data in PostgreSQL database"""
    
    if not POSTGRES_AVAILABLE:
        logger.warning("PostgreSQL not available. Skipping database storage.")
        return
    
    try:
        # Database connection (configure as needed)
        conn = psycopg2.connect(
            dbname="criminal_activities",
            user="your_user", 
            password="your_password",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sanctions_lists (
                id SERIAL PRIMARY KEY,
                list_name VARCHAR(500) NOT NULL,
                authority VARCHAR(500) NOT NULL,
                country VARCHAR(100) NOT NULL,
                page INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(list_name, authority, country)
            );
        """)
        
        # Insert data
        for entry in data:
            cursor.execute(
                """
                INSERT INTO sanctions_lists (list_name, authority, country, page, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (list_name, authority, country) DO NOTHING
                """,
                (entry["list_name"], entry["authority"], entry["country"], 
                 entry.get("page"), entry["created_at"])
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Data successfully stored in PostgreSQL database")
        
    except Exception as e:
        logger.error(f"Database error: {e}")

def main():
    """Main function"""
    
    print("🔍 Sanctions Data Extraction Tool")
    print("=" * 50)
    
    # Extract data
    data = extract_sanctions_data()
    
    # Store in database if available
    store_in_database(data)
    
    # Show summary
    print(f"\n📊 Extraction Summary:")
    print(f"   📋 Total entries: {len(data)}")
    print(f"   🌍 Countries covered: {len(set(entry['country'] for entry in data))}")
    print(f"   🏛️ Authorities: {len(set(entry['authority'] for entry in data))}")
    
    print(f"\n🎯 Data Sources Identified:")
    for entry in data:
        print(f"   • {entry['list_name']} ({entry['country']})")
    
    print(f"\n✅ Extraction completed successfully!")

if __name__ == "__main__":
    main()
