#!/bin/bash

# FastAPI Backend Startup Script
# This script helps you start the services in the correct order

set -e

echo "🚀 FastAPI Backend Startup Script"
echo "=================================="

# Function to check if a service is healthy
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name to be healthy..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is healthy!"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts - $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to become healthy after $max_attempts attempts"
    return 1
}

# Function to show service URLs
show_urls() {
    echo ""
    echo "🌐 Service URLs:"
    echo "================"
    echo "• FastAPI Backend:    http://localhost:8000"
    echo "• API Documentation:  http://localhost:8000/docs"
    echo "• Health Check:       http://localhost:8000/health"
    
    if [ "$1" = "full" ]; then
        echo "• Jaeger UI:          http://localhost:16686"
        echo "• Grafana:            http://localhost:3000 (admin/admin)"
        echo "• Loki:               http://localhost:3100"
        echo "• Tempo:              http://localhost:3200"
        echo "• OTEL Collector:     http://localhost:13133"
    fi
    echo ""
}

# Check command line arguments
case "${1:-full}" in
    "simple")
        echo "🔧 Starting simple setup (API only)..."
        echo ""
        
        # Generate secret key if not set
        if [ -z "$SECRET_KEY" ]; then
            echo "🔑 Generating SECRET_KEY..."
            export SECRET_KEY=$(openssl rand -hex 32)
            echo "   SECRET_KEY=$SECRET_KEY"
            echo ""
        fi
        
        # Start simple setup
        docker-compose -f docker-compose.simple.yml up -d
        
        # Wait for API to be healthy
        check_service "FastAPI API" "http://localhost:8000/health"
        
        show_urls "simple"
        echo "✅ Simple setup is ready!"
        ;;
        
    "full")
        echo "🔧 Starting full setup (API + Observability)..."
        echo ""
        
        # Generate secret key if not set
        if [ -z "$SECRET_KEY" ]; then
            echo "🔑 Generating SECRET_KEY..."
            export SECRET_KEY=$(openssl rand -hex 32)
            echo "   SECRET_KEY=$SECRET_KEY"
            echo ""
        fi
        
        # Start full setup
        docker-compose up -d
        
        # Wait for services to be healthy (in dependency order)
        check_service "Loki" "http://localhost:3100/ready"
        check_service "Tempo" "http://localhost:3200/ready"
        check_service "Jaeger" "http://localhost:16686"
        check_service "OTEL Collector" "http://localhost:13133"
        check_service "Grafana" "http://localhost:3000/api/health"
        check_service "FastAPI API" "http://localhost:8000/health"
        
        show_urls "full"
        echo "✅ Full setup is ready!"
        ;;
        
    "stop")
        echo "🛑 Stopping all services..."
        docker-compose down
        docker-compose -f docker-compose.simple.yml down
        echo "✅ All services stopped!"
        ;;
        
    "logs")
        echo "📋 Showing logs..."
        docker-compose logs -f
        ;;
        
    "status")
        echo "📊 Service Status:"
        echo "=================="
        docker-compose ps
        echo ""
        docker-compose -f docker-compose.simple.yml ps
        ;;
        
    *)
        echo "Usage: $0 [simple|full|stop|logs|status]"
        echo ""
        echo "Commands:"
        echo "  simple  - Start API only (faster startup)"
        echo "  full    - Start API + full observability stack (default)"
        echo "  stop    - Stop all services"
        echo "  logs    - Show service logs"
        echo "  status  - Show service status"
        echo ""
        echo "Environment Variables:"
        echo "  SECRET_KEY - JWT secret key (auto-generated if not set)"
        echo ""
        exit 1
        ;;
esac
