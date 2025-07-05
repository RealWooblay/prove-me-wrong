#!/bin/bash

# Deploy Prove Me Wrong μAgent System to Railway
# This script deploys the μAgent system with proper inter-agent communication

set -e

echo "🚀 Deploying Prove Me Wrong μAgent System to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   npm install -g @railway/cli"
    exit 1
fi

# Check if we're logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged in to Railway. Please run:"
    echo "   railway login"
    exit 1
fi

# Create .env file for local testing if it doesn't exist
if [ ! -f "agents/.env" ]; then
    echo "📝 Creating .env file for local testing..."
    cat > agents/.env << EOF
# ASI-1 Mini API Configuration
ASI_API_KEY=sk_a1d55fd6b1ba47ddadc98bd1e8048e56ff00c4736c844a9db4aab791d33f0989

# Railway URL Configuration
RAILWAY_URL=https://prove-me-wrong-uagents-production.up.railway.app

# Blockchain Configuration (update with your actual values)
RPC_URL=https://rpc.ankr.com/polygon
CHAIN_ID=137
PMW_ADDRESS=0x...
PMW_POOL_ADDRESS=0x...
ADMIN_PRIVATE_KEY=0x...

# μAgent Configuration
GENERATOR_AGENT_PORT=8000
RESOLVER_AGENT_PORT=8001
COORDINATOR_AGENT_PORT=8002
GENERATOR_SERVER_PORT=8003
RESOLVER_SERVER_PORT=8004
PROXY_SERVER_PORT=8005
EOF
    echo "✅ Created agents/.env file"
fi

# Initialize Railway project if not already done
if [ ! -f ".railway" ]; then
    echo "🔧 Initializing Railway project..."
    railway init --name "prove-me-wrong-uagents"
fi

# Link the service
echo "🔗 Linking Railway service..."
railway service

# Set environment variables for Railway
echo "🔧 Setting Railway environment variables..."

# Set all environment variables at once
railway variables \
    --set "ASI_API_KEY=sk_a1d55fd6b1ba47ddadc98bd1e8048e56ff00c4736c844a9db4aab791d33f0989" \
    --set "RAILWAY_URL=https://prove-me-wrong-uagents-production.up.railway.app" \
    --set "DATABASE_URL=sqlite:///./markets.db" \
    --set "RPC_URL=https://rpc.ankr.com/polygon" \
    --set "CHAIN_ID=137" \
    --set "PMW_ADDRESS=0x..." \
    --set "PMW_POOL_ADDRESS=0x..." \
    --set "ADMIN_PRIVATE_KEY=0x..." \
    --set "GENERATOR_AGENT_PORT=8000" \
    --set "RESOLVER_AGENT_PORT=8001" \
    --set "COORDINATOR_AGENT_PORT=8002" \
    --set "GENERATOR_SERVER_PORT=8003" \
    --set "RESOLVER_SERVER_PORT=8004" \
    --set "PROXY_SERVER_PORT=8005"

echo "✅ Environment variables set"

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment completed!"
echo ""
echo "📊 μAgent System Status:"
echo "   - Market Generator Agent: http://localhost:8000"
echo "   - Market Resolver Agent: http://localhost:8001"
echo "   - Market Coordinator Agent: http://localhost:8002"
echo "   - Generator Server: http://localhost:8003"
echo "   - Resolver Server: http://localhost:8004"
echo "   - Proxy Server: http://localhost:8005"
echo ""
echo "🔍 Health Check Endpoints:"
echo "   - GET http://localhost:8000/health (Generator Agent)"
echo "   - GET http://localhost:8001/health (Resolver Agent)"
echo "   - GET http://localhost:8002/health (Coordinator Agent)"
echo "   - GET http://localhost:8003/health (Generator Server)"
echo "   - GET http://localhost:8004/health (Resolver Server)"
echo "   - GET http://localhost:8005/health (Proxy Server)"
echo ""
echo "📝 API Endpoints:"
echo "   - POST http://localhost:8000/analyze-market (Generator Agent)"
echo "   - POST http://localhost:8001/resolve-market (Resolver Agent)"
echo "   - POST http://localhost:8002/create-market (Coordinator Agent)"
echo ""
echo "🧪 Test μAgent Communication:"
echo "   python agents/test_uagents_communication.py"
echo ""
echo "📋 View logs:"
echo "   railway logs"
echo ""
echo "🎯 The μAgent system is now running with inter-agent communication!" 