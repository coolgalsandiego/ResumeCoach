"""
Setup auto-scaling for SageMaker endpoint
"""
import boto3
import json
from typing import Optional

application_autoscaling = boto3.client('application-autoscaling')
sagemaker_client = boto3.client('sagemaker')


def setup_autoscaling(
    endpoint_name: str,
    min_capacity: int = 1,
    max_capacity: int = 4,
    target_value: float = 70.0,  # Target CPU utilization %
    scale_in_cooldown: int = 300,  # 5 minutes
    scale_out_cooldown: int = 60   # 1 minute
):
    """
    Setup auto-scaling for SageMaker endpoint
    
    Args:
        endpoint_name: Name of the SageMaker endpoint
        min_capacity: Minimum number of instances
        max_capacity: Maximum number of instances
        target_value: Target metric value (CPU utilization %)
        scale_in_cooldown: Cooldown period before scaling in (seconds)
        scale_out_cooldown: Cooldown period before scaling out (seconds)
    """
    # Verify endpoint exists
    try:
        endpoint = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
        if endpoint['EndpointStatus'] != 'InService':
            raise ValueError(f"Endpoint {endpoint_name} is not in service")
    except sagemaker_client.exceptions.ClientError as e:
        raise ValueError(f"Endpoint {endpoint_name} not found: {e}")
    
    # Get endpoint variant name
    endpoint_config = sagemaker_client.describe_endpoint_config(
        EndpointConfigName=endpoint['EndpointConfigName']
    )
    variant_name = endpoint_config['ProductionVariants'][0]['VariantName']
    
    # Register scalable target
    resource_id = f"endpoint/{endpoint_name}/variant/{variant_name}"
    namespace = "aws/sagemaker"
    scalable_dimension = "sagemaker:variant:DesiredInstanceCount"
    
    print(f"Registering scalable target: {resource_id}")
    try:
        application_autoscaling.register_scalable_target(
            ServiceNamespace=namespace,
            ResourceId=resource_id,
            ScalableDimension=scalable_dimension,
            MinCapacity=min_capacity,
            MaxCapacity=max_capacity
        )
        print(f"✅ Scalable target registered")
    except application_autoscaling.exceptions.ValidationException as e:
        if 'already registered' in str(e).lower():
            print(f"Scalable target already registered, updating...")
            application_autoscaling.register_scalable_target(
                ServiceNamespace=namespace,
                ResourceId=resource_id,
                ScalableDimension=scalable_dimension,
                MinCapacity=min_capacity,
                MaxCapacity=max_capacity
            )
        else:
            raise
    
    # Create scaling policy
    policy_name = f"{endpoint_name}-scaling-policy"
    
    # Target tracking scaling policy
    policy = {
        'TargetTrackingScalingPolicyConfiguration': {
            'TargetValue': target_value,
            'PredefinedMetricSpecification': {
                'PredefinedMetricType': 'SageMakerVariantInvocationsPerInstance'
            },
            'ScaleInCooldown': scale_in_cooldown,
            'ScaleOutCooldown': scale_out_cooldown
        }
    }
    
    print(f"Creating scaling policy: {policy_name}")
    try:
        application_autoscaling.put_scaling_policy(
            PolicyName=policy_name,
            ServiceNamespace=namespace,
            ResourceId=resource_id,
            ScalableDimension=scalable_dimension,
            PolicyType='TargetTrackingScaling',
            **policy
        )
        print(f"✅ Scaling policy created")
    except Exception as e:
        print(f"Error creating policy: {e}")
        raise
    
    print(f"\n✅ Auto-scaling configured!")
    print(f"Endpoint: {endpoint_name}")
    print(f"Min capacity: {min_capacity}")
    print(f"Max capacity: {max_capacity}")
    print(f"Target: {target_value}% CPU utilization")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup auto-scaling for SageMaker endpoint')
    parser.add_argument('--endpoint-name', required=True, help='SageMaker endpoint name')
    parser.add_argument('--min-capacity', type=int, default=1, help='Minimum instances')
    parser.add_argument('--max-capacity', type=int, default=4, help='Maximum instances')
    parser.add_argument('--target-value', type=float, default=70.0, help='Target CPU %')
    parser.add_argument('--scale-in-cooldown', type=int, default=300, help='Scale-in cooldown (seconds)')
    parser.add_argument('--scale-out-cooldown', type=int, default=60, help='Scale-out cooldown (seconds)')
    
    args = parser.parse_args()
    
    setup_autoscaling(
        endpoint_name=args.endpoint_name,
        min_capacity=args.min_capacity,
        max_capacity=args.max_capacity,
        target_value=args.target_value,
        scale_in_cooldown=args.scale_in_cooldown,
        scale_out_cooldown=args.scale_out_cooldown
    )
