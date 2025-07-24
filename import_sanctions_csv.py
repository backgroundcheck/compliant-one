#!/usr/bin/env python3
"""
CSV Sanctions Data Import Tool for Compliant-One Platform
Standalone script to import sanctions and SDN data from CSV files

Usage:
    python3 import_sanctions_csv.py --csv_file sanctions.csv --list_name "OFAC_SDN_2024"
    python3 import_sanctions_csv.py --csv_file EU_list.csv --format eu_consolidated
    python3 import_sanctions_csv.py --directory /path/to/csv/files --auto_import
"""

import argparse
import sys
import os
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

try:
    from services.sanctions.csv_importer import SanctionsCSVImporter
except ImportError as e:
    print(f"❌ Error importing CSV importer: {e}")
    print("Make sure you're running this script from the compliant-one project root directory")
    sys.exit(1)

def print_banner():
    """Print application banner"""
    print("=" * 80)
    print("🛡️  COMPLIANT-ONE SANCTIONS DATA IMPORT TOOL")
    print("=" * 80)
    print("Import sanctions lists, SDN data, and PEP information from CSV files")
    print("Supports: OFAC SDN, EU Consolidated List, UN Consolidated List, Custom CSV")
    print("=" * 80)
    print()

def preview_csv_file(csv_file: str, rows: int = 5):
    """Preview a CSV file"""
    print(f"📄 Previewing: {csv_file}")
    print("-" * 60)
    
    try:
        importer = SanctionsCSVImporter()
        preview = importer.preview_csv(csv_file, rows)
        
        print(f"📊 File Information:")
        print(f"   • Total Rows: ~{preview.get('estimated_total_rows', 'Unknown')}")
        print(f"   • Columns: {preview.get('total_columns', 'Unknown')}")
        print(f"   • Size: {preview.get('file_size_mb', 0):.2f} MB")
        print(f"   • Detected Format: {preview.get('detected_format', 'Unknown')}")
        print()
        
        print(f"🏷️  Column Names:")
        columns = preview.get('column_names', [])
        for i, col in enumerate(columns[:15], 1):  # Show first 15 columns
            print(f"   {i:2d}. {col}")
        if len(columns) > 15:
            print(f"   ... and {len(columns) - 15} more columns")
        print()
        
        # Show sample data
        if 'sample_rows' in preview and preview['sample_rows']:
            print(f"📋 Sample Data (first {rows} rows):")
            sample_df = pd.DataFrame(preview['sample_rows'])
            print(sample_df.to_string(max_cols=5, max_colwidth=30))
            print()
        
        # Column mapping
        mapping_info = importer.map_csv_columns(csv_file)
        if mapping_info.get('column_mapping'):
            print(f"🗂️  Detected Column Mapping:")
            for db_field, csv_col in mapping_info['column_mapping'].items():
                print(f"   • {db_field} ← {csv_col}")
            print()
            
            if mapping_info.get('unmapped_columns'):
                print(f"⚠️  Unmapped Columns: {', '.join(mapping_info['unmapped_columns'])}")
                print()
        
        return preview
        
    except Exception as e:
        print(f"❌ Error previewing file: {e}")
        return None

def import_single_csv(
    csv_file: str, 
    list_name: str = None, 
    format_type: str = None,
    table_name: str = "sanctions_entities",
    batch_size: int = 1000,
    preview_only: bool = False
):
    """Import a single CSV file"""
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return False
    
    # Generate list name if not provided
    if not list_name:
        filename = Path(csv_file).stem
        timestamp = datetime.now().strftime('%Y%m%d')
        list_name = f"{filename}_{timestamp}"
    
    print(f"📥 Importing: {csv_file}")
    print(f"   • List Name: {list_name}")
    print(f"   • Format: {format_type or 'auto-detect'}")
    print(f"   • Target Table: {table_name}")
    print(f"   • Batch Size: {batch_size}")
    print()
    
    if preview_only:
        preview_csv_file(csv_file)
        return True
    
    try:
        importer = SanctionsCSVImporter()
        
        # Import the file
        print("🚀 Starting import...")
        result = importer.import_csv_to_database(
            csv_file=csv_file,
            list_name=list_name,
            table_name=table_name,
            format_type=format_type,
            batch_size=batch_size
        )
        
        # Display results
        if result.get('success', False):
            print("✅ Import Successful!")
            print(f"   • Total Rows Processed: {result['total_rows_processed']}")
            print(f"   • Successfully Imported: {result['successfully_imported']}")
            print(f"   • Errors: {result['errors']}")
            print(f"   • Detected Format: {result['detected_format']}")
            print()
            
            # Show column mapping
            if result.get('column_mapping'):
                print("🗂️  Column Mapping Used:")
                for db_field, csv_col in result['column_mapping'].items():
                    print(f"   • {db_field} ← {csv_col}")
                print()
            
            return True
        else:
            print(f"❌ Import Failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Import Error: {e}")
        return False

def import_directory(
    directory: str,
    auto_import: bool = False,
    format_type: str = None,
    table_name: str = "sanctions_entities"
):
    """Import all CSV files from a directory"""
    
    if not os.path.exists(directory):
        print(f"❌ Directory not found: {directory}")
        return False
    
    # Find all CSV files
    csv_files = list(Path(directory).glob("*.csv"))
    if not csv_files:
        print(f"❌ No CSV files found in: {directory}")
        return False
    
    print(f"📂 Found {len(csv_files)} CSV files in: {directory}")
    for i, csv_file in enumerate(csv_files, 1):
        print(f"   {i}. {csv_file.name}")
    print()
    
    if not auto_import:
        response = input("Do you want to import all files? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Import cancelled.")
            return False
    
    # Import each file
    successful_imports = 0
    for csv_file in csv_files:
        print(f"\n{'='*60}")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        list_name = f"{csv_file.stem}_{timestamp}"
        
        success = import_single_csv(
            str(csv_file),
            list_name=list_name,
            format_type=format_type,
            table_name=table_name
        )
        
        if success:
            successful_imports += 1
    
    print(f"\n🎯 Import Summary:")
    print(f"   • Total Files: {len(csv_files)}")
    print(f"   • Successful: {successful_imports}")
    print(f"   • Failed: {len(csv_files) - successful_imports}")
    
    return successful_imports > 0

def show_database_stats():
    """Show current database statistics"""
    try:
        importer = SanctionsCSVImporter()
        stats = importer.get_import_statistics()
        
        print("📊 Current Database Statistics:")
        print(f"   • Total Sanctions Entities: {stats['total_sanctions_entities']}")
        print(f"   • Total PEP Entities: {stats['total_pep_entities']}")
        print(f"   • Total Records: {stats['total_sanctions_entities'] + stats['total_pep_entities']}")
        print()
        
        if stats['recent_imports']:
            print("📅 Recent Imports:")
            for imp in stats['recent_imports'][:10]:
                print(f"   • {imp['list_name']}: {imp['count']} records ({imp['last_imported'][:19]})")
            print()
        
        if stats['entities_by_list_and_type']:
            print("📋 Breakdown by List and Type:")
            for item in stats['entities_by_list_and_type'][:20]:
                print(f"   • {item['list_name']} ({item['entity_type']}): {item['count']} records")
            print()
        
    except Exception as e:
        print(f"❌ Error getting database statistics: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Import sanctions and SDN data from CSV files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview a CSV file
  python3 import_sanctions_csv.py --csv_file sanctions.csv --preview

  # Import a single CSV file
  python3 import_sanctions_csv.py --csv_file sanctions.csv --list_name "OFAC_SDN_2024"

  # Import with specific format
  python3 import_sanctions_csv.py --csv_file eu_list.csv --format eu_consolidated

  # Import all CSV files from a directory
  python3 import_sanctions_csv.py --directory /path/to/csv/files --auto_import

  # Show database statistics
  python3 import_sanctions_csv.py --stats
        """
    )
    
    parser.add_argument('--csv_file', type=str, help='Path to CSV file to import')
    parser.add_argument('--directory', type=str, help='Directory containing CSV files')
    parser.add_argument('--list_name', type=str, help='Name for the sanctions list')
    parser.add_argument('--format', type=str, 
                       choices=['ofac_sdn', 'eu_consolidated', 'un_consolidated', 'generic'],
                       help='CSV format type (auto-detected if not specified)')
    parser.add_argument('--table', type=str, default='sanctions_entities',
                       choices=['sanctions_entities', 'pep_entities'],
                       help='Database table to import to')
    parser.add_argument('--batch_size', type=int, default=1000,
                       help='Batch size for import (default: 1000)')
    parser.add_argument('--preview', action='store_true',
                       help='Preview CSV file without importing')
    parser.add_argument('--auto_import', action='store_true',
                       help='Auto-import all files in directory without prompts')
    parser.add_argument('--stats', action='store_true',
                       help='Show database statistics')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Show statistics
    if args.stats:
        show_database_stats()
        return
    
    # Import from directory
    if args.directory:
        success = import_directory(
            args.directory,
            auto_import=args.auto_import,
            format_type=args.format,
            table_name=args.table
        )
        sys.exit(0 if success else 1)
    
    # Import single file
    if args.csv_file:
        success = import_single_csv(
            args.csv_file,
            list_name=args.list_name,
            format_type=args.format,
            table_name=args.table,
            batch_size=args.batch_size,
            preview_only=args.preview
        )
        sys.exit(0 if success else 1)
    
    # No arguments provided
    print("❌ No action specified. Use --help for usage information.")
    print("\nQuick start:")
    print("  python3 import_sanctions_csv.py --csv_file your_file.csv --preview")
    print("  python3 import_sanctions_csv.py --stats")
    sys.exit(1)

if __name__ == "__main__":
    main()
