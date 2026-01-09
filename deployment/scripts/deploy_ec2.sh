#!/bin/bash

# Deploy Resume Coach application to EC2
# This script sets up an EC2 instance and deploys the application

set -e

# Configuration
INSTANCE_TYPE="${INSTANCE_TYPE:-t3.medium}"
KEY_NAME="${KEY_NAME:-resume-coach-key}"
SECURITY_GROUP_NAME="${SECURITY_GROUP_NAME:-resume-coach-sg}"
REGION="${AWS_REGION:-us-east-1}"
AMI_ID="${AMI_ID:-}"  # Amazon Linux 2 AMI ID (will be fetched if not provided)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting EC2 deployment for Resume Coach${NC}"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

# Get default VPC
echo "📋 Getting default VPC..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region $REGION)
if [ "$VPC_ID" == "None" ] || [ -z "$VPC_ID" ]; then
    echo -e "${RED}❌ No default VPC found. Please specify a VPC.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Using VPC: $VPC_ID${NC}"

# Create security group if it doesn't exist
echo "🔒 Setting up security group..."
SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" \
    --query "SecurityGroups[0].GroupId" \
    --output text \
    --region $REGION 2>/dev/null || echo "")

if [ -z "$SG_ID" ] || [ "$SG_ID" == "None" ]; then
    echo "Creating security group: $SECURITY_GROUP_NAME"
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP_NAME \
        --description "Security group for Resume Coach" \
        --vpc-id $VPC_ID \
        --query "GroupId" \
        --output text \
        --region $REGION)
    
    # Add rules
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region $REGION > /dev/null
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region $REGION > /dev/null
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0 \
        --region $REGION > /dev/null
    
    echo -e "${GREEN}✅ Security group created: $SG_ID${NC}"
else
    echo -e "${GREEN}✅ Using existing security group: $SG_ID${NC}"
fi

# Get latest Amazon Linux 2 AMI if not provided
if [ -z "$AMI_ID" ]; then
    echo "📦 Getting latest Amazon Linux 2 AMI..."
    AMI_ID=$(aws ec2 describe-images \
        --owners amazon \
        --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" "Name=state,Values=available" \
        --query "Images | sort_by(@, &CreationDate) | [-1].ImageId" \
        --output text \
        --region $REGION)
    echo -e "${GREEN}✅ Using AMI: $AMI_ID${NC}"
fi

# Create user data script
USER_DATA=$(cat <<'EOF'
#!/bin/bash
yum update -y
yum install -y docker git

# Start Docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone repository (update with your repo URL)
# git clone https://github.com/yourusername/ResumeCoach.git /opt/resume-coach
# cd /opt/resume-coach

# Or copy files via S3 or other method
# aws s3 sync s3://your-bucket/resume-coach/ /opt/resume-coach/

# Start services
# cd /opt/resume-coach/deployment/docker
# docker-compose up -d

echo "Deployment complete!" > /tmp/deployment-status.txt
EOF
)

# Launch EC2 instance
echo "🖥️  Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SG_ID \
    --user-data "$USER_DATA" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=resume-coach}]" \
    --query "Instances[0].InstanceId" \
    --output text \
    --region $REGION)

echo -e "${GREEN}✅ Instance launched: $INSTANCE_ID${NC}"

# Wait for instance to be running
echo "⏳ Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION
echo -e "${GREEN}✅ Instance is running${NC}"

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query "Reservations[0].Instances[0].PublicIpAddress" \
    --output text \
    --region $REGION)

echo -e "${GREEN}✅ Deployment initiated!${NC}"
echo ""
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo ""
echo "Next steps:"
echo "1. SSH into the instance: ssh -i ~/.ssh/$KEY_NAME.pem ec2-user@$PUBLIC_IP"
echo "2. Clone or copy your application code"
echo "3. Set up environment variables"
echo "4. Run docker-compose up -d"
echo ""
echo -e "${YELLOW}⚠️  Note: The instance is still setting up. Wait a few minutes before accessing.${NC}"
