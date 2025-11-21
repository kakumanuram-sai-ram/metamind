#!/bin/bash
# Setup script using uv for Superset Dashboard Extractor

cd "$(dirname "$0")"

# Add uv to PATH if not already there
export PATH="$HOME/.local/bin:$PATH"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "Creating virtual environment with uv..."
uv venv meta_env

echo "Installing dependencies..."
source meta_env/bin/activate
uv pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment:"
echo "  source meta_env/bin/activate"
echo ""
echo "To run the API server:"
echo "  python scripts/api_server.py"

