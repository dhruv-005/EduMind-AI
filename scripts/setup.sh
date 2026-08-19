#!/bin/bash

set -e

echo "=========================================="
echo "   EduMind AI Platform Setup"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check Python
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 not found. Please install Python 3.11+"
    exit 1
fi
log_info "Python found: $(python3 --version)"

# Check Node
if ! command -v node &> /dev/null; then
    log_error "Node.js not found. Please install Node.js 18+"
    exit 1
fi
log_info "Node found: $(node --version)"

# Setup backend
log_info "Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_info "Virtual environment created"
fi

source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
log_info "Backend dependencies installed"

# Download spaCy model
python -m spacy download en_core_web_sm --quiet 2>/dev/null || \
    log_warn "spaCy model download failed (optional)"

# Copy env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || true
    log_warn "Created .env from example - please add your API keys!"
fi

# Create directories
mkdir -p uploads logs chroma_db
log_info "Backend directories created"

cd ..

# Setup frontend
log_info "Setting up frontend..."
cd frontend
npm install --silent
log_info "Frontend dependencies installed"

# Copy env
if [ ! -f ".env" ]; then
    echo "VITE_API_BASE_URL=http://localhost:8000" > .env
    echo "VITE_WS_BASE_URL=ws://localhost:8000" >> .env
    echo "VITE_APP_NAME=EduMind AI" >> .env
    log_info "Frontend .env created"
fi

cd ..

echo ""
echo "=========================================="
echo "   Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Add your API keys to backend/.env:"
echo "   - GROQ_API_KEY (get free at console.groq.com)"
echo "   - GEMINI_API_KEY (get free at aistudio.google.com)"
echo ""
echo "2. Run backend:"
echo "   cd backend && source venv/bin/activate"
echo "   uvicorn main:app --reload --port 8000"
echo ""
echo "3. Run frontend (new terminal):"
echo "   cd frontend && npm run dev"
echo ""
echo "4. Open: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
