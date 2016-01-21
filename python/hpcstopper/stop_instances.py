#!/usr/bin/env python
import boto3

client = boto3.client('cloudwatch', 'sa-east-1')

response = client.put_metric_alarm(
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
    alarm_status = client.describe_alarms(
        AlarmNames=[
            'OCRLoad'
        ]
    )
    for val in alarm_status['MetricAlarms']:
        return val['StateValue']

if 'OK' in alarm_state():
    print "Do nothing"
else:
    print "Do something"
