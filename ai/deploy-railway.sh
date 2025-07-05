#!/bin/bash

# Deploy to Railway
# This script helps deploy the AI services to Railway

set -e

echo "🚀 Deploying Prove Me Wrong AI Services to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   npm install -g @railway/cli"
    echo "   Then run: railway login"
    exit 1
fi

# Check if we're logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged in to Railway. Please run: railway login"
    exit 1
fi

# Check if ASI_API_KEY is set
if [ -z "$ASI_API_KEY" ]; then
    echo "⚠️  ASI_API_KEY environment variable not set."
    echo "   Please set it with: export ASI_API_KEY=your_api_key_here"
    echo "   Or add it to Railway after deployment."
fi

echo "📊 Setting up PostgreSQL database..."
echo "   Railway will automatically provision a PostgreSQL database"
echo "   The DATABASE_URL will be automatically set as an environment variable"

echo "📦 Building and deploying to Railway..."

# Deploy to Railway
railway up

echo "✅ Deployment complete!"
echo ""
echo "🔗 Your services will be available at:"
echo "   - Main API: https://your-project-name.railway.app"
echo "   - Generator: https://your-project-name.railway.app/generator/*"
echo "   - Resolver: https://your-project-name.railway.app/resolver/*"
echo ""
echo "📋 Available endpoints:"
echo "   - POST /generator/generate - Generate a new market"
echo "   - GET /generator/markets - List all markets"
echo "   - POST /resolver/resolve - Resolve a market"
echo "   - GET /resolver/resolutions/{market_id}/outcome - Get market outcome"
echo "   - GET /health - Health check"
echo ""
echo "🔧 To set environment variables in Railway:"
echo "   railway variables set ASI_API_KEY=your_api_key_here"
echo "   Note: DATABASE_URL is automatically set by Railway PostgreSQL service"
echo ""
echo "📊 To view logs:"
echo "   railway logs" 