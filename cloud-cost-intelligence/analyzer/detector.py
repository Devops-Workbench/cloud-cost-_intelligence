import boto3
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

def get_aws_clients():
    kwargs = {
        'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
        'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'region_name': os.getenv('AWS_DEFAULT_REGION')
    }
    return {
        'ec2': boto3.client('ec2', **kwargs),
        'cloudwatch': boto3.client('cloudwatch', **kwargs),
        'rds': boto3.client('rds', **kwargs),
        'pricing': boto3.client('pricing', region_name='us-east-1',
                    aws_access_key_id=kwargs['aws_access_key_id'],
                    aws_secret_access_key=kwargs['aws_secret_access_key'])
    }

def get_metric_average(cloudwatch, namespace, metric_name, dimensions, days=30):
    response = cloudwatch.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=datetime.utcnow() - timedelta(days=days),
        EndTime=datetime.utcnow(),
        Period=days * 86400,
        Statistics=['Average']
    )
    if response['Datapoints']:
        return round(response['Datapoints'][0]['Average'], 2)
    return 0.0

def get_idle_ec2_instances():
    clients = get_aws_clients()
    ec2 = clients['ec2']
    cloudwatch = clients['cloudwatch']

    reservations = ec2.describe_instances(Filters=[
        {'Name': 'instance-state-name', 'Values': ['running']}
    ])['Reservations']

    idle_instances = []

    for r in reservations:
        for instance in r['Instances']:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']

            dimensions = [{'Name': 'InstanceId', 'Value': instance_id}]

            avg_cpu = get_metric_average(cloudwatch, 'AWS/EC2', 'CPUUtilization', dimensions)
            avg_network = get_metric_average(cloudwatch, 'AWS/EC2', 'NetworkIn', dimensions)

            if avg_cpu < 5.0 and avg_network < 1000000:  # CPU < 5% AND Network < 1MB
                idle_instances.append({
                    'resource_type': 'EC2',
                    'instance_id': instance_id,
                    'instance_type': instance_type,
                    'avg_cpu': avg_cpu,
                    'avg_network_in': avg_network,
                    'recommendation': 'stop or downsize'
                })

    return idle_instances

def get_idle_rds_instances():
    clients = get_aws_clients()
    rds = clients['rds']
    cloudwatch = clients['cloudwatch']

    instances = rds.describe_db_instances()['DBInstances']
    idle_rds = []

    for db in instances:
        db_id = db['DBInstanceIdentifier']
        db_class = db['DBInstanceClass']

        dimensions = [{'Name': 'DBInstanceIdentifier', 'Value': db_id}]
        avg_connections = get_metric_average(cloudwatch, 'AWS/RDS', 'DatabaseConnections', dimensions)

        if avg_connections < 1.0:  # Zero connections for 30 days
            idle_rds.append({
                'resource_type': 'RDS',
                'instance_id': db_id,
                'instance_type': db_class,
                'avg_connections': avg_connections,
                'recommendation': 'stop or delete'
            })

    return idle_rds

def get_orphaned_ebs_volumes():
    clients = get_aws_clients()
    ec2 = clients['ec2']

    volumes = ec2.describe_volumes(Filters=[
        {'Name': 'status', 'Values': ['available']}  # available = not attached
    ])['Volumes']

    orphaned = []
    for vol in volumes:
        orphaned.append({
            'resource_type': 'EBS',
            'instance_id': vol['VolumeId'],
            'instance_type': f"{vol['Size']}GB {vol['VolumeType']}",
            'recommendation': 'delete orphaned volume'
        })

    return orphaned

def get_unused_elastic_ips():
    clients = get_aws_clients()
    ec2 = clients['ec2']

    addresses = ec2.describe_addresses()['Addresses']
    unused = []

    for addr in addresses:
        if 'AssociationId' not in addr:  # Not associated with any instance
            unused.append({
                'resource_type': 'ElasticIP',
                'instance_id': addr['PublicIp'],
                'instance_type': 'Elastic IP',
                'recommendation': 'release unused IP ($3.6/month wasted)'
            })

    return unused

def scan_all_resources():
    print("Scanning EC2 instances...")
    ec2 = get_idle_ec2_instances()

    print("Scanning RDS instances...")
    rds = get_idle_rds_instances()

    print("Scanning EBS volumes...")
    ebs = get_orphaned_ebs_volumes()

    print("Scanning Elastic IPs...")
    eips = get_unused_elastic_ips()

    all_resources = ec2 + rds + ebs + eips
    print(f"Total wasteful resources found: {len(all_resources)}")
    return all_resources

if __name__ == "__main__":
    resources = scan_all_resources()
    for r in resources:
        print(r)