#!/bin/bash

# Demo Market Resolution Script
# Usage: ./demo-market.sh <market_id> <outcome>
# Example: ./demo-market.sh "Will Bitcoin reach $100k by 2026?-jackcoleman" YES
# Example: ./demo-market.sh "cc8a0733-39c4-4522-b457-a5c354fdaa45" NO

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RAILWAY_URL="https://prove-me-wrong-uagents-production.up.railway.app"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if we have the required arguments
if [ $# -ne 2 ]; then
    print_error "Usage: $0 <market_id> <outcome>"
    print_error "Example: $0 'Will Bitcoin reach $100k by 2026?-jackcoleman' YES"
    print_error "Example: $0 'cc8a0733-39c4-4522-b457-a5c354fdaa45' NO"
    print_error "Outcome must be YES or NO"
    exit 1
fi

MARKET_ID="$1"
OUTCOME="$2"

# Validate outcome
if [ "$OUTCOME" != "YES" ] && [ "$OUTCOME" != "NO" ]; then
    print_error "Outcome must be YES or NO, got: $OUTCOME"
    exit 1
fi

print_status "Setting market outcome..."
print_status "Market ID: $MARKET_ID"
print_status "Outcome: $OUTCOME"
print_status "Railway URL: $RAILWAY_URL"

# First, let's check if the market exists
print_status "Checking if market exists..."

MARKET_INFO=$(curl -s "$RAILWAY_URL/generator/markets/$MARKET_ID" 2>/dev/null || echo "{}")

if echo "$MARKET_INFO" | grep -q "Not Found"; then
    print_error "Market not found: $MARKET_ID"
    print_status "Available markets:"
    curl -s "$RAILWAY_URL/generator/markets" | jq -r '.markets[] | "  - \(.id): \(.title)"' 2>/dev/null || print_warning "Could not fetch market list"
    exit 1
fi

print_success "Market found!"

# Extract market title for display
MARKET_TITLE=$(echo "$MARKET_INFO" | jq -r '.title // "Unknown"' 2>/dev/null || echo "Unknown")
print_status "Market: $MARKET_TITLE"

# Set the outcome using the generator's update endpoint
print_status "Setting outcome to: $OUTCOME"

RESPONSE=$(curl -s -X PUT "$RAILWAY_URL/generator/markets/$MARKET_ID/outcome" \
    -H "Content-Type: application/json" \
    -d "{
        \"outcome\": \"$OUTCOME\",
        \"resolved_at\": \"$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)\",
        \"resolution_confidence\": 1.0
    }")

if echo "$RESPONSE" | grep -q "success.*true"; then
    print_success "Market outcome set successfully!"
    
    # Show the updated market info
    print_status "Updated market information:"
    UPDATED_MARKET=$(curl -s "$RAILWAY_URL/generator/markets/$MARKET_ID")
    echo "$UPDATED_MARKET" | jq '.' 2>/dev/null || echo "$UPDATED_MARKET"
    
    # Also check if there's a resolution record
    print_status "Checking resolution record..."
    RESOLUTION=$(curl -s "$RAILWAY_URL/resolver/resolutions/$MARKET_ID" 2>/dev/null || echo "{}")
    if echo "$RESOLUTION" | grep -q "Not Found"; then
        print_warning "No resolution record found (this is normal for demo markets)"
    else
        print_success "Resolution record found:"
        echo "$RESOLUTION" | jq '.' 2>/dev/null || echo "$RESOLUTION"
    fi
    
else
    print_error "Failed to set market outcome"
    print_error "Response: $RESPONSE"
    exit 1
fi

print_success "Demo market resolution complete!"
print_status "Market ID: $MARKET_ID"
print_status "Outcome: $OUTCOME"
print_status "You can now test the resolution endpoints with this market." 