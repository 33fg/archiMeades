#!/bin/bash
# Deploy and run DGX heartbeat on 10.88.111.9. Requires SSH access.
# Usage: ./scripts/deploy-dgx-heartbeat.sh [--no-pip] [--install-systemd]
#   --no-pip: use stdlib-only (no pip/uvicorn needed)
#   --install-systemd: install as systemd service (survives reboot; requires sudo)
# Env: DGX_HOST, DGX_SSH_USER, DGX_SSH_KEY, DGX_SSH_PASSWORD (for sshpass)
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DGX_HOST="${DGX_HOST:-10.88.111.9}"
DGX_SSH_USER="${DGX_SSH_USER:-}"
DGX_SSH_KEY="${DGX_SSH_KEY:-}"
DGX_SSH_PASSWORD="${DGX_SSH_PASSWORD:-}"
NO_PIP=false
INSTALL_SYSTEMD=false
for arg in "$@"; do
  [[ "$arg" == "--no-pip" ]] && NO_PIP=true
  [[ "$arg" == "--install-systemd" ]] && INSTALL_SYSTEMD=true
done
[[ "$INSTALL_SYSTEMD" == true ]] && NO_PIP=true  # systemd install uses standalone script

# Build SSH target: user@host or just host
if [[ -n "$DGX_SSH_USER" ]]; then
  DGX="$DGX_SSH_USER@$DGX_HOST"
else
  DGX="$DGX_HOST"
fi

SSH_OPTS="-o StrictHostKeyChecking=no"
[[ -n "$DGX_SSH_KEY" ]] && SSH_OPTS="$SSH_OPTS -i $DGX_SSH_KEY"

# Use sshpass when password provided
SCP_CMD="scp"
SSH_CMD="ssh"
if [[ -n "$DGX_SSH_PASSWORD" ]]; then
  export SSHPASS="$DGX_SSH_PASSWORD"
  SCP_CMD="sshpass -e scp"
  SSH_CMD="sshpass -e ssh"
fi

echo "Deploying heartbeat to $DGX..."

if $NO_PIP; then
  # Stdlib-only: no pip. Uses run-dgx-heartbeat-standalone.py
  $SCP_CMD $SSH_OPTS "$ROOT/scripts/run-dgx-heartbeat-standalone.py" "$DGX:/tmp/"
  $SSH_CMD $SSH_OPTS "$DGX" "pkill -f run-dgx-heartbeat-standalone 2>/dev/null; pkill -f 'python3 main.py' 2>/dev/null; sleep 1; nohup python3 /tmp/run-dgx-heartbeat-standalone.py > /tmp/dgx-heartbeat.log 2>&1 & sleep 2; curl -s http://localhost:8000/health || cat /tmp/dgx-heartbeat.log"
else
  $SCP_CMD $SSH_OPTS -r "$ROOT/dgx_orchestrator/" "$DGX:/tmp/dgx_orchestrator/"
  $SSH_CMD $SSH_OPTS "$DGX" "cd /tmp/dgx_orchestrator && pip3 install -q -r requirements.txt && pkill -f 'python3 main.py' 2>/dev/null; nohup python3 main.py > /tmp/dgx-heartbeat.log 2>&1 & sleep 2; curl -s http://localhost:8000/health || cat /tmp/dgx-heartbeat.log"
fi

if $INSTALL_SYSTEMD; then
  echo "Installing systemd service (survives reboot)..."
  $SCP_CMD $SSH_OPTS "$ROOT/scripts/install-dgx-heartbeat-systemd.sh" "$DGX:/tmp/"
  if [[ -n "$DGX_SSH_PASSWORD" ]]; then
    $SSH_CMD $SSH_OPTS "$DGX" "echo '$DGX_SSH_PASSWORD' | sudo -S bash /tmp/install-dgx-heartbeat-systemd.sh /tmp/run-dgx-heartbeat-standalone.py"
  else
    $SSH_CMD $SSH_OPTS "$DGX" "sudo bash /tmp/install-dgx-heartbeat-systemd.sh /tmp/run-dgx-heartbeat-standalone.py" || {
      echo "Note: systemd install requires sudo. Set DGX_SSH_PASSWORD or run manually: sudo bash /tmp/install-dgx-heartbeat-systemd.sh /tmp/run-dgx-heartbeat-standalone.py"
    }
  fi
fi

echo ""
echo "Heartbeat should be at $DGX:8000. Check Settings -> DGX Cluster."
