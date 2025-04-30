#!/bin/bash

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
mkdir -p ./logs

# Build and start all services
echo "Starting all services..."
docker-compose up -d

# Check if services are running
echo "Checking services status..."
sleep 10
docker-compose ps

echo "Chat API is now running!"
echo "Access the API at http://localhost:80/docs"
echo "Access Grafana at http://localhost:3000 (admin/admin)"
echo "Access Prometheus at http://localhost:9090"
