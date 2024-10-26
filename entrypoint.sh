#!/bin/bash

# Wait for the database to be ready
echo "Waiting for database..."

# Use ping to check if the database service is up
while ! ping -c 1 db; do
  sleep 1
done

# Check if PostgreSQL is ready to accept connections
while ! pg_isready -h db -U eklavya -d expenses_db; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

echo "Database is ready!"

if [ ! -d "migrations" ]; then
    flask db init
    echo "Migrations directory created."
fi

# Create initial migration
flask db migrate -m "Initial migration" || true
flask db upgrade || true

# Start the Flask application
python run.py
