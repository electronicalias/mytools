import boto3
import collections
import datetime

to_tag = collections.defaultdict(list)

ec2 = boto3.client('ec2', 'eu-west-1')

reservations = ec2.describe_instances(
    Filters=[
        {
            'Name': 'tag-value', 
            'Values': ['IGrasp'],
        },
    ])['Reservations']

instances = sum(
    [
        [i for i in r['Instances']]
        for r in reservations
    ], [])

for instance in instances:
    try:
        retention_days = [
            int(t.get('Value')) for t in instance['Tags']
            if t['Key'] == 'Retention'][0]
    except IndexError:
        retention_days = 7

print retention_days
