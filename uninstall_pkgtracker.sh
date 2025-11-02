#!/bin/bash
set -e
echo "🧹 Uninstalling pkgtracker..."

sudo systemctl disable --now pkgtracker.timer pkgtracker.service >/dev/null 2>&1 || true
sudo rm -f /etc/systemd/system/pkgtracker.{service,timer}
sudo systemctl daemon-reload

sudo rm -f /usr/local/bin/pkgtracker
sudo rm -rf /var/lib/pkgtracker
sudo rm -rf /etc/pkgtracker
sudo rm -f /etc/apt/apt.conf.d/99pkgtracker 2>/dev/null || true

echo "✅ pkgtracker fully uninstalled."
