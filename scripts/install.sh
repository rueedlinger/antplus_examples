#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# -----------------------
# Disclaimer
# -----------------------
echo "======================================"
echo " AMWA Installer"
echo "======================================"
echo ""
echo "DISCLAIMER:"
echo "This script will install and configure the AMWA service"
echo "on your system. It will modify systemd services and"
echo "write files to /etc/systemd/system."
echo ""
echo "NO WARRANTY is provided. Use at your own risk."
echo ""

read -r -p "Type 'yes' to continue: " CONFIRM
if [[ "$CONFIRM" != "yes" ]]; then
    echo "Aborted."
    exit 1
fi

# -----------------------
# Check sudo
# -----------------------
if [[ $EUID -ne 0 ]]; then
    echo "Error: This script must be run with sudo."
    echo "Example:"
    echo "sudo ./install.sh"
    exit 1
fi

CURRENT_USER=${SUDO_USER:-$(whoami)}

# -----------------------
# Configuration
# -----------------------
REPO_DIR="amwa"
REPO_URL="https://github.com/rueedlinger/${REPO_DIR}"
VENV_DIR=".setup"
FRONTEND_DIR="frontend"
SERVICE_FILE="/etc/systemd/system/amwa.service"

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

echo "Activating virtual environment..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "Upgrading pip..."
pip install --upgrade pip
echo "pip version: $(pip --version)"

echo "Installing uv..."
pip install uv
command -v uv >/dev/null || { echo "uv installation failed"; exit 1; }

# -----------------------
# Step 3: Navigate to repository
# -----------------------
echo ""
echo "=== Step 3: Entering repository directory ==="
cd "$REPO_DIR"

REPO_PATH="$(pwd)"

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
    npm ci --include=dev --prefix "$FRONTEND_DIR"
    npm run build --prefix "$FRONTEND_DIR"
else
    echo "Warning: Frontend directory '$FRONTEND_DIR' does not exist."
    exit 1
fi

# -----------------------
# Step 6: Copy frontend build
# -----------------------
echo ""
echo "=== Step 6: Copy frontend build ==="

mkdir -p app/dist
cp -r "$FRONTEND_DIR/dist/." app/dist/

# -----------------------
# Step 7: Install systemd service
# -----------------------
echo ""
echo "=== Step 7: Installing systemd service ==="

SERVICE_SRC="${REPO_PATH}/scripts/amwa.service"

if [ ! -f "$SERVICE_SRC" ]; then
    echo "Service file not found: $SERVICE_SRC"
    exit 1
fi

echo "Copying service file..."
cp "$SERVICE_SRC" "$SERVICE_FILE"

echo "Configuring service..."

sed -i "s|ExecStart=.*|ExecStart=${REPO_PATH}/scripts/start.sh|" "$SERVICE_FILE"
sed -i "s|WorkingDirectory=.*|WorkingDirectory=${REPO_PATH}|" "$SERVICE_FILE"
sed -i "s|User=.*|User=${CURRENT_USER}|" "$SERVICE_FILE"

echo "Reloading systemd..."
systemctl daemon-reload

echo "Enabling service..."
systemctl enable amwa

echo "Starting service..."
systemctl start amwa

# -----------------------
# Step 8: Status
# -----------------------
echo ""
echo "=== Step 8: Service status ==="

systemctl status amwa --no-pager

echo ""
echo "=== Installation finished successfully ==="