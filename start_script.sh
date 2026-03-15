#!/bin/bash

echo "🚀 Starting VRA File Management System..."

# 1. Bring down any ghost containers and start fresh
docker compose down

# 2. Start the containers in the background (detached mode)
docker compose up -d

echo "⏳ Waiting for Database to be ready..."
# 3. Wait for the web container to finish its internal wait-for-db script
sleep 5

# 4. Run migrations just in case models changed
echo "📦 Checking for database updates..."
docker exec vra_django python manage.py migrate --noinput

echo "✅ System is UP!"
echo "🔗 Access the App: http://localhost:8000"
echo "🔗 Access Admin: http://localhost:8000/admin"
echo "-------------------------------------------"
echo "📝 Showing recent logs (Ctrl+C to exit logs, app will keep running):"
echo "Press Ctrl + C "
docker compose logs -f web