#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Accept project dir as argument or env var, default to cwd
PROJECT_DIR="${1:-${DATAFLOW_PROJECT_DIR:-$(pwd)}}"
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"

# Verify it looks like a dataflow project
if [ ! -f "$PROJECT_DIR/dataflow.yaml" ]; then
    echo "Error: $PROJECT_DIR does not contain a dataflow.yaml"
    echo ""
    echo "Usage: ./scripts/dev.sh <project-dir>"
    echo "   or: DATAFLOW_PROJECT_DIR=/path/to/project npm run dev"
    echo ""
    echo "Create a project first: cd backend && uv run dataflow init my-project"
    echo "Projects are stored in: $ROOT_DIR/projects/"
    exit 1
fi

# Colors for log prefixes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Kill any stale processes on our ports
for port in 8000 5173; do
    pids=$(lsof -ti:"$port" 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}[cleanup]${NC} Killing stale processes on port $port: $pids"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 0.5
    fi
done

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    echo "Shutting down..."
    # Kill specific child PIDs and their process trees
    for pid in $BACKEND_PID $FRONTEND_PID; do
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            pkill -P "$pid" 2>/dev/null || true
            kill "$pid" 2>/dev/null || true
        fi
    done
    # Also kill anything left on our ports
    for port in 8000 5173; do
        pids=$(lsof -ti:"$port" 2>/dev/null || true)
        if [ -n "$pids" ]; then
            echo "$pids" | xargs kill -9 2>/dev/null || true
        fi
    done
    wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo -e "${GREEN}[project]${NC} $PROJECT_DIR"

# Start backend
echo -e "${GREEN}[backend]${NC} Starting uvicorn on :8000..."
(
    cd "$ROOT_DIR/backend"
    DATAFLOW_PROJECT_DIR="$PROJECT_DIR" uv run uvicorn dataflow.server.app:create_app --factory --host 0.0.0.0 --port 8000 --reload 2>&1 | sed "s/^/$(printf "${GREEN}[backend]${NC} ")/"
) &
BACKEND_PID=$!

# Start frontend
echo -e "${BLUE}[frontend]${NC} Starting Vite on :5173..."
(
    cd "$ROOT_DIR/frontend"
    npm run dev 2>&1 | sed "s/^/$(printf "${BLUE}[frontend]${NC} ")/"
) &
FRONTEND_PID=$!

wait
