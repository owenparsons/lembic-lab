#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for log prefixes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

cleanup() {
    echo ""
    echo "Shutting down..."
    kill 0 2>/dev/null
    wait 2>/dev/null
}
trap cleanup EXIT INT TERM

# Start backend
echo -e "${GREEN}[backend]${NC} Starting uvicorn on :8000..."
(
    cd "$ROOT_DIR/backend"
    uv run uvicorn dataflow.server.app:create_app --factory --host 0.0.0.0 --port 8000 --reload 2>&1 | sed "s/^/$(printf "${GREEN}[backend]${NC} ")/"
) &

# Start frontend
echo -e "${BLUE}[frontend]${NC} Starting Vite on :5173..."
(
    cd "$ROOT_DIR/frontend"
    npm run dev 2>&1 | sed "s/^/$(printf "${BLUE}[frontend]${NC} ")/"
) &

wait
