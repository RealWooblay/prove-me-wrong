#!/bin/bash

# AI Prediction Market System Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GENERATOR_PORT="8000"
RESOLVER_PORT="8001"

echo -e "${GREEN}=== AI Prediction Market System Deployment ===${NC}\n"

# Check if ASI_API_KEY is set
if [ -z "$ASI_API_KEY" ]; then
    echo -e "${RED}Error: ASI_API_KEY environment variable is not set${NC}"
    echo "Please set it with: export ASI_API_KEY='your_api_key_here'"
    exit 1
fi

echo -e "${GREEN}✓ ASI_API_KEY is configured${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker Compose is available${NC}"

# Stop existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose down --remove-orphans 2>/dev/null || true
echo -e "${GREEN}✓ Existing containers stopped${NC}"

# Create necessary directories
echo -e "${YELLOW}Creating storage directories...${NC}"
mkdir -p generator/markets
mkdir -p resolver/resolutions
echo -e "${GREEN}✓ Storage directories created${NC}"

# Build and start services
echo -e "${YELLOW}Building and starting services...${NC}"
docker-compose up --build -d

echo -e "${GREEN}✓ Services started successfully${NC}"

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Test generator health
echo -e "${YELLOW}Testing generator health...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:$GENERATOR_PORT/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Generator is healthy${NC}"
        break
    else
        if [ $i -eq 10 ]; then
            echo -e "${RED}Error: Generator failed to start within expected time${NC}"
            echo "Generator logs:"
            docker-compose logs generator
            exit 1
        fi
        echo -e "${YELLOW}Waiting for generator... (attempt $i/10)${NC}"
        sleep 3
    fi
done

# Test resolver health
echo -e "${YELLOW}Testing resolver health...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:$RESOLVER_PORT/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Resolver is healthy${NC}"
        break
    else
        if [ $i -eq 10 ]; then
            echo -e "${RED}Error: Resolver failed to start within expected time${NC}"
            echo "Resolver logs:"
            docker-compose logs resolver
            exit 1
        fi
        echo -e "${YELLOW}Waiting for resolver... (attempt $i/10)${NC}"
        sleep 3
    fi
done

# Display service information
echo -e "\n${GREEN}=== Service Information ===${NC}"
echo -e "${BLUE}Generator Agent:${NC}"
echo "  URL: http://localhost:$GENERATOR_PORT"
echo "  Health: http://localhost:$GENERATOR_PORT/health"
echo "  API Docs: http://localhost:$GENERATOR_PORT/docs"

echo -e "\n${BLUE}Resolver Agent:${NC}"
echo "  URL: http://localhost:$RESOLVER_PORT"
echo "  Health: http://localhost:$RESOLVER_PORT/health"
echo "  API Docs: http://localhost:$RESOLVER_PORT/docs"

# Display useful commands
echo -e "\n${GREEN}=== Useful Commands ===${NC}"
echo "View all logs: docker-compose logs -f"
echo "View generator logs: docker-compose logs -f generator"
echo "View resolver logs: docker-compose logs -f resolver"
echo "Stop services: docker-compose down"
echo "Restart services: docker-compose restart"
echo "Rebuild services: docker-compose up --build -d"

# Test the system
echo -e "\n${YELLOW}Running system tests...${NC}"

# Test generator
echo -e "${BLUE}Testing generator...${NC}"
cd generator
python3 test_generator.py
cd ..

# Test resolver
echo -e "${BLUE}Testing resolver...${NC}"
cd resolver
python3 test_resolver.py
cd ..

echo -e "\n${GREEN}=== Deployment Complete! ===${NC}"
echo -e "The AI Prediction Market System is now running and ready to use."
echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Create markets using the generator: POST /generate"
echo "2. The resolver will automatically check markets every hour"
echo "3. Check resolutions: GET /resolutions"
echo "4. Monitor logs for system activity"

# Display example usage
echo -e "\n${GREEN}=== Example Usage ===${NC}"
echo -e "${BLUE}Create a market:${NC}"
echo 'curl -X POST http://localhost:8000/generate \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '"'"'{"prompt": "Tesla stock price will be above $250 on December 31, 2024"}'"'"

echo -e "\n${BLUE}Resolve all markets:${NC}"
echo 'curl -X POST http://localhost:8001/resolve-all'

echo -e "\n${BLUE}List all resolutions:${NC}"
echo 'curl http://localhost:8001/resolutions' 