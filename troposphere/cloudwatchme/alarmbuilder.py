#!/usr/bin/env python
import argparse
from troposphere import Base64, FindInMap, GetAtt, AWSHelperFn, AWSObject, AWSProperty, Join
from troposphere import Parameter, Output, Ref, Template
from troposphere.cloudwatch import Alarm, MetricDimension
import troposphere.autoscaling as asc
import troposphere.ec2 as ec2
import boto3
from subprocess import call
from subprocess import Popen, PIPE
import json
import time

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

ec2 = boto3.client('elb',arg.region_name)
sns = boto3.client('sns',arg.region_name)
cfn = boto3.client('cloudformation',arg.region_name)
elbs = ec2.describe_load_balancers()

def topic_arn():
    arn = sns.list_topics()
    for item in arn['Topics']:
        if arg.topic_name in item['TopicArn']:
            return item['TopicArn']

def param(name, param_type):
    res_name = str(name).replace('-','')
    name = t.add_parameter(Parameter(
        res_name + 'Param',
        Description=str('Auto Generated Param for: ' + param_type + ' : ' + name),
        Type="String",
        Default=name,
    ))

def elb(name, metric_type):
    if 'Latency' in metric_type:
        stat_type = 'Average'
    res_name = str(name).replace('-','')
    name = t.add_resource(
        Alarm(
            res_name,
            AlarmDescription="SurgeQueueLength Alarm if the queue is over 100 max per minute.",
            Namespace="AWS/ELB",
            MetricName=metric_type,
            Dimensions=[
                MetricDimension(
                    Name="LoadBalancerName",
                    Value=Ref(str(res_name) + 'Param')
                ),
            ],
            Statistic=stat_type,
            Period="60",
            EvaluationPeriods="5",
            Threshold="0.8",
            ComparisonOperator="GreaterThanOrEqualToThreshold",
            AlarmActions=[Ref(sns_topic_name)],
        )
    )

def create_change_set(set_name, stack_name):
    p = Popen(str('/usr/bin/aws cloudformation create-change-set \
    --change-set-name ' + set_name + '\
    --stack-name ' + stack_name + '\
    --capabilities CAPABILITY_IAM \
    --region ' + arg.region_name + ' \
    --template-body file://cfn_body.json'), shell=True)
    return p

def get_change_set(set_name, stack_name):
    p = Popen(str('/usr/bin/aws cloudformation describe-change-set \
    --change-set-name ' + set_name + ' \
    --stack-name ' + stack_name + ' \
    --region ' + arg.region_name), shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate() 
    return out

topic = topic_arn()

t = Template()

t.add_description("""\
This script is automatically deployed by Jenkins, the script first lists all of the ELBs in a region and then installs the alarms specified for each...""")

sns_topic_name = t.add_parameter(Parameter(
    "SnsTopicArn",
    Description=str("Auto Generated Paramemerter for an SNS Topic"),
    Type="String",
    Default=topic,
))

for i in elbs['LoadBalancerDescriptions']:
    param(str(i['LoadBalancerName']), 'ELB')
    elb(str(i['LoadBalancerName']), 'Latency')

# print(t.to_json())

cfn_body = t.to_json()
cfn_file = open("cfn_body.json", "w")
cfn_file.write(cfn_body)
cfn_file.close()

set_name = 'tweet-tweet'
stack_name = 'CloudWatch-Alarms'

create_change_set(set_name, stack_name)
time.sleep(10)

data = json.loads(get_change_set(set_name, stack_name))

print("{0:35} {1:65} {2:25} {3:25}".format("ResourceType", "PhysicalResourceId", "Action", "Replacement"))
for i in data['Changes']:
    print("{0:35} {1:65} {2:25} {3:25}".format(
    i['ResourceChange']['ResourceType'],
    i['ResourceChange']['PhysicalResourceId'],
    i['ResourceChange']['Action'],
    i['ResourceChange']['Replacement']))

user_input = raw_input("Please enter Yes if you wish to continue this change, please note anywhere that it says replace. This program will log \
the request and the user that creates the request. Enter No if you do not wish to continue: ")

if 'Y' not in user_input or 'y' not in user_input or 'Yes' not in user_input or 'yes' not in user_input:
    exit

'''
response = cfn.create_stack(
    StackName='CloudWatch-Alarms',
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
'''
