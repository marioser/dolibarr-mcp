#!/bin/bash
# =============================================================================
# Dolibarr MCP Server - Docker Image Publisher
# =============================================================================
# Builds and pushes the Docker image to Docker Hub
#
# Usage:
#   ./scripts/docker-publish.sh [username] [version]
#
# Examples:
#   ./scripts/docker-publish.sh miometrix 2.1.0
#   ./scripts/docker-publish.sh myuser latest
# =============================================================================

set -e

# Configuration
DOCKERHUB_USERNAME="${1:-miometrix}"
VERSION="${2:-2.1.0}"
IMAGE_NAME="dolibarr-mcp"
FULL_IMAGE="${DOCKERHUB_USERNAME}/${IMAGE_NAME}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Dolibarr MCP Docker Publisher${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Image: ${FULL_IMAGE}:${VERSION}"
echo ""

# Check if logged in to Docker Hub
if ! docker info 2>/dev/null | grep -q "Username"; then
    echo -e "${YELLOW}Not logged in to Docker Hub. Please login:${NC}"
    docker login
fi

# Navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo -e "${GREEN}Building image...${NC}"
docker build -f docker/Dockerfile -t "${FULL_IMAGE}:${VERSION}" .

# Tag as latest if not already latest
if [ "$VERSION" != "latest" ]; then
    echo -e "${GREEN}Tagging as latest...${NC}"
    docker tag "${FULL_IMAGE}:${VERSION}" "${FULL_IMAGE}:latest"
fi

echo -e "${GREEN}Pushing to Docker Hub...${NC}"
docker push "${FULL_IMAGE}:${VERSION}"

if [ "$VERSION" != "latest" ]; then
    docker push "${FULL_IMAGE}:latest"
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Successfully published!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Images pushed:"
echo "  - ${FULL_IMAGE}:${VERSION}"
if [ "$VERSION" != "latest" ]; then
    echo "  - ${FULL_IMAGE}:latest"
fi
echo ""
echo "To deploy on CapRover:"
echo "  1. Go to App → Deployment → Deploy via ImageName"
echo "  2. Enter: ${FULL_IMAGE}:${VERSION}"
echo ""
echo "To use in docker-compose:"
echo "  image: ${FULL_IMAGE}:${VERSION}"
