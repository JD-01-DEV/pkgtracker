#!/bin/bash
set -e

echo "⚙️ Installing pkgtracker (cross-distro)..."

# Detect package manager
detect_pkg_manager() {
  if command -v apt >/dev/null 2>&1; then echo apt
  elif command -v dnf >/dev/null 2>&1; then echo dnf
  elif command -v yum >/dev/null 2>&1; then echo yum
  elif command -v pacman >/dev/null 2>&1; then echo pacman
  elif command -v zypper >/dev/null 2>&1; then echo zypper
  elif command -v apk >/dev/null 2>&1; then echo apk
  else echo unknown; fi
}

PKG_MANAGER=$(detect_pkg_manager)
echo "Detected package manager: $PKG_MANAGER"

# Install required tools
case $PKG_MANAGER in
  apt)
    sudo apt update -y
    sudo apt install -y python3 sqlite3 systemd
    ;;
  dnf|yum)
    sudo $PKG_MANAGER install -y python3 sqlite sqlite-devel systemd
    ;;
  pacman)
    sudo pacman -Sy --noconfirm python sqlite systemd
    ;;
  zypper)
    sudo zypper install -y python3 sqlite3 systemd
    ;;
  apk)
    sudo apk add python3 sqlite
    ;;
  *)
    echo "⚠️ Unsupported package manager. Please install Python3 and SQLite manually."
    ;;
esac

# Create installation path
sudo mkdir -p /usr/local/bin
sudo mkdir -p /var/lib/pkgtracker
sudo mkdir -p /etc/pkgtracker

# Copy script (assuming pkgtracker.py in current directory)
sudo cp pkgtracker.py /usr/local/bin/pkgtracker
sudo chmod +x /usr/local/bin/pkgtracker

# Create systemd service and timer
SERVICE_PATH=/etc/systemd/system/pkgtracker.service
TIMER_PATH=/etc/systemd/system/pkgtracker.timer

sudo tee $SERVICE_PATH >/dev/null <<'EOF'
[Unit]
Description=PkgTracker Package Update

[Service]
Type=oneshot
ExecStart=/usr/local/bin/pkgtracker
EOF

sudo tee $TIMER_PATH >/dev/null <<'EOF'
[Unit]
Description=Run pkgtracker every hour

[Timer]
OnBootSec=5min
OnUnitActiveSec=1h
Unit=pkgtracker.service

[Install]
WantedBy=timers.target
EOF

# Enable and start timer
sudo systemctl daemon-reload
sudo systemctl enable --now pkgtracker.timer

# APT hook (only if apt exists)
if command -v apt >/dev/null 2>&1; then
  echo 'DPkg::Post-Invoke {"/usr/local/bin/pkgtracker &";};' | sudo tee /etc/apt/apt.conf.d/99pkgtracker >/dev/null
  echo "✔ APT hook installed"
fi

echo "✅ pkgtracker installed successfully!"
echo "You can now run:"
echo "  pkgtracker --list all"
echo "  pkgtracker --help"
