#!/usr/bin/env bash
set -e
set -o pipefail

# -----------------------
# Step 0: Clone repository
# -----------------------
REPO_DIR="amwa"
REPO_URL="https://github.com/rueedlinger/${REPO_DIR}"

echo "📥 Cloning repository..."
if [ ! -d "$REPO_DIR" ]; then
    git clone "$REPO_URL"
else
    echo "⚠️ Repository already exists. Pulling latest changes..."
    cd "$REPO_DIR" && git pull && cd ..
fi

# Work in parent directory
cd "$REPO_DIR"

# -----------------------
# Step 1: Build frontend
# -----------------------


echo "📦 Building frontend..."
cd frontend

# Ensure Node.js is installed
if ! command -v node >/dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js v20+."
    exit 1
fi

echo "Node version: $(node -v)"
echo "npm version: $(npm -v)"

npm install --include=dev
npm install @tailwindcss/vite

npm run build
echo "✅ Frontend build complete."
cd ..

# -----------------------
# Step 2: Setup backend
# -----------------------
echo "🐍 Setting up backend..."

# Ensure Python is installed
if ! command -v python3 >/dev/null; then
    echo "❌ Python3 is not installed."
    exit 1
fi

echo "Python version: $(python3 --version)"

# Create a virtual environment if it doesn't exist
# to install uv
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "⚡ Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"


# Upgrade pip in venv
pip install --upgrade pip
echo "pip version: $(pip --version)"


# Install uv in venv
pip install uv

# Sync all dependencies via uv (Poetry alternative)
uv sync --all-groups

# Copy frontend build into backend dist folder
mkdir -p app/dist
cp -r frontend/dist/* app/dist/

echo "✅ Backend setup complete."

# -----------------------
# Step 3: Finish
# -----------------------
echo "✅ Finished"
