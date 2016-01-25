#!/usr/bin/env python
import argparse
import boto3

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

cw = boto3.client('cloudwatch', region)
ec2 = boto3.client('ec2', region)

response = cw.put_metric_alarm(
    AlarmName='OCRLoad',
    AlarmDescription='The CPU Average load of the OCR job has reduced below 10%',
    ActionsEnabled=False,
    MetricName=tag + '/CPU',
    Namespace='HPC',
    Statistic='Average',
    Period=300,
    Unit='Percent',
    EvaluationPeriods=12,
    Threshold=5,
    ComparisonOperator='LessThanThreshold'
)

def alarm_state():
    alarm_status = cw.describe_alarms(
        AlarmNames=[
            'OCRLoad'
        ]
    )
    for val in alarm_status['MetricAlarms']:
        return val['StateValue']

def sotp_instance():
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [ 'running' ]
            },
            {
                'Name': 'tag:Job',
                'Values': [ tag ]
            }
        ]
    )
    for item in response['Reservations']:
        for instance in item['Instances']:
            stop = ec2.stop_instances(
                InstanceIds=[
                     instance['InstanceId']
                ]
            )

if 'OK' in alarm_state():
    print "Do nothing, the alarm status is currently OK"
else:
    print "Stopping Instances"
    # stop_instance()
