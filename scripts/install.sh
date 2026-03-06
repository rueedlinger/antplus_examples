#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# -----------------------
# Configuration
# -----------------------
REPO_DIR="amwa"
REPO_URL="https://github.com/rueedlinger/${REPO_DIR}"
VENV_DIR=".setup"
FRONTEND_DIR="frontend"

# -----------------------
# Step 0: Clone repository
# -----------------------
echo ""
echo "=== Step 0: Cloning repository ==="
if [ ! -d "$REPO_DIR" ]; then
    echo "Cloning $REPO_URL into $REPO_DIR..."
    git clone "$REPO_URL"
else
    echo "Repository exists. Pulling latest changes..."
    git -C "$REPO_DIR" pull
fi

# -----------------------
# Step 1: Check dependencies
# -----------------------
echo ""
echo "=== Step 1: Checking dependencies ==="
dependencies=(python3 node npm git)

for cmd in "${dependencies[@]}"; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: $cmd is not installed."
        exit 1
    fi
done

echo "Python version: $(python3 --version)"
echo "Node version: $(node -v)"
echo "npm version: $(npm -v)"
echo "Git version: $(git --version)"

# -----------------------
# Step 2: Setup Python environment
# -----------------------
echo ""
echo "=== Step 2: Setting up Python virtual environment ==="
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "Activating virtual environment..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo "pip version: $(pip --version)"

# Install uv
echo "Installing uv..."
pip install uv

# -----------------------
# Step 3: Navigate to repository
# -----------------------
echo ""
echo "=== Step 3: Entering repository directory ==="
cd "$REPO_DIR"

# -----------------------
# Step 4: Build backend
# -----------------------
echo ""
echo "=== Step 4: Building backend ==="
uv sync --all-groups

# -----------------------
# Step 5: Build frontend
# -----------------------
echo ""
echo "=== Step 5: Building frontend ==="
if [ -d "$FRONTEND_DIR" ]; then
    npm install --include=dev --prefix "$FRONTEND_DIR"
else
    echo "Warning: Frontend directory '$FRONTEND_DIR' does not exist. Skipping npm install."
fi

# -----------------------
# Step 6: Finish
# -----------------------
echo ""
echo "=== Step 6: Setup and build finished successfully! ==="