# 📥 CSV Sanctions Data Import Guide

## Overview

The compliant-one platform provides comprehensive tools for importing sanctions data, Specially Designated Nationals (SDN) lists, and Politically Exposed Persons (PEP) data from CSV files. This guide covers all available import methods and supported formats.

## 🚀 Quick Start

### Method 1: Web Dashboard (Recommended)

1. **Access Platform**: <http://localhost:8501>
2. **Login**: admin / SecurePass123!
3. **Navigate**: Admin Panel → Web Crawler → **📊 Compliance Analysis** tab → **📥 Import Sanctions Data** subtab
4. **Upload**: Select your CSV files and follow the guided import process

### Method 2: Command Line Tool

```bash
# Preview a CSV file first
python3 import_sanctions_csv.py --csv_file your_sanctions.csv --preview

# Import the CSV file
python3 import_sanctions_csv.py --csv_file your_sanctions.csv --list_name "My_Sanctions_List"

# Import multiple files from a directory
python3 import_sanctions_csv.py --directory /path/to/csv/files --auto_import
```

## 📋 Supported CSV Formats

### 1. OFAC SDN (Office of Foreign Assets Control)

**Source**: U.S. Treasury Department  
**Download**: <https://sanctionslist.ofac.treas.gov/Home/SdnList>

**Expected Columns**:

- `name` or `sdn_name` - Entity name
- `sdn_type` or `entity_type` - Individual/Entity/Vessel
- `program` - Sanctions program
- `title` - Position/title
- `address` - Address information
- `country` - Country/nationality
- `aliases` or `alternative_names` - Alternative names

**Example**:

```csv
name,sdn_type,program,title,address,country,aliases
"DOE, John",Individual,UKRAINE-EO13660,"President","123 Main St, City","United States","Johnny Doe; J. Doe"
```

### 2. EU Consolidated List

**Source**: European Union  
**Download**: <https://data.europa.eu/data/datasets/consolidated-list-of-persons-groups-and-entities-subject-to-eu-financial-sanctions>

**Expected Columns**:

- `name_1`, `name_2`, `name_3` - Entity names
- `entity_type` or `subject_type` - Type classification
- `regulation` - EU regulation reference
- `nationality` - Nationality/country
- `address` - Address information

**Example**:

```csv
name_1,name_2,entity_type,regulation,nationality,address
"Smith, Jane","Jane S","Person","Council Regulation (EU) 833/2014","GB","London, UK"
```

### 3. UN Consolidated List

**Source**: United Nations Security Council  
**Download**: <https://scsanctions.un.org/en/consolidated-list>

**Expected Columns**:

- `name`, `first_name`, `second_name` - Names
- `alias` - Alternative names
- `dataid` - UN identifier
- `committee` - UN committee
- `nationality_1`, `nationality_2` - Nationalities
- `address_1`, `address_2` - Addresses
- `listed_on` - Listing date

**Example**:

```csv
name,alias,dataid,committee,nationality_1,address_1,listed_on
"Brown, Robert","Bob Brown","QDi.123","1267/1989/2253 Committee","US","New York, USA","2024-01-15"
```

### 4. Generic Format

**Use for**: Custom sanctions lists or other compliance data

**Required Columns**:

- `name` - Entity name (required)
- `type` or `entity_type` - Entity type
- `country` - Country/nationality
- `address` - Address information
- `aliases` - Alternative names
- `program` or `list` - Source list/program
- `date` or `list_date` - Date added

**Example**:

```csv
name,type,country,address,aliases,program,date
"Wilson, Sarah","Individual","Canada","Toronto, ON","S. Wilson; Sarah W","Custom_Watch_List","2024-07-20"
```

## 🛠️ Import Methods

### Web Dashboard Import

#### Step 1: Access Import Interface

1. Login to the platform at <http://localhost:8501>
2. Go to **Admin Panel** → **Web Crawler**
3. Click the **📊 Compliance Analysis** tab
4. Click the **📥 Import Sanctions Data** subtab

#### Step 2: Upload Files

1. Use the file uploader to select one or more CSV files
2. The system will automatically:
   - Detect the CSV format
   - Preview file contents
   - Show column mappings
   - Estimate import time

#### Step 3: Configure Import

For each file, configure:

- **List Name**: Unique identifier for this data set
- **Format Type**: Auto-detect or manually specify
- **Target Table**: sanctions_entities or pep_entities
- **Batch Size**: Number of records to process at once

#### Step 4: Review and Import

1. Click **🔍 Preview Column Mapping** to verify field mappings
2. Click **📥 Import All Files** to start the import process
3. Monitor progress with the real-time progress bar
4. Review import results and statistics

### Command Line Import

#### Basic Import

```bash
# Import a single CSV file
python3 import_sanctions_csv.py --csv_file sanctions.csv --list_name "OFAC_SDN_2024"
```

#### Advanced Options

```bash
# Specify format and table
python3 import_sanctions_csv.py \
  --csv_file eu_sanctions.csv \
  --list_name "EU_Consolidated_2024" \
  --format eu_consolidated \
  --table sanctions_entities \
  --batch_size 500

# Import all CSV files from a directory
python3 import_sanctions_csv.py \
  --directory /data/sanctions_csv/ \
  --auto_import

# Preview a file before importing
python3 import_sanctions_csv.py \
  --csv_file large_file.csv \
  --preview
```

#### Check Database Statistics

```bash
# View current database contents
python3 import_sanctions_csv.py --stats
```

## 📊 Column Mapping

The system automatically maps CSV columns to database fields:

| Database Field | Possible CSV Columns |
|----------------|---------------------|
| `name` | name, sdn_name, entity_name, individual_name, name_1 |
| `aliases` | aliases, alternative_names, aka, also_known_as, name_2, name_3 |
| `entity_type` | entity_type, type, sdn_type, subject_type |
| `program` | program, sanction_program, list_type, regulation, committee |
| `address` | address, addresses, location, address_1, birth_place |
| `country` | country, country_code, nationality, nationality_1 |
| `list_date` | list_date, date_added, publication_date, listed_on |

### Custom Mapping

If your CSV has different column names, you can:

1. Rename columns in your CSV to match expected names
2. Use the web interface to manually adjust mappings
3. Modify the `field_mappings` in `/services/sanctions/csv_importer.py`

## 🎯 Best Practices

### Data Preparation

1. **Clean your CSV**:
   - Remove empty rows and columns
   - Ensure consistent date formats (YYYY-MM-DD preferred)
   - Use UTF-8 encoding for special characters

2. **Optimize for import**:
   - Keep files under 100MB for best performance
   - Use batch sizes of 1000-5000 records
   - Separate different data types (sanctions vs PEP)

### Import Strategy

1. **Start with preview**: Always preview files before importing
2. **Test with small batches**: Import a subset first to verify mapping
3. **Use meaningful list names**: Include date and source (e.g., "OFAC_SDN_20240722")
4. **Monitor progress**: Watch for errors during import

### Data Management

1. **Regular updates**: Set up a schedule to import updated lists
2. **Version control**: Use dated list names to track versions
3. **Cleanup**: Periodically remove old or test data
4. **Backup**: Export data before major updates

## 🔧 Troubleshooting

### Common Issues

#### Import Fails with Column Errors

```
❌ Error: Column 'name' not found
```

**Solution**: Check column mapping. Your CSV might use different column names.

#### Memory Issues with Large Files

```
❌ Error: Memory error during import
```

**Solutions**:

- Reduce batch size to 500-1000
- Split large files into smaller chunks
- Import during off-peak hours

#### Date Format Errors

```
❌ Error: Invalid date format
```

**Solution**: Convert dates to YYYY-MM-DD format in your CSV.

#### Character Encoding Issues

```
❌ Error: Unicode decode error
```

**Solution**: Save CSV with UTF-8 encoding.

### Verification Steps

#### Check Import Results

```bash
# View database statistics
python3 import_sanctions_csv.py --stats

# Or use the web interface:
# Admin Panel → Compliance Analysis → Manage Data
```

#### Verify Data Quality

1. Check total record counts match expectations
2. Verify key entities are properly imported
3. Test sanctions screening with known entities
4. Review error logs for any issues

## 📈 Performance Guidelines

### File Size Recommendations

- **Small files** (< 10MB): Standard settings work well
- **Medium files** (10-50MB): Use batch size 2000-3000
- **Large files** (> 50MB): Use batch size 1000, import during off-peak

### Import Speed

- **Typical speed**: 1000-5000 records per minute
- **Factors affecting speed**:
  - File size and complexity
  - Number of columns
  - System resources
  - Database size

## 🔗 Data Sources

### Official Sources

1. **OFAC SDN List**: <https://sanctionslist.ofac.treas.gov/>
2. **EU Consolidated List**: <https://data.europa.eu/data/datasets/consolidated-list-of-persons-groups-and-entities-subject-to-eu-financial-sanctions>
3. **UN Consolidated List**: <https://scsanctions.un.org/en/consolidated-list>
4. **UK Sanctions List**: <https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1178226/UK_Sanctions_List.csv>

### Commercial Sources

- World-Check (Thomson Reuters)
- Dow Jones Risk & Compliance
- LexisNexis World Compliance
- Accuity (now part of LexisNexis)

## 📞 Support

### Getting Help

1. **Check this guide** for common issues and solutions
2. **Review logs** in the platform or command line output
3. **Test with sample data** to isolate issues
4. **Use preview mode** to verify column mappings

### Additional Resources

- Platform documentation: `/docs/`
- API documentation: Available in the web interface
- Sample CSV files: `/data/samples/`

---

**Last Updated**: July 22, 2025  
**Platform Version**: Enhanced with CSV Import  
**Supported Formats**: OFAC SDN, EU Consolidated, UN Consolidated, Generic CSV
