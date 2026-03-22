#!/bin/bash
set -e

# ============================================================
# HotelBook EC2 Server Setup Script
# One-time provisioning for Ubuntu 22.04 (or compatible)
# Usage: sudo bash setup-server.sh
# ============================================================

REPO_URL="https://github.com/USER/claude_test.git"
APP_DIR="/opt/hotelbook"
SWAP_SIZE="2G"

echo "=== HotelBook Server Setup ==="
echo ""

# -----------------------------------------------------------
# 1. Update system packages
# -----------------------------------------------------------
echo "[1/7] Updating system packages..."
apt-get update && apt-get upgrade -y

# -----------------------------------------------------------
# 2. Install Docker Engine and Docker Compose plugin
# -----------------------------------------------------------
if command -v docker &> /dev/null; then
    echo "[2/7] Docker already installed, skipping."
else
    echo "[2/7] Installing Docker Engine..."
    apt-get install -y ca-certificates curl gnupg

    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

# -----------------------------------------------------------
# 3. Add current user to docker group
# -----------------------------------------------------------
echo "[3/7] Configuring docker group..."
DEPLOY_USER="${SUDO_USER:-$USER}"
if id -nG "$DEPLOY_USER" | grep -qw docker; then
    echo "  User '$DEPLOY_USER' already in docker group."
else
    usermod -aG docker "$DEPLOY_USER"
    echo "  Added '$DEPLOY_USER' to docker group."
fi

# -----------------------------------------------------------
# 4. Create swap file (idempotent)
# -----------------------------------------------------------
if [ -f /swapfile ]; then
    echo "[4/7] Swap file already exists, skipping."
else
    echo "[4/7] Creating ${SWAP_SIZE} swap file..."
    fallocate -l ${SWAP_SIZE} /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile

    # Persist in fstab if not already there
    if ! grep -q '/swapfile' /etc/fstab; then
        echo '/swapfile none swap sw 0 0' >> /etc/fstab
    fi
    echo "  Swap enabled."
fi

# -----------------------------------------------------------
# 5. Create application directory
# -----------------------------------------------------------
if [ -d "$APP_DIR" ]; then
    echo "[5/7] Application directory $APP_DIR already exists, skipping."
else
    echo "[5/7] Creating application directory..."
    mkdir -p "$APP_DIR"
    chown "$DEPLOY_USER":"$DEPLOY_USER" "$APP_DIR"
fi

# -----------------------------------------------------------
# 6. Clone repository
# -----------------------------------------------------------
if [ -d "$APP_DIR/.git" ]; then
    echo "[6/7] Repository already cloned, skipping."
else
    echo "[6/7] Cloning repository..."
    sudo -u "$DEPLOY_USER" git clone "$REPO_URL" "$APP_DIR"
fi

# -----------------------------------------------------------
# 7. Create keys directory
# -----------------------------------------------------------
echo "[7/7] Ensuring keys directory exists..."
mkdir -p "$APP_DIR/keys"
chmod 700 "$APP_DIR/keys"
chown "$DEPLOY_USER":"$DEPLOY_USER" "$APP_DIR/keys"

# -----------------------------------------------------------
# Summary
# -----------------------------------------------------------
echo ""
echo "=== Setup Complete ==="
echo ""
echo "What was configured:"
echo "  - System packages updated"
echo "  - Docker Engine + Compose plugin installed"
echo "  - User '$DEPLOY_USER' added to docker group"
echo "  - ${SWAP_SIZE} swap file at /swapfile"
echo "  - Application directory at $APP_DIR"
echo "  - Repository cloned from $REPO_URL"
echo "  - Keys directory at $APP_DIR/keys (mode 700)"
echo ""
echo "Next steps:"
echo "  1. Log out and back in for docker group to take effect"
echo "  2. Configure these GitHub Secrets in your repository:"
echo "     - EC2_HOST        (this server's public IP or hostname)"
echo "     - EC2_USER        ($DEPLOY_USER)"
echo "     - EC2_SSH_KEY     (SSH private key for this server)"
echo "     - AUTH_DB_PASSWORD (strong random password)"
echo "     - ROOM_DB_PASSWORD (strong random password)"
echo "     - BOOKING_DB_PASSWORD (strong random password)"
echo "     - RABBITMQ_PASS   (strong random password)"
echo "     - ADMIN_EMAIL     (initial admin email)"
echo "     - ADMIN_PASSWORD  (initial admin password)"
echo "     - JWT_PRIVATE_KEY (run: openssl genrsa 2048)"
echo "     - JWT_PUBLIC_KEY  (extract from private key)"
echo "  3. Push to main branch to trigger CI/CD deployment"
echo ""
