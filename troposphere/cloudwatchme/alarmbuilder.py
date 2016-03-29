#!/usr/bin/env python
import argparse
from troposphere import Base64, FindInMap, GetAtt, AWSHelperFn, AWSObject, AWSProperty, Join
from troposphere import Parameter, Output, Ref, Template
from troposphere.cloudwatch import Alarm, MetricDimension
import troposphere.autoscaling as asc
import troposphere.ec2 as ec2
import boto3

ec2 = boto3.client('elb','us-east-1')
sns = boto3.client('sns','us-east-1')
elbs = ec2.describe_load_balancers()


''' Collect all of the command line variables '''
parser = argparse.ArgumentParser(
prog='alarm creater',
formatter_class=argparse.RawDescriptionHelpFormatter,
description='''This program will build an alarm stack.''')
parser.add_argument('-rgn','--region_name', required=True)
parser.add_argument('-tpn','--topic_name', required=True)
arg = parser.parse_args()

def topic_arn():
    arn = sns.list_topics()
    for item in arn['Topics']:
        if arg.topic_name in item['TopicArn']:
            return item['TopicArn']

def param(name):
    name = t.add_parameter(Parameter(
        name + 'Param',
        Description="Auto Generated Param",
        Type="String",
        Default=name,
    ))

def elb(name,topic):
    name = t.add_resource(
        Alarm(
            name,
            AlarmDescription="SurgeQueueLength Alarm if the queue is over 100 max per minute.",
            Namespace="AWS/ELB",
            MetricName="SurgeQueueLength",
            Dimensions=[
                MetricDimension(
                    Name="LoadBalancerName",
                    Value=Ref(str(name + 'Param'))
                ),
            ],
            Statistic="Maximum",
            Period="60",
            EvaluationPeriods="3",
            Threshold="100",
            ComparisonOperator="GreaterThanOrEqualToThreshold",
            AlarmActions=[topic],
        )
    )

t = Template()

t.add_description("""\
This script is automatically deployed by Jenkins, the script first lists all of the ELBs in a region and then installs the alarms specified for each...""")

topic = topic_arn()

for i in elbs['LoadBalancerDescriptions']:
    param(str(i['LoadBalancerName']).replace('-',''))
    elb(str(i['LoadBalancerName']).replace('-',''),topic)

# print(t.to_json())

cfn = boto3.client('cloudformation', 'us-east-1')
cfn_body = t.to_json()

response = cfn.create_stack(
    StackName='CloudWatch-Test',
    TemplateBody=cfn_body,
    Capabilities=[
        'CAPABILITY_IAM',
    ],
    Tags=[
        {
            'Key': 'Name',
            'Value': 'CloudWatch-Test'
        },
        {
            'Key': 'RequestedBy',
            'Value': 'Philip Smith'
        }
    ],
)

print response
