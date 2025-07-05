#!/bin/bash

# Blockchain deployment script for ProveMeWrong market generator
# This script helps set up the environment variables needed for blockchain integration

echo "🚀 ProveMeWrong Blockchain Deployment Setup"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    touch .env
fi

# Function to prompt for input with default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    echo -n "$prompt [$default]: "
    read input
    
    if [ -z "$input" ]; then
        input="$default"
    fi
    
    # Update .env file
    if grep -q "^$var_name=" .env; then
        # Update existing line
        sed -i "s/^$var_name=.*/$var_name=$input/" .env
    else
        # Add new line
        echo "$var_name=$input" >> .env
    fi
}

echo ""
echo "📋 Please provide the following configuration:"
echo ""

# RPC URL
prompt_with_default "Enter your Ethereum RPC URL" "https://sepolia.infura.io/v3/YOUR-PROJECT-ID" "RPC_URL"

# Contract Address
prompt_with_default "Enter the deployed ProveMeWrong contract address" "0x0000000000000000000000000000000000000000" "PMW_ADDRESS"

# Admin Private Key
echo ""
echo "⚠️  IMPORTANT: Your admin private key will be used to deploy markets to the blockchain."
echo "   Make sure this wallet has sufficient funds for gas fees."
echo ""
prompt_with_default "Enter admin wallet private key (without 0x prefix)" "" "ADMIN_PRIVATE_KEY"

# Chain ID
prompt_with_default "Enter chain ID" "11155111" "CHAIN_ID"

echo ""
echo "✅ Configuration saved to .env file"
echo ""
echo "📝 Next steps:"
echo "1. Deploy the ProveMeWrong contract to your chosen network"
echo "2. Update CONTRACT_ADDRESS in .env with the deployed contract address"
echo "3. Ensure your admin wallet has sufficient funds for gas fees"
echo "4. Start the server with: python server.py"
echo ""
echo "🔧 To load environment variables, run:"
echo "   source .env && python server.py"
echo ""
echo "🌐 Health check endpoint will show blockchain status:"
echo "   curl http://localhost:8000/health" 