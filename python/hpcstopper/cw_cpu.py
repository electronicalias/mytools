#!/usr/bin/env pythoA
import argparse
import datetime
import boto3

ec2 = boto3.client('ec2', 'sa-east-1')
cw = boto3.client('cloudwatch', 'sa-east-1')

parser = argparse.ArgumentParser(
    prog='HPC_OPTIMIZER',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    Welcoe to the HPC Cluster Optimizer, this optimizer works on the basis that you are using a tag called 'Usage', the value of which
    can be used to query running instances to see if they have finished processing. If they have it will stop the instances.
    ''')
parser.add_argument('-rgn','--region_name', required=True)
parser.add_argument('-tag','--tag_name', required=True)
arg = parser.parse_args()

region = arg.region_name
tag = arg.tag_name

def metric_series(instance_id):
    metric = cw.get_metric_statistics(
        Period=300,
        StartTime=datetime.datetime.utcnow() - datetime.timedelta(seconds=1800),
        EndTime=datetime.datetime.utcnow(),
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Statistics=[
            'Average'
        ],
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            },
        ],
        Unit='Percent'
    )
    return metric['Datapoints']


response = ec2.describe_instances(
    Filters=[
        {
            'Name': 'instance-state-name',
            'Values': [ 'running' ]
        },
        {
            'Name': 'tag:Usage',
            'Values': [ 'OCR' ]
        }
    ]
)
ave_count = 0
cpu_value = 0
for item in response['Reservations']:
    for instance in item['Instances']:
        for metric in metric_series(instance['InstanceId']):
            cpu_value = cpu_value + metric['Average']
            ave_count = ave_count + 1

''' Calculate the average CPU load over all HPC OCR instances '''
average = cpu_value / ave_count

cw.put_metric_data(
    Namespace='HPC',
    MetricData=[
        {
            'MetricName': tag + '/CPU',
             'Timestamp': datetime.datetime.utcnow(),
             'Value': average,
             'Unit': 'Percent'
         }
    ]
)
