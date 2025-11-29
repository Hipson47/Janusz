#!/bin/bash

# AI Agent Knowledge Base Pipeline Script
# Automates Document -> YAML -> TOON conversion
# Supports: PDF, MD, TXT, DOCX, HTML, RTF, EPUB

echo "🔄 Starting AI Agent Knowledge Base Pipeline..."
echo "Documents → YAML → TOON"
echo "Supported formats: PDF, MD, TXT, DOCX, HTML, RTF, EPUB"
echo

# Step 1: Convert PDFs to YAML
echo "📄 Converting PDFs to YAML..."
python pdf_yaml_converter.py

if [ $? -ne 0 ]; then
    echo "❌ Error: PDF to YAML conversion failed"
    exit 1
fi

echo "✓ PDF to YAML conversion completed"
echo

# Step 2: Convert YAMLs to TOON
echo "🎨 Converting YAMLs to TOON..."
python toon.py

if [ $? -ne 0 ]; then
    echo "❌ Error: YAML to TOON conversion failed"
    exit 1
fi

echo "✓ YAML to TOON conversion completed"
echo

echo "🎉 Pipeline completed successfully: PDF → YAML → TOON"
