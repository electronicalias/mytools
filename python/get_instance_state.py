import boto3
ec2 = boto3.resource('ec2','us-east-1')
instance = ec2.Instance('i-b63ff531')

print instance.state['Name']
