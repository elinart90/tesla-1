#!/usr/bin/env bash
# ============================================================
# VRA FMS – Virtual Environment & Project Setup Script
# Volta River Authority File Management System
# ============================================================
# Usage: bash setup_venv.sh

set -e

echo "========================================================"
echo " VRA File Management System – Setup Script"
echo " Volta River Authority"
echo "========================================================"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required. Please install Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✔ Python $PYTHON_VERSION found"

# Create virtual environment
echo ""
echo "Creating virtual environment: venv/"
python3 -m venv venv
echo "✔ Virtual environment created"

# Activate
source venv/bin/activate
echo "✔ Virtual environment activated"

# Upgrade pip
pip install --upgrade pip --quiet
echo "✔ pip upgraded"

# Install requirements
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo "✔ Dependencies installed"

# Copy .env file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✔ .env file created from .env.example"
    echo ""
    echo "⚠  IMPORTANT: Edit .env with your actual credentials before continuing."
else
    echo "✔ .env file already exists – skipping copy"
fi

# Create media directories
mkdir -p media/uploads
echo "✔ Media directory created"

# Create static directories
mkdir -p static/images staticfiles
echo "✔ Static directories created"

echo ""
echo "========================================================"
echo " NEXT STEPS:"
echo "========================================================"
echo ""
echo " 1. Edit .env with your real credentials"
echo " 2. Set up PostgreSQL:"
echo "    sudo -u postgres psql"
echo "    CREATE DATABASE vra_fms_db;"
echo "    CREATE USER vra_admin WITH PASSWORD 'your_password';"
echo "    GRANT ALL PRIVILEGES ON DATABASE vra_fms_db TO vra_admin;"
echo "    \\q"
echo ""
echo " 3. Run Django setup:"
echo "    source venv/bin/activate"
echo "    python manage.py migrate"
echo "    python manage.py createsuperuser"
echo "    python manage.py collectstatic --noinput"
echo "    python manage.py runserver"
echo ""
echo " 4. Access the system:"
echo "    http://127.0.0.1:8000/"
echo ""
echo "========================================================"
