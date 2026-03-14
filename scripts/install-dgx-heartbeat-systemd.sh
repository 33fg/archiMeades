#!/bin/bash
# Install DGX heartbeat as systemd service (survives reboot). Run on DGX as root.
# Uses standalone script - no pip required.
# Deploy from your machine: ./scripts/deploy-dgx-heartbeat.sh --no-pip --install-systemd
set -e
HEARTBEAT_SRC="${1:-/tmp/run-dgx-heartbeat-standalone.py}"
mkdir -p /opt/dgx-heartbeat
cp "$HEARTBEAT_SRC" /opt/dgx-heartbeat/heartbeat.py
chmod +x /opt/dgx-heartbeat/heartbeat.py
cat > /etc/systemd/system/dgx-heartbeat.service << 'EOF'
[Unit]
Description=DGX Heartbeat for ArchiMeades
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/dgx-heartbeat/heartbeat.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable dgx-heartbeat
systemctl restart dgx-heartbeat
echo "Installed. Status:"
systemctl status dgx-heartbeat --no-pager
