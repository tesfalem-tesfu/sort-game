#!/bin/bash

# Sorting Quiz Game Deployment Script
# Usage: ./deploy.sh [local|docker|production]

set -e

DEPLOYMENT_TYPE=${1:-local}
PROJECT_NAME="sorting-quiz"

echo "🚀 Starting $DEPLOYMENT_TYPE deployment..."

case $DEPLOYMENT_TYPE in
    "local")
        echo "📦 Setting up local development environment..."
        
        # Backend setup
        echo "🔧 Setting up backend..."
        cd backend
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -r requirements.txt
        
        # Database setup
        echo "🗄️ Setting up database..."
        python -c "from app import app, db; with app.app_context(): db.create_all()"
        
        # Frontend setup
        echo "🎨 Setting up frontend..."
        cd ../frontend
        npm install
        
        echo "✅ Local setup complete!"
        echo "📋 To run:"
        echo "   Backend: cd backend && source venv/bin/activate && python app.py"
        echo "   Frontend: cd frontend && npm run dev"
        ;;
        
    "docker")
        echo "🐳 Docker deployment..."
        
        # Build and start containers
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        
        echo "✅ Docker deployment complete!"
        echo "🌐 Available at:"
        echo "   Frontend: http://localhost:3000"
        echo "   Backend:  http://localhost:5000"
        echo "   Database: localhost:3306"
        ;;
        
    "production")
        echo "🌟 Production deployment..."
        
        # Check if required tools are installed
        command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed."; exit 1; }
        command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed."; exit 1; }
        
        # Production environment checks
        if [ ! -f ".env" ]; then
            echo "❌ .env file not found. Please create it with production values."
            exit 1
        fi
        
        echo "🔒 Checking production configuration..."
        
        # Deploy with production configurations
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
        
        echo "✅ Production deployment complete!"
        echo "🔍 Check logs with: docker-compose logs -f"
        ;;
        
    *)
        echo "❌ Invalid deployment type: $DEPLOYMENT_TYPE"
        echo "📋 Usage: $0 [local|docker|production]"
        exit 1
        ;;
esac

echo "🎉 Deployment completed successfully!"
