import boto3
from dotenv import load_dotenv
import os

load_dotenv()

def get_idle_ec2_instances():
    ec2 = boto3.client('ec2',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION')
    )

    cloudwatch = boto3.client('cloudwatch',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION')
    )

    reservations = ec2.describe_instances(Filters=[
        {'Name': 'instance-state-name', 'Values': ['running']}
    ])['Reservations']

    idle_instances = []

    for r in reservations:
        for instance in r['Instances']:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']

            # Check average CPU usage over last 7 days
            metrics = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=__import__('datetime').datetime.utcnow() - __import__('datetime').timedelta(days=7),
                EndTime=__import__('datetime').datetime.utcnow(),
                Period=604800,
                Statistics=['Average']
            )

            if metrics['Datapoints']:
                avg_cpu = metrics['Datapoints'][0]['Average']
                if avg_cpu < 5.0:  # less than 5% CPU = idle
                    idle_instances.append({
                        'instance_id': instance_id,
                        'instance_type': instance_type,
                        'avg_cpu': round(avg_cpu, 2)
                    })

    return idle_instances


if __name__ == "__main__":
    idle = get_idle_ec2_instances()
    print("Idle Instances Found:", idle)