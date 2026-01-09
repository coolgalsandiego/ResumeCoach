"""
Deploy Llama 2 model to AWS SageMaker
This script creates a SageMaker endpoint for the Llama 2 model
"""
import boto3
import json
import time
from typing import Optional

sagemaker_client = boto3.client('sagemaker')
iam_client = boto3.client('iam')


def get_or_create_role(role_name: str = 'SageMakerExecutionRole') -> str:
    """Get or create IAM role for SageMaker"""
    try:
        role = iam_client.get_role(RoleName=role_name)
        return role['Role']['Arn']
    except iam_client.exceptions.NoSuchEntityException:
        print(f"Creating IAM role: {role_name}")
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "sagemaker.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        role = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy),
            Description="SageMaker execution role for Resume Coach"
        )
        
        # Attach SageMaker execution policy
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/AmazonSageMakerFullAccess'
        )
        
        return role['Role']['Arn']


def deploy_llama2_model(
    model_name: str,
    instance_type: str = 'ml.g5.2xlarge',
    initial_instance_count: int = 1,
    role_name: str = 'SageMakerExecutionRole',
    image_uri: Optional[str] = None,
    model_data_uri: Optional[str] = None
):
    """
    Deploy Llama 2 model to SageMaker
    
    Args:
        model_name: Name for the model/endpoint
        instance_type: EC2 instance type (e.g., ml.g5.2xlarge)
        initial_instance_count: Number of instances
        role_name: IAM role name
        image_uri: Docker image URI (if using custom container)
        model_data_uri: S3 URI for model artifacts
    """
    print(f"Deploying Llama 2 model: {model_name}")
    
    # Get or create IAM role
    role_arn = get_or_create_role(role_name)
    print(f"Using IAM role: {role_arn}")
    
    # If using Hugging Face DLC (Deep Learning Container)
    if not image_uri:
        # Use Hugging Face Llama 2 DLC
        region = boto3.Session().region_name
        account_id = boto3.client('sts').get_caller_identity()['Account']
        
        # Hugging Face DLC for Llama 2
        image_uri = (
            f"{account_id}.dkr.ecr.{region}.amazonaws.com/"
            f"huggingface-pytorch-inference:2.0.0-transformers4.28.1-gpu-py310-cu118-ubuntu20.04"
        )
    
    # Create model
    model_config = {
        'ModelName': model_name,
        'PrimaryContainer': {
            'Image': image_uri,
            'ModelDataUrl': model_data_uri or f's3://your-bucket/models/{model_name}/',
            'Environment': {
                'HF_MODEL_ID': 'meta-llama/Llama-2-7b-chat-hf',
                'HF_TASK': 'text-generation',
                'MAX_INPUT_LENGTH': '2048',
                'MAX_TOTAL_TOKENS': '4096',
            }
        },
        'ExecutionRoleArn': role_arn
    }
    
    try:
        print("Creating SageMaker model...")
        sagemaker_client.create_model(**model_config)
        print(f"Model created: {model_name}")
    except sagemaker_client.exceptions.ClientError as e:
        if 'ResourceInUse' in str(e):
            print(f"Model {model_name} already exists")
        else:
            raise
    
    # Create endpoint configuration
    endpoint_config_name = f"{model_name}-config"
    endpoint_config = {
        'EndpointConfigName': endpoint_config_name,
        'ProductionVariants': [{
            'VariantName': 'AllTraffic',
            'ModelName': model_name,
            'InitialInstanceCount': initial_instance_count,
            'InstanceType': instance_type,
            'InitialVariantWeight': 1
        }]
    }
    
    try:
        print("Creating endpoint configuration...")
        sagemaker_client.create_endpoint_config(**endpoint_config)
        print(f"Endpoint configuration created: {endpoint_config_name}")
    except sagemaker_client.exceptions.ClientError as e:
        if 'ResourceInUse' in str(e):
            print(f"Endpoint config {endpoint_config_name} already exists")
        else:
            raise
    
    # Create endpoint
    endpoint_name = model_name
    try:
        print("Creating endpoint...")
        sagemaker_client.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=endpoint_config_name
        )
        print(f"Endpoint creation initiated: {endpoint_name}")
        
        # Wait for endpoint to be ready
        print("Waiting for endpoint to be in service...")
        waiter = sagemaker_client.get_waiter('endpoint_in_service')
        waiter.wait(EndpointName=endpoint_name)
        print(f"Endpoint is ready: {endpoint_name}")
        
    except sagemaker_client.exceptions.ClientError as e:
        if 'ResourceInUse' in str(e):
            print(f"Endpoint {endpoint_name} already exists")
            # Check status
            response = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
            status = response['EndpointStatus']
            print(f"Current endpoint status: {status}")
        else:
            raise
    
    return endpoint_name


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy Llama 2 to SageMaker')
    parser.add_argument('--model-name', default='llama2-resume-coach', help='Model name')
    parser.add_argument('--instance-type', default='ml.g5.2xlarge', help='Instance type')
    parser.add_argument('--instance-count', type=int, default=1, help='Instance count')
    parser.add_argument('--role-name', default='SageMakerExecutionRole', help='IAM role name')
    
    args = parser.parse_args()
    
    endpoint_name = deploy_llama2_model(
        model_name=args.model_name,
        instance_type=args.instance_type,
        initial_instance_count=args.instance_count,
        role_name=args.role_name
    )
    
    print(f"\n✅ Deployment complete!")
    print(f"Endpoint name: {endpoint_name}")
    print(f"\nUpdate your .env file with:")
    print(f"SAGEMAKER_ENDPOINT={endpoint_name}")
    print(f"USE_SAGEMAKER=true")
