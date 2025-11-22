#!/bin/bash
#
# Script to download all .sql files from extracted_meta folder to local machine
#
# Usage:
#   ./download_sql_files.sh [remote_user@remote_host]
#
# Example:
#   ./download_sql_files.sh devuser@your-server.com
#

# Configuration
REMOTE_USER_HOST="${1:-devuser@localhost}"
REMOTE_BASE_DIR="/home/devuser/sai_dev/metamind/extracted_meta"
LOCAL_DEST_DIR="/Users/kakumanusairam/Downloads/MetaMind"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Download SQL Files from Remote Server"
echo "=========================================="
echo "Remote: ${REMOTE_USER_HOST}"
echo "Source: ${REMOTE_BASE_DIR}"
echo "Destination: ${LOCAL_DEST_DIR}"
echo "=========================================="
echo ""

# Create local destination directory if it doesn't exist
mkdir -p "${LOCAL_DEST_DIR}"

# Check if remote host is localhost (for testing)
if [[ "${REMOTE_USER_HOST}" == *"localhost"* ]] && [[ "${REMOTE_USER_HOST}" != *"@"* ]]; then
    echo -e "${YELLOW}Warning: Using localhost. Make sure to provide remote host as argument.${NC}"
    echo "Example: ./download_sql_files.sh devuser@your-server.com"
    echo ""
fi

# Method 1: Using rsync (recommended - preserves structure, efficient)
echo -e "${GREEN}Method 1: Using rsync (recommended)${NC}"
echo "Downloading all .sql files..."

if command -v rsync &> /dev/null; then
    rsync -avz --include="*/" --include="*.sql" --exclude="*" \
        "${REMOTE_USER_HOST}:${REMOTE_BASE_DIR}/" \
        "${LOCAL_DEST_DIR}/"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Download completed successfully using rsync!${NC}"
        echo ""
        echo "Files downloaded to: ${LOCAL_DEST_DIR}"
        echo ""
        echo "Downloaded files:"
        find "${LOCAL_DEST_DIR}" -name "*.sql" -type f | wc -l | xargs echo "  Total .sql files:"
        find "${LOCAL_DEST_DIR}" -name "*.sql" -type f | head -10
        if [ $(find "${LOCAL_DEST_DIR}" -name "*.sql" -type f | wc -l) -gt 10 ]; then
            echo "  ... and more"
        fi
    else
        echo -e "${RED}✗ Download failed!${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}rsync not found. Trying SCP method...${NC}"
    
    # Method 2: Using SCP (fallback)
    echo -e "${GREEN}Method 2: Using SCP${NC}"
    
    # First, get list of all .sql files from remote
    echo "Finding all .sql files on remote server..."
    SQL_FILES=$(ssh "${REMOTE_USER_HOST}" "find ${REMOTE_BASE_DIR} -name '*.sql' -type f")
    
    if [ -z "$SQL_FILES" ]; then
        echo -e "${RED}✗ No .sql files found on remote server${NC}"
        exit 1
    fi
    
    echo "Found $(echo "$SQL_FILES" | wc -l) .sql files"
    echo ""
    
    # Download each file, preserving directory structure
    COUNT=0
    TOTAL=$(echo "$SQL_FILES" | wc -l)
    
    while IFS= read -r sql_file; do
        if [ -n "$sql_file" ]; then
            COUNT=$((COUNT + 1))
            
            # Get relative path from REMOTE_BASE_DIR
            RELATIVE_PATH="${sql_file#${REMOTE_BASE_DIR}/}"
            LOCAL_FILE="${LOCAL_DEST_DIR}/${RELATIVE_PATH}"
            LOCAL_DIR=$(dirname "$LOCAL_FILE")
            
            # Create local directory structure
            mkdir -p "$LOCAL_DIR"
            
            # Download file
            echo "[$COUNT/$TOTAL] Downloading: $RELATIVE_PATH"
            scp "${REMOTE_USER_HOST}:${sql_file}" "$LOCAL_FILE"
            
            if [ $? -eq 0 ]; then
                echo -e "  ${GREEN}✓${NC} Downloaded"
            else
                echo -e "  ${RED}✗${NC} Failed"
            fi
        fi
    done <<< "$SQL_FILES"
    
    echo ""
    echo -e "${GREEN}✓ Download completed!${NC}"
    echo "Files downloaded to: ${LOCAL_DEST_DIR}"
fi

echo ""
echo "=========================================="
echo "Download Summary"
echo "=========================================="
echo "Destination: ${LOCAL_DEST_DIR}"
echo "Total .sql files: $(find "${LOCAL_DEST_DIR}" -name "*.sql" -type f 2>/dev/null | wc -l | tr -d ' ')"
echo "=========================================="

