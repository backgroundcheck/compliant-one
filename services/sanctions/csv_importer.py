"""
CSV Sanctions Data Import Utility for Compliant-One Platform
Supports importing sanctions and SDN (Specially Designated Nationals) data from CSV files
"""

import csv
import sqlite3
import pandas as pd
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
import re

class SanctionsCSVImporter:
    """Import sanctions and SDN data from CSV files"""
    
    def __init__(self, db_path: str = "sanctions.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Standard field mappings for common CSV formats
        self.field_mappings = {
            # OFAC SDN format
            'ofac_sdn': {
                'name': ['name', 'sdn_name', 'entity_name', 'individual_name'],
                'aliases': ['aliases', 'alternative_names', 'aka', 'also_known_as'],
                'entity_type': ['entity_type', 'type', 'sdn_type'],
                'program': ['program', 'sanction_program', 'list_type'],
                'address': ['address', 'addresses', 'location'],
                'country': ['country', 'country_code', 'nationality'],
                'list_date': ['list_date', 'date_added', 'publication_date'],
                'id_number': ['id_number', 'identification_number', 'passport_number']
            },
            
            # EU Consolidated List format
            'eu_consolidated': {
                'name': ['name_1', 'name', 'entity_name'],
                'aliases': ['name_2', 'name_3', 'other_names'],
                'entity_type': ['entity_type', 'subject_type'],
                'program': ['regulation', 'legal_basis'],
                'address': ['address', 'birth_place'],
                'country': ['country', 'nationality'],
                'list_date': ['regulation_date', 'listing_date']
            },
            
            # UN Consolidated List format
            'un_consolidated': {
                'name': ['name', 'first_name', 'second_name', 'third_name'],
                'aliases': ['alias', 'alternative_spelling'],
                'entity_type': ['entity_type', 'dataid'],
                'program': ['committee', 'list_type'],
                'address': ['address_1', 'address_2', 'address_3'],
                'country': ['country', 'nationality_1', 'nationality_2'],
                'list_date': ['listed_on', 'narrative_date_of_listing']
            },
            
            # Generic format
            'generic': {
                'name': ['name', 'full_name', 'entity_name', 'individual_name'],
                'aliases': ['aliases', 'aka', 'alternative_names', 'other_names'],
                'entity_type': ['type', 'entity_type', 'category'],
                'program': ['program', 'list', 'source'],
                'address': ['address', 'location', 'residence'],
                'country': ['country', 'nationality', 'citizenship'],
                'list_date': ['date', 'list_date', 'added_date']
            }
        }
    
    def detect_csv_format(self, csv_file: str) -> str:
        """Detect the format of the CSV file based on column headers"""
        try:
            df = pd.read_csv(csv_file, nrows=1)
            columns = [col.lower().replace(' ', '_') for col in df.columns]
            
            # Check for OFAC SDN format
            if any(col in columns for col in ['sdn_name', 'sdn_type', 'program']):
                return 'ofac_sdn'
            
            # Check for EU format
            elif any(col in columns for col in ['name_1', 'regulation', 'subject_type']):
                return 'eu_consolidated'
            
            # Check for UN format
            elif any(col in columns for col in ['dataid', 'committee', 'listed_on']):
                return 'un_consolidated'
            
            # Default to generic
            else:
                return 'generic'
                
        except Exception as e:
            self.logger.warning(f"Could not detect format for {csv_file}: {e}")
            return 'generic'
    
    def preview_csv(self, csv_file: str, rows: int = 5) -> Dict:
        """Preview CSV file structure and data"""
        try:
            df = pd.read_csv(csv_file, nrows=rows)
            detected_format = self.detect_csv_format(csv_file)
            
            preview_info = {
                'file_path': csv_file,
                'total_columns': len(df.columns),
                'column_names': list(df.columns),
                'detected_format': detected_format,
                'sample_rows': df.head(rows).to_dict('records'),
                'estimated_total_rows': sum(1 for line in open(csv_file)) - 1,  # Exclude header
                'file_size_mb': Path(csv_file).stat().st_size / (1024 * 1024)
            }
            
            return preview_info
            
        except Exception as e:
            self.logger.error(f"Error previewing CSV file {csv_file}: {e}")
            return {'error': str(e)}
    
    def map_csv_columns(self, csv_file: str, format_type: str = None) -> Dict:
        """Map CSV columns to database fields"""
        if format_type is None:
            format_type = self.detect_csv_format(csv_file)
        
        try:
            df = pd.read_csv(csv_file, nrows=1)
            csv_columns = [col.lower().replace(' ', '_') for col in df.columns]
            
            mapping = {}
            field_mapping = self.field_mappings.get(format_type, self.field_mappings['generic'])
            
            for db_field, possible_columns in field_mapping.items():
                for col in possible_columns:
                    if col in csv_columns:
                        mapping[db_field] = df.columns[csv_columns.index(col)]
                        break
                else:
                    # If no exact match, look for partial matches
                    for csv_col in csv_columns:
                        if any(keyword in csv_col for keyword in possible_columns):
                            mapping[db_field] = df.columns[csv_columns.index(csv_col)]
                            break
            
            return {
                'detected_format': format_type,
                'column_mapping': mapping,
                'unmapped_columns': [col for col in df.columns if col not in mapping.values()],
                'csv_columns': list(df.columns)
            }
            
        except Exception as e:
            self.logger.error(f"Error mapping columns for {csv_file}: {e}")
            return {'error': str(e)}
    
    def clean_and_validate_data(self, row: Dict, mapping: Dict) -> Dict:
        """Clean and validate a single row of data"""
        cleaned_row = {}
        
        # Map fields
        for db_field, csv_column in mapping.items():
            if csv_column in row:
                value = row[csv_column]
                
                # Clean the value
                if pd.isna(value) or value == '':
                    cleaned_row[db_field] = None
                else:
                    # Convert to string and clean
                    value = str(value).strip()
                    
                    # Special handling for specific fields
                    if db_field == 'entity_type':
                        cleaned_row[db_field] = self._normalize_entity_type(value)
                    elif db_field == 'country':
                        cleaned_row[db_field] = self._normalize_country(value)
                    elif db_field == 'list_date':
                        cleaned_row[db_field] = self._parse_date(value)
                    elif db_field == 'aliases':
                        cleaned_row[db_field] = self._normalize_aliases(value)
                    else:
                        cleaned_row[db_field] = value
            else:
                cleaned_row[db_field] = None
        
        # Set defaults
        cleaned_row['status'] = 'active'
        cleaned_row['created_at'] = datetime.now().isoformat()
        
        return cleaned_row
    
    def _normalize_entity_type(self, value: str) -> str:
        """Normalize entity type values"""
        value = value.lower()
        if 'individual' in value or 'person' in value:
            return 'individual'
        elif 'entity' in value or 'organization' in value or 'company' in value:
            return 'entity'
        elif 'vessel' in value or 'ship' in value:
            return 'vessel'
        elif 'aircraft' in value or 'plane' in value:
            return 'aircraft'
        else:
            return 'other'
    
    def _normalize_country(self, value: str) -> str:
        """Normalize country codes and names"""
        # Simple country normalization - can be expanded
        country_mappings = {
            'usa': 'United States',
            'uk': 'United Kingdom',
            'uae': 'United Arab Emirates',
            'dprk': 'North Korea'
        }
        
        value_lower = value.lower()
        return country_mappings.get(value_lower, value)
    
    def _parse_date(self, value: str) -> Optional[str]:
        """Parse various date formats"""
        if not value or pd.isna(value):
            return None
        
        # Common date formats
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%m-%d-%Y',
            '%B %d, %Y',
            '%d %B %Y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(str(value), fmt)
                return parsed_date.date().isoformat()
            except ValueError:
                continue
        
        # If no format works, return as-is
        return str(value)
    
    def _normalize_aliases(self, value: str) -> str:
        """Normalize aliases field"""
        if not value or pd.isna(value):
            return ""
        
        # Split on common delimiters and clean
        aliases = re.split(r'[;,\|]', str(value))
        cleaned_aliases = [alias.strip() for alias in aliases if alias.strip()]
        
        return '; '.join(cleaned_aliases)
    
    def import_csv_to_database(
        self, 
        csv_file: str, 
        list_name: str,
        table_name: str = 'sanctions_entities',
        format_type: str = None,
        custom_mapping: Dict = None,
        batch_size: int = 1000
    ) -> Dict:
        """Import CSV data to sanctions database"""
        
        try:
            # Get column mapping
            if custom_mapping:
                mapping = custom_mapping
                detected_format = format_type or 'custom'
            else:
                mapping_info = self.map_csv_columns(csv_file, format_type)
                mapping = mapping_info['column_mapping']
                detected_format = mapping_info['detected_format']
            
            # Read CSV file
            df = pd.read_csv(csv_file)
            total_rows = len(df)
            
            self.logger.info(f"Starting import of {total_rows} rows from {csv_file}")
            self.logger.info(f"Detected format: {detected_format}")
            self.logger.info(f"Column mapping: {mapping}")
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Process data in batches
            imported_count = 0
            error_count = 0
            
            for batch_start in range(0, total_rows, batch_size):
                batch_end = min(batch_start + batch_size, total_rows)
                batch_df = df.iloc[batch_start:batch_end]
                
                batch_data = []
                for _, row in batch_df.iterrows():
                    try:
                        cleaned_row = self.clean_and_validate_data(row.to_dict(), mapping)
                        cleaned_row['list_name'] = list_name
                        batch_data.append(cleaned_row)
                    except Exception as e:
                        self.logger.warning(f"Error processing row {batch_start + len(batch_data)}: {e}")
                        error_count += 1
                        continue
                
                # Insert batch
                if batch_data:
                    self._insert_batch(cursor, table_name, batch_data)
                    imported_count += len(batch_data)
                
                # Progress update
                progress = (batch_end / total_rows) * 100
                self.logger.info(f"Progress: {progress:.1f}% ({batch_end}/{total_rows} rows processed)")
            
            conn.commit()
            conn.close()
            
            result = {
                'success': True,
                'file_imported': csv_file,
                'list_name': list_name,
                'table_name': table_name,
                'total_rows_processed': total_rows,
                'successfully_imported': imported_count,
                'errors': error_count,
                'detected_format': detected_format,
                'column_mapping': mapping
            }
            
            self.logger.info(f"Import completed: {imported_count} rows imported, {error_count} errors")
            return result
            
        except Exception as e:
            self.logger.error(f"Error importing CSV file {csv_file}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file': csv_file
            }
    
    def _insert_batch(self, cursor, table_name: str, batch_data: List[Dict]):
        """Insert a batch of data into the database"""
        if not batch_data:
            return
        
        # Get all possible columns from the batch
        all_columns = set()
        for row in batch_data:
            all_columns.update(row.keys())
        
        # Build insert query
        columns = list(all_columns)
        placeholders = ', '.join(['?' for _ in columns])
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        # Prepare data for insertion
        rows_data = []
        for row in batch_data:
            row_values = [row.get(col) for col in columns]
            rows_data.append(row_values)
        
        cursor.executemany(query, rows_data)
    
    def import_multiple_csvs(
        self, 
        csv_files: List[str], 
        list_names: List[str] = None,
        format_types: List[str] = None
    ) -> List[Dict]:
        """Import multiple CSV files"""
        
        if list_names and len(list_names) != len(csv_files):
            raise ValueError("list_names must have same length as csv_files")
        
        if format_types and len(format_types) != len(csv_files):
            raise ValueError("format_types must have same length as csv_files")
        
        results = []
        for i, csv_file in enumerate(csv_files):
            list_name = list_names[i] if list_names else f"imported_list_{i+1}"
            format_type = format_types[i] if format_types else None
            
            result = self.import_csv_to_database(csv_file, list_name, format_type=format_type)
            results.append(result)
        
        return results
    
    def get_import_statistics(self) -> Dict:
        """Get statistics about imported data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get counts by list
            cursor.execute("""
                SELECT list_name, entity_type, COUNT(*) as count 
                FROM sanctions_entities 
                GROUP BY list_name, entity_type
                ORDER BY list_name, entity_type
            """)
            
            list_stats = cursor.fetchall()
            
            # Get total counts
            cursor.execute("SELECT COUNT(*) FROM sanctions_entities")
            total_sanctions = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM pep_entities")
            total_peps = cursor.fetchone()[0]
            
            # Get recent imports
            cursor.execute("""
                SELECT list_name, COUNT(*) as count, MAX(created_at) as last_imported
                FROM sanctions_entities 
                GROUP BY list_name
                ORDER BY last_imported DESC
            """)
            
            recent_imports = cursor.fetchall()
            
            return {
                'total_sanctions_entities': total_sanctions,
                'total_pep_entities': total_peps,
                'entities_by_list_and_type': [
                    {'list_name': row[0], 'entity_type': row[1], 'count': row[2]} 
                    for row in list_stats
                ],
                'recent_imports': [
                    {'list_name': row[0], 'count': row[1], 'last_imported': row[2]}
                    for row in recent_imports
                ]
            }
            
        finally:
            conn.close()


def main():
    """Example usage of the CSV importer"""
    importer = SanctionsCSVImporter()
    
    # Example: Preview a CSV file
    csv_file = "path/to/your/sanctions.csv"
    preview = importer.preview_csv(csv_file)
    print(f"CSV Preview: {json.dumps(preview, indent=2)}")
    
    # Example: Import a CSV file
    result = importer.import_csv_to_database(
        csv_file=csv_file,
        list_name="OFAC_SDN_2024",
        format_type="ofac_sdn"
    )
    print(f"Import Result: {json.dumps(result, indent=2)}")
    
    # Example: Get statistics
    stats = importer.get_import_statistics()
    print(f"Import Statistics: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    main()
