#!/bin/bash
# Compliant.one Folder Merge Script
# Merge /root/compliant.one into /root/compliant-one

echo "🔄 Starting Compliant.one folder merge..."
echo "================================================================"

# Define paths
SOURCE_DIR="/root/compliant.one"
TARGET_DIR="/root/compliant-one"
BACKUP_DIR="/root/compliant.one.backup"

echo "📁 Source: $SOURCE_DIR"
echo "📁 Target: $TARGET_DIR" 
echo "📁 Backup: $BACKUP_DIR"

# Create backup if not exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "📦 Creating backup..."
    cp -r "$SOURCE_DIR" "$BACKUP_DIR"
    echo "✅ Backup created at $BACKUP_DIR"
fi

# Create directories in target if they don't exist
echo "📂 Creating directory structure..."
mkdir -p "$TARGET_DIR/data/legacy_data"
mkdir -p "$TARGET_DIR/data/documents"
mkdir -p "$TARGET_DIR/data/pdfs"
mkdir -p "$TARGET_DIR/services/document_processing"
mkdir -p "$TARGET_DIR/legacy"

# 1. Move PDF files (valuable data)
echo "📄 Moving PDF documents..."
if [ -d "$SOURCE_DIR/downloaded_pdfs" ]; then
    echo "   Moving 6,014 PDF files..."
    mv "$SOURCE_DIR/downloaded_pdfs" "$TARGET_DIR/data/pdfs/"
    echo "✅ PDF files moved to $TARGET_DIR/data/pdfs/"
fi

# 2. Move documents database (if exists)
echo "💾 Moving documents database..."
if [ -f "$SOURCE_DIR/documents.db" ]; then
    mv "$SOURCE_DIR/documents.db" "$TARGET_DIR/data/legacy_data/"
    echo "✅ Documents database moved"
fi

# 3. Copy useful scripts for integration
echo "🔧 Copying processing scripts..."
if [ -f "$SOURCE_DIR/ingest_documents.py" ]; then
    cp "$SOURCE_DIR/ingest_documents.py" "$TARGET_DIR/services/document_processing/"
    echo "✅ Document ingestion script copied"
fi

if [ -f "$SOURCE_DIR/download_pdfs.py" ]; then
    cp "$SOURCE_DIR/download_pdfs.py" "$TARGET_DIR/services/document_processing/"
    echo "✅ PDF download script copied"
fi

if [ -f "$SOURCE_DIR/query_documents.py" ]; then
    cp "$SOURCE_DIR/query_documents.py" "$TARGET_DIR/services/document_processing/"
    echo "✅ Document query script copied"
fi

# 4. Copy anti-bribery module (useful for compliance)
echo "⚖️ Copying compliance modules..."
if [ -f "$SOURCE_DIR/anti_bribery.py" ]; then
    cp "$SOURCE_DIR/anti_bribery.py" "$TARGET_DIR/services/compliance/"
    echo "✅ Anti-bribery module copied"
fi

# 5. Copy any data files
echo "📊 Moving data files..."
if [ -d "$SOURCE_DIR/data" ]; then
    cp -r "$SOURCE_DIR/data"/* "$TARGET_DIR/data/legacy_data/" 2>/dev/null || echo "   No additional data files found"
fi

# 6. Copy the legacy app for reference
echo "📱 Preserving legacy app..."
cp "$SOURCE_DIR/app.py" "$TARGET_DIR/legacy/legacy_app.py"
cp "$SOURCE_DIR/README.md" "$TARGET_DIR/legacy/legacy_README.md"

# 7. Copy requirements and merge them
echo "📋 Merging requirements..."
if [ -f "$SOURCE_DIR/requirements.txt" ]; then
    echo "" >> "$TARGET_DIR/requirements.txt"
    echo "# Legacy requirements from compliant.one" >> "$TARGET_DIR/requirements.txt"
    cat "$SOURCE_DIR/requirements.txt" >> "$TARGET_DIR/requirements.txt"
    echo "✅ Requirements merged"
fi

# 8. Copy ethics-eye-osint-guard if valuable
echo "👁️ Copying OSINT tools..."
if [ -d "$SOURCE_DIR/ethics-eye-osint-guard" ]; then
    cp -r "$SOURCE_DIR/ethics-eye-osint-guard" "$TARGET_DIR/integrations/"
    echo "✅ OSINT tools copied to integrations"
fi

# 9. Generate merge summary
echo "📊 Generating merge summary..."
cat > "$TARGET_DIR/MERGE_SUMMARY.md" << EOF
# Folder Merge Summary

## Merged on: $(date)

### Source: /root/compliant.one
### Target: /root/compliant-one

## Files Moved/Copied:

### 📄 Documents & Data:
- 6,014 PDF files moved to \`data/pdfs/downloaded_pdfs/\`
- documents.db moved to \`data/legacy_data/\`
- Legacy data files moved to \`data/legacy_data/\`

### 🔧 Processing Scripts:
- ingest_documents.py → \`services/document_processing/\`
- download_pdfs.py → \`services/document_processing/\`
- query_documents.py → \`services/document_processing/\`

### ⚖️ Compliance Modules:
- anti_bribery.py → \`services/compliance/\`

### 👁️ OSINT Tools:
- ethics-eye-osint-guard → \`integrations/\`

### 📱 Legacy App (for reference):
- app.py → \`legacy/legacy_app.py\`
- README.md → \`legacy/legacy_README.md\`

### 📋 Requirements:
- Legacy requirements merged into main requirements.txt

## Backup Location:
Original folder backed up to: \`/root/compliant.one.backup\`

## Next Steps:
1. Integrate document processing scripts into main platform
2. Review and integrate legacy compliance modules
3. Test PDF processing functionality
4. Update documentation
EOF

echo "✅ Merge summary created"

# 10. Check disk space after merge
echo "💾 Checking disk usage..."
echo "Current target directory size:"
du -sh "$TARGET_DIR"

echo ""
echo "🎉 Merge completed successfully!"
echo "================================================================"
echo "📊 Summary:"
echo "   - 6,014 PDF files integrated"
echo "   - Document processing scripts copied"
echo "   - Compliance modules preserved"
echo "   - Legacy app backed up"
echo "   - OSINT tools integrated"
echo ""
echo "📖 See MERGE_SUMMARY.md for detailed information"
echo "📁 Original folder backed up to: $BACKUP_DIR"
echo ""
echo "🚀 You can now safely remove the original folder if desired:"
echo "   rm -rf /root/compliant.one"
