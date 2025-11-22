#!/bin/bash
#
# Simple SCP script to download all .sql files
# Place this script in /Users/kakumanusairam/Downloads/MetaMind/ and run it
#
# Usage:
#   ./download_sql_files_simple.sh
#

# ============================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================
REMOTE_USER="devuser"                    # Your remote username
REMOTE_HOST="your-server.com"            # Your remote server hostname/IP
REMOTE_PATH="/home/devuser/sai_dev/metamind/extracted_meta"
LOCAL_PATH="/Users/kakumanusairam/Downloads/MetaMind"

# ============================================
# SCRIPT (No need to modify below)
# ============================================

REMOTE="${REMOTE_USER}@${REMOTE_HOST}"

echo "=========================================="
echo "Download SQL Files Script"
echo "=========================================="
echo "Remote Server: ${REMOTE}"
echo "Remote Path: ${REMOTE_PATH}"
echo "Local Path: ${LOCAL_PATH}"
echo "=========================================="
echo ""

# Create local directory
mkdir -p "${LOCAL_PATH}"

# Check if rsync is available (preferred method)
if command -v rsync &> /dev/null; then
    echo "Using rsync to download files..."
    echo ""
    
    rsync -avz --progress \
        --include="*/" \
        --include="*.sql" \
        --exclude="*" \
        "${REMOTE}:${REMOTE_PATH}/" \
        "${LOCAL_PATH}/"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Download completed successfully!"
        echo ""
        echo "Files location: ${LOCAL_PATH}"
        echo "Total .sql files: $(find "${LOCAL_PATH}" -name "*.sql" -type f 2>/dev/null | wc -l | tr -d ' ')"
    else
        echo ""
        echo "✗ Download failed. Please check:"
        echo "  1. Remote server connection"
        echo "  2. SSH key authentication"
        echo "  3. Remote path exists"
        exit 1
    fi
else
    echo "rsync not found. Using SCP method..."
    echo ""
    
    # Get list of SQL files
    echo "Finding SQL files on remote server..."
    SQL_FILES=$(ssh "${REMOTE}" "find ${REMOTE_PATH} -name '*.sql' -type f" 2>/dev/null)
    
    if [ $? -ne 0 ]; then
        echo "✗ Failed to connect to remote server"
        echo "Please check your SSH connection and credentials"
        exit 1
    fi
    
    if [ -z "$SQL_FILES" ]; then
        echo "✗ No .sql files found"
        exit 1
    fi
    
    TOTAL=$(echo "$SQL_FILES" | wc -l | tr -d ' ')
    echo "Found ${TOTAL} .sql files"
    echo ""
    
    COUNT=0
    while IFS= read -r sql_file; do
        if [ -n "$sql_file" ]; then
            COUNT=$((COUNT + 1))
            
            # Get relative path
            RELATIVE_PATH="${sql_file#${REMOTE_PATH}/}"
            LOCAL_FILE="${LOCAL_PATH}/${RELATIVE_PATH}"
            LOCAL_DIR=$(dirname "$LOCAL_FILE")
            
            # Create directory and download
            mkdir -p "$LOCAL_DIR"
            echo "[${COUNT}/${TOTAL}] $(basename "$sql_file")"
            scp "${REMOTE}:${sql_file}" "$LOCAL_FILE" > /dev/null 2>&1
            
            if [ $? -eq 0 ]; then
                echo "  ✓"
            else
                echo "  ✗ Failed"
            fi
        fi
    done <<< "$SQL_FILES"
    
    echo ""
    echo "✓ Download completed!"
    echo "Files location: ${LOCAL_PATH}"
fi

echo ""
echo "=========================================="

