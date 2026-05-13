#!/usr/bin/env bash
# ============================================================
# TruthLens — Mac Setup Script
# Run: chmod +x scripts/setup_mac.sh && ./scripts/setup_mac.sh
# ============================================================

set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd)
echo "🔍 TruthLens Setup — Root: $ROOT"

# ── Backend ───────────────────────────────────────────────────
echo ""
echo "=== Setting up Backend ==="
cd "$ROOT/backend"

if ! command -v python3 &>/dev/null; then
  echo "ERROR: Python 3 not found. Install from https://python.org"
  exit 1
fi

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"

mkdir -p trained_models

# Create .env if not exists
if [ ! -f "$ROOT/.env" ]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "⚠️  Created .env from template — update MONGODB_URI and SECRET_KEY"
fi

echo "✅ Backend setup complete"

# ── Frontend ──────────────────────────────────────────────────
echo ""
echo "=== Setting up Frontend ==="
cd "$ROOT/frontend"

if ! command -v node &>/dev/null; then
  echo "ERROR: Node.js not found. Install from https://nodejs.org"
  exit 1
fi

npm install
echo "✅ Frontend setup complete"

# ── Done ──────────────────────────────────────────────────────
echo ""
echo "============================================"
echo "✅ Setup complete!"
echo ""
echo "To start the backend:"
echo "  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "To start the frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "API docs: http://localhost:8000/docs"
echo "Frontend: http://localhost:5173"
echo "============================================"
