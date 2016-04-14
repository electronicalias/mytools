import boto3
ec2 = boto3.client('ec2','us-east-1')

data = ec2.describe_instances()

print data
