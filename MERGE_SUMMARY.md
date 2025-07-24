# Folder Merge Summary

## Merged on: Tue Jul 22 02:44:59 PKT 2025

### Source: /root/compliant.one
### Target: /root/compliant-one

## Files Moved/Copied:

### 📄 Documents & Data:
- 6,014 PDF files moved to `data/pdfs/downloaded_pdfs/`
- documents.db moved to `data/legacy_data/`
- Legacy data files moved to `data/legacy_data/`

### 🔧 Processing Scripts:
- ingest_documents.py → `services/document_processing/`
- download_pdfs.py → `services/document_processing/`
- query_documents.py → `services/document_processing/`

### ⚖️ Compliance Modules:
- anti_bribery.py → `services/compliance/`

### 👁️ OSINT Tools:
- ethics-eye-osint-guard → `integrations/`

### 📱 Legacy App (for reference):
- app.py → `legacy/legacy_app.py`
- README.md → `legacy/legacy_README.md`

### 📋 Requirements:
- Legacy requirements merged into main requirements.txt

## Backup Location:
Original folder backed up to: `/root/compliant.one.backup`

## Next Steps:
1. Integrate document processing scripts into main platform
2. Review and integrate legacy compliance modules
3. Test PDF processing functionality
4. Update documentation
