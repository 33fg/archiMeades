#!/bin/bash
# Run ArchiMeades backend as a daemon. Use: ./scripts/archimedes-daemon.sh start|stop|status
# Run from project root or ~/archimedes on DGX.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

PIDFILE="$ROOT/archimedes.pid"
LOGFILE="$ROOT/archimedes.log"
PORT=8002

start() {
    if [ -f "$PIDFILE" ]; then
        pid=$(cat "$PIDFILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "ArchiMeades already running (PID $pid)"
            return 0
        fi
        rm -f "$PIDFILE"
    fi
    echo "Starting ArchiMeades daemon on port $PORT..."
    (
        cd "$ROOT/backend"
        export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///./gravitational.db}"
        export NEO4J_URI="${NEO4J_URI:-bolt://localhost:7688}"
        export NEO4J_USER="${NEO4J_USER:-neo4j}"
        export NEO4J_PASSWORD="${NEO4J_PASSWORD:-gravitational}"
        export DGX_HOST="${DGX_HOST:-127.0.0.1}"
        exec -a archimeades ../.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
    ) >> "$LOGFILE" 2>&1 &
    echo $! > "$PIDFILE"
    sleep 2
    if kill -0 $(cat "$PIDFILE") 2>/dev/null; then
        echo "ArchiMeades started (PID $(cat "$PIDFILE")), log: $LOGFILE"
        echo "API: http://0.0.0.0:$PORT"
    else
        echo "Failed to start. Check $LOGFILE"
        rm -f "$PIDFILE"
        return 1
    fi
}

stop() {
    if [ ! -f "$PIDFILE" ]; then
        echo "ArchiMeades not running (no PID file)"
        return 0
    fi
    pid=$(cat "$PIDFILE")
    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid"
        echo "Stopped ArchiMeades (PID $pid)"
    else
        echo "ArchiMeades not running (stale PID file)"
    fi
    rm -f "$PIDFILE"
}

status() {
    if [ ! -f "$PIDFILE" ]; then
        echo "ArchiMeades: stopped"
        return 0
    fi
    pid=$(cat "$PIDFILE")
    if kill -0 "$pid" 2>/dev/null; then
        echo "ArchiMeades: running (PID $pid, port $PORT)"
        return 0
    else
        echo "ArchiMeades: stopped (stale PID file)"
        rm -f "$PIDFILE"
        return 1
    fi
}

case "${1:-}" in
    start)  start ;;
    stop)   stop ;;
    status) status ;;
    restart) stop; start ;;
    *) echo "Usage: $0 {start|stop|status|restart}"; exit 1 ;;
esac
