#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# -----------------------
# DISCLAIMER
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
# CHECK SUDO
# -----------------------
if [[ $EUID -ne 0 ]]; then
    echo "Error: This script must be run with sudo."
    echo "Example: sudo ./install.sh"
    exit 1
fi

CURRENT_USER=${SUDO_USER:-$(whoami)}
echo "Running commands as user: $CURRENT_USER"

# Helper function to run commands as normal user
run_as_user() {
    sudo -u "$CURRENT_USER" bash -c "$1"
}

# -----------------------
# CONFIGURATION
# -----------------------
REPO_DIR="amwa"
REPO_URL="https://github.com/rueedlinger/${REPO_DIR}"
VENV_DIR=".setup"
FRONTEND_DIR="frontend"
SERVICE_FILE="/etc/systemd/system/amwa.service"

USER_HOME=$(eval echo "~$CURRENT_USER")
REPO_PATH="${USER_HOME}/${REPO_DIR}"

# -----------------------
# STEP 0: Clone repository (as user)
# -----------------------
echo ""
echo "=== Step 0: Cloning repository ==="
if [ ! -d "$REPO_PATH" ]; then
    run_as_user "git clone $REPO_URL $REPO_PATH"
else
    run_as_user "git -C $REPO_PATH pull"
fi

# Ensure correct ownership
chown -R "$CURRENT_USER":"$CURRENT_USER" "$REPO_PATH"

# -----------------------
# STEP 1: Check dependencies (user)
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
# STEP 2: Setup Python environment (user)
# -----------------------
echo ""
echo "=== Step 2: Setting up Python virtual environment ==="
run_as_user "
cd $REPO_PATH
if [ ! -d '$VENV_DIR' ]; then
    python3 -m venv $VENV_DIR
fi
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install uv
"

# -----------------------
# STEP 3: Build backend (user)
# -----------------------
echo ""
echo "=== Step 3: Building backend ==="
run_as_user "
cd $REPO_PATH
source $VENV_DIR/bin/activate
uv sync --all-groups
"

# -----------------------
# STEP 4: Build frontend (user)
# -----------------------
echo ""
echo "=== Step 4: Building frontend ==="
if run_as_user "[ -d '$REPO_PATH/$FRONTEND_DIR' ]"; then
    run_as_user "
cd $REPO_PATH
npm ci --include=dev --prefix $FRONTEND_DIR
npm run build --prefix $FRONTEND_DIR
"
else
    echo "Warning: Frontend directory '$FRONTEND_DIR' does not exist."
    exit 1
fi

# -----------------------
# STEP 5: Copy frontend build into backend (user)
# -----------------------
echo ""
echo "=== Step 5: Copying frontend build ==="
run_as_user "
cd $REPO_PATH
mkdir -p app/dist
cp -r $FRONTEND_DIR/dist/. app/dist/
"

# -----------------------
# STEP 6: ANT+ USB setup (root)
# -----------------------
echo ""
echo "=== Step 6: Optional ANT+ USB adapter setup ==="

# Add user to plugdev group
usermod -aG plugdev "$CURRENT_USER"
echo "Added $CURRENT_USER to plugdev group. Log out and back in if necessary."

read -r -p "Do you want to configure the ANT+ USB adapter? [yes/no]: " ANTUSB_CHOICE

if [[ "$ANTUSB_CHOICE" == "yes" ]]; then
   

    # Ask user for path to udev rule file
    read -r -p "Please provide the path to your ANT+ udev rule file (e.g., antusb.rules): " ANTUSB_RULE_FILE

    # Check that file exists
    if [ ! -f "$ANTUSB_RULE_FILE" ]; then
        echo "Error: File '$ANTUSB_RULE_FILE' does not exist. Aborting ANT+ USB setup."
        exit 1
    fi

    # Copy the udev rule to /etc/udev/rules.d/
    UDEV_RULE_DEST="/etc/udev/rules.d/99-antusb.rules"
    cp "$ANTUSB_RULE_FILE" "$UDEV_RULE_DEST"
    echo "Copied udev rule to $UDEV_RULE_DEST"

    # Apply the new rule
    udevadm control --reload-rules
    udevadm trigger
    echo "ANT+ USB udev rule applied successfully."

else
    echo "Skipping ANT+ USB adapter setup."
fi

# -----------------------
# STEP 7: Install systemd service (root)
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
# STEP 8: Show service status
# -----------------------
echo ""
echo "=== Step 8: Service status ==="
systemctl status amwa --no-pager

echo ""
echo "=== Installation finished successfully ==="