#!/bin/bash

# Market Generator Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="market-generator"
CONTAINER_NAME="market-generator-container"
PORT="8000"

echo -e "${GREEN}=== Market Generator Deployment Script ===${NC}\n"

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

# Stop and remove existing container if it exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}Stopping existing container...${NC}"
    docker stop $CONTAINER_NAME > /dev/null 2>&1 || true
    docker rm $CONTAINER_NAME > /dev/null 2>&1 || true
    echo -e "${GREEN}✓ Existing container removed${NC}"
fi

# Build the Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t $IMAGE_NAME .
echo -e "${GREEN}✓ Docker image built successfully${NC}"

# Run the container
echo -e "${YELLOW}Starting container...${NC}"
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:8000 \
    -e ASI_API_KEY="$ASI_API_KEY" \
    -e PYTHONUNBUFFERED=1 \
    $IMAGE_NAME

echo -e "${GREEN}✓ Container started successfully${NC}"

# Wait for the service to be ready
echo -e "${YELLOW}Waiting for service to be ready...${NC}"
sleep 5

# Test the health endpoint
echo -e "${YELLOW}Testing health endpoint...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Service is healthy and ready${NC}"
        break
    else
        if [ $i -eq 10 ]; then
            echo -e "${RED}Error: Service failed to start within expected time${NC}"
            echo "Container logs:"
            docker logs $CONTAINER_NAME
            exit 1
        fi
        echo -e "${YELLOW}Waiting for service... (attempt $i/10)${NC}"
        sleep 2
    fi
done

# Display service information
echo -e "\n${GREEN}=== Service Information ===${NC}"
echo "Container Name: $CONTAINER_NAME"
echo "Service URL: http://localhost:$PORT"
echo "Health Check: http://localhost:$PORT/health"
echo "API Docs: http://localhost:$PORT/docs"

# Display useful commands
echo -e "\n${GREEN}=== Useful Commands ===${NC}"
echo "View logs: docker logs -f $CONTAINER_NAME"
echo "Stop service: docker stop $CONTAINER_NAME"
echo "Restart service: docker restart $CONTAINER_NAME"
echo "Remove service: docker rm -f $CONTAINER_NAME"

# Test the API
echo -e "\n${YELLOW}Running quick API test...${NC}"
python3 test_generator.py

echo -e "\n${GREEN}=== Deployment Complete! ===${NC}"
echo "The Market Generator Agent is now running and ready to use." 