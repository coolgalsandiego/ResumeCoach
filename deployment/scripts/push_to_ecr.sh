#!/bin/bash

# Push Docker images to AWS ECR
# This script builds and pushes both backend and frontend images to ECR

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-}"
ECR_REPOSITORY="${ECR_REPOSITORY:-resume-coach}"
BACKEND_IMAGE="${ECR_REPOSITORY}-backend"
FRONTEND_IMAGE="${ECR_REPOSITORY}-frontend"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🐳 Pushing Docker images to ECR${NC}"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found${NC}"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found${NC}"
    exit 1
fi

# Get AWS account ID if not provided
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "📋 Getting AWS account ID..."
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo -e "${GREEN}✅ Account ID: $AWS_ACCOUNT_ID${NC}"
fi

# ECR base URL
ECR_BASE="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Login to ECR
echo "🔐 Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_BASE

# Create repositories if they don't exist
echo "📦 Creating ECR repositories..."
for repo in $BACKEND_IMAGE $FRONTEND_IMAGE; do
    if aws ecr describe-repositories --repository-names $repo --region $AWS_REGION &>/dev/null; then
        echo -e "${GREEN}✅ Repository exists: $repo${NC}"
    else
        echo "Creating repository: $repo"
        aws ecr create-repository \
            --repository-name $repo \
            --region $AWS_REGION \
            --image-scanning-configuration scanOnPush=true \
            --encryption-configuration encryptionType=AES256 > /dev/null
        echo -e "${GREEN}✅ Repository created: $repo${NC}"
    fi
done

# Build and push backend
echo ""
echo -e "${YELLOW}🔨 Building backend image...${NC}"
cd "$(dirname "$0")/../.."
docker build -t $BACKEND_IMAGE:latest -f deployment/docker/Dockerfile.backend .

echo -e "${YELLOW}📤 Tagging backend image...${NC}"
docker tag $BACKEND_IMAGE:latest $ECR_BASE/$BACKEND_IMAGE:latest

echo -e "${YELLOW}📤 Pushing backend image...${NC}"
docker push $ECR_BASE/$BACKEND_IMAGE:latest
echo -e "${GREEN}✅ Backend image pushed${NC}"

# Build and push frontend
echo ""
echo -e "${YELLOW}🔨 Building frontend image...${NC}"
docker build -t $FRONTEND_IMAGE:latest -f deployment/docker/Dockerfile.frontend .

echo -e "${YELLOW}📤 Tagging frontend image...${NC}"
docker tag $FRONTEND_IMAGE:latest $ECR_BASE/$FRONTEND_IMAGE:latest

echo -e "${YELLOW}📤 Pushing frontend image...${NC}"
docker push $ECR_BASE/$FRONTEND_IMAGE:latest
echo -e "${GREEN}✅ Frontend image pushed${NC}"

echo ""
echo -e "${GREEN}✅ All images pushed successfully!${NC}"
echo ""
echo "Backend image: $ECR_BASE/$BACKEND_IMAGE:latest"
echo "Frontend image: $ECR_BASE/$FRONTEND_IMAGE:latest"
echo ""
echo "Update your docker-compose.yml or ECS task definition with these image URIs."
