#!/bin/bash
# Install DGX heartbeat as systemd service. Run on the DGX as root.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p /opt/dgx-heartbeat
cp "$DIR/main.py" /opt/dgx-heartbeat/
cp "$DIR/requirements.txt" /opt/dgx-heartbeat/
pip3 install -q -r /opt/dgx-heartbeat/requirements.txt
cat > /etc/systemd/system/dgx-heartbeat.service << 'EOF'
[Unit]
Description=DGX Heartbeat for ArchiMeades
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/dgx-heartbeat
ExecStart=/usr/bin/python3 main.py
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
