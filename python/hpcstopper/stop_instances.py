#!/usr/bin/env python
import boto3

cw = boto3.client('cloudwatch', 'sa-east-1')
ec2 = boto3.client('ec2', 'sa-east-1')

response = cw.put_metric_alarm(
    AlarmName='OCRLoad',
    AlarmDescription='The CPU Average load of the OCR job has reduced below 10%',
    ActionsEnabled=False,
    MetricName='CPU',
    Namespace='HPC',
    Statistic='Average',
    Period=300,
    Unit='Percent',
    EvaluationPeriods=6,
    Threshold=10,
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

def terminate_instance():
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [ 'running' ]
            },
            {
                'Name': 'tag:Job',
                'Values': [ 'OCR' ]
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
    terminate_instance()
