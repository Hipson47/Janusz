#!/bin/bash

# AI Agent Knowledge Base Pipeline Script
# Automates Document -> YAML -> TOON conversion
# Supports: PDF, MD, TXT, DOCX, HTML, RTF, EPUB

# Function to check and install TOON CLI
check_and_install_toon() {
    # Check if toon command already exists
    if command -v toon >/dev/null 2>&1; then
        echo "✓ TOON CLI is already installed"
        return 0
    fi

    echo "🔍 TOON CLI not found, attempting to install..."

    # Check if cargo is available (preferred method according to README)
    if command -v cargo >/dev/null 2>&1; then
        echo "📦 Installing TOON CLI via cargo..."
        if cargo install toon; then
            echo "✓ TOON CLI installed successfully via cargo"
            return 0
        else
            echo "❌ Failed to install via cargo, trying binary download..."
        fi
    else
        echo "⚠️  Cargo not found, trying binary download..."
    fi

    # Detect OS and architecture for binary download
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        echo "❌ Unsupported OS: $OSTYPE"
        echo "   Please install TOON CLI manually from: https://github.com/toon-format/toon"
        return 1
    fi

    ARCH=$(uname -m)
    if [[ "$ARCH" == "x86_64" ]]; then
        ARCH="x86_64"
    elif [[ "$ARCH" == "arm64" ]] || [[ "$ARCH" == "aarch64" ]]; then
        ARCH="aarch64"
    else
        echo "❌ Unsupported architecture: $ARCH"
        echo "   Please install TOON CLI manually from: https://github.com/toon-format/toon"
        return 1
    fi

    # Create temp directory for download
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"

    # Download binary from GitHub releases
    BINARY_NAME="toon-$OS-$ARCH"
    DOWNLOAD_URL="https://github.com/toon-format/toon/releases/latest/download/$BINARY_NAME"

    echo "📥 Downloading TOON CLI binary for $OS-$ARCH..."
    if curl -L -o toon "$DOWNLOAD_URL"; then
        chmod +x toon

        # Try to install to a system directory, fallback to local directory
        if [[ -w "/usr/local/bin" ]]; then
            sudo mv toon /usr/local/bin/ 2>/dev/null && {
                echo "✓ TOON CLI installed to /usr/local/bin/"
                cd - >/dev/null
                rm -rf "$TEMP_DIR"
                return 0
            }
        fi

        # Try user local bin directory
        LOCAL_BIN="$HOME/.local/bin"
        mkdir -p "$LOCAL_BIN" 2>/dev/null && mv toon "$LOCAL_BIN/" 2>/dev/null && {
            export PATH="$LOCAL_BIN:$PATH"
            echo "✓ TOON CLI installed to $LOCAL_BIN/ and added to PATH"
            cd - >/dev/null
            rm -rf "$TEMP_DIR"
            return 0
        }

        # Fallback: use current directory and add to PATH
        mv toon ./toon 2>/dev/null && {
            export PATH="$(pwd):$PATH"
            echo "✓ TOON CLI added to PATH for current session"
            cd - >/dev/null
            rm -rf "$TEMP_DIR"
            return 0
        }
    fi

    # Cleanup on failure
    cd - >/dev/null
    rm -rf "$TEMP_DIR"
    echo "❌ Failed to download TOON CLI binary"
    echo "   Please install manually from: https://github.com/toon-format/toon"
    return 1
}

echo "🔄 Starting AI Agent Knowledge Base Pipeline..."
echo "Documents → YAML → TOON"
echo "Supported formats: PDF, MD, TXT, DOCX, HTML, RTF, EPUB"
echo

# KROK 0: Check and install TOON CLI
echo "🔧 Checking TOON CLI installation..."
check_and_install_toon

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install TOON CLI"
    exit 1
fi

echo "✓ TOON CLI ready"
echo

# Step 1: Convert documents to YAML
echo "📄 Converting documents to YAML..."
python -m janusz.cli convert

if [ $? -ne 0 ]; then
    echo "❌ Error: Document to YAML conversion failed"
    exit 1
fi

echo "✓ Document to YAML conversion completed"
echo

# Step 2: Convert YAMLs to TOON
echo "🎨 Converting YAMLs to TOON..."
python -m janusz.cli toon

if [ $? -ne 0 ]; then
    echo "❌ Error: YAML to TOON conversion failed"
    exit 1
fi

echo "✓ YAML to TOON conversion completed"
echo

echo "🎉 Pipeline completed successfully: PDF → YAML → TOON"
