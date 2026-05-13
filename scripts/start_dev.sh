#!/usr/bin/env bash
# Start both backend and frontend in development mode
# Usage: ./scripts/start_dev.sh

ROOT=$(cd "$(dirname "$0")/.." && pwd)

echo "🚀 Starting TruthLens development servers…"

# Backend
cd "$ROOT/backend"
source venv/bin/activate 2>/dev/null || true
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Frontend
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "Services running:"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait and handle Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'; exit 0" INT
wait
