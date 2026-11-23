#!/usr/bin/env bash
# Setup script for Reverse Engineer Anything (REA) in Google Antigravity on Linux / macOS.

set -e

echo "=========================================================="
echo " Reverse Engineer Anything (REA) - Antigravity Setup      "
echo "=========================================================="

# 1. Check Python
echo "[1/4] Checking Python environment..."
if command -v python3 >/dev/null 2>&1; then
    echo "  Found Python: $(python3 --version)"
elif command -v python >/dev/null 2>&1; then
    echo "  Found Python: $(python --version)"
else
    echo "  WARNING: Python not found. Please install Python 3.8+."
fi

# 2. Check Node.js
echo "[2/4] Checking Node.js environment..."
if command -v node >/dev/null 2>&1; then
    echo "  Found Node: $(node -v)"
else
    echo "  WARNING: Node.js not found."
fi

# 3. Test rea_helper.py
echo "[3/4] Verifying REA Companion Helper..."
python3 scripts/rea_helper.py --help >/dev/null 2>&1 || python scripts/rea_helper.py --help >/dev/null 2>&1
echo "  REA Companion script verified successfully."

# 4. Global Antigravity Plugin Setup
echo "[4/4] Registering Global Antigravity Plugin..."
GLOBAL_PLUGIN_DIR="$HOME/.gemini/config/plugins/reverse-engineer-anything"
mkdir -p "$GLOBAL_PLUGIN_DIR"
cp .agents/plugin.json "$GLOBAL_PLUGIN_DIR/plugin.json"
cp .agents/mcp_config.json "$GLOBAL_PLUGIN_DIR/mcp_config.json"
cp -r .agents/skills "$GLOBAL_PLUGIN_DIR/"
cp -r .agents/rules "$GLOBAL_PLUGIN_DIR/"
cp -r .agents/agents "$GLOBAL_PLUGIN_DIR/"

echo ""
echo "Setup Complete! REA is now installed for Antigravity & Gemini AI."

