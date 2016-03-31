#!/usr/bin/env python
import argparse
from troposphere import Base64, FindInMap, GetAtt, AWSHelperFn, AWSObject, AWSProperty, Join
from troposphere import Parameter, Output, Ref, Template
from troposphere.cloudwatch import Alarm, MetricDimension
import troposphere.autoscaling as asc
import troposphere.ec2 as ec2
import boto3
import time
import cmd
import string
import random


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
awscmd = cmd.aws(arg.region_name)


''' Define all functions here '''
def id_gen(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

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
            EvaluationPeriods="3",
            Threshold="0.7",
            ComparisonOperator="GreaterThanOrEqualToThreshold",
            AlarmActions=[Ref(sns_topic_name)],
        )
    )

def cfn(stack_name, template):
    status = awscmd.get_stack_status(stack_name)
    if 'CREATE_COMPLETE' in status or 'UPDATE_COMPLETE' in status:
        print("Updating: {}".format(stack_name))
        awscmd.update_stack(stack_name,template)
    elif 'No stacks found' in status:
        print("Creating: {}".format(stack_name))
        awscmd.create_stack(stack_name,template)

topic = topic_arn()


''' Creating the Template here '''
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

cfn_body = t.to_json()
''' Finish Creating the Template Here, the JSON can now be accessed from cfn_body '''

set_name = 'change-set-' + id_gen()
stack_name = 'CloudWatch-Alarms'

awscmd.create_change_set(stack_name, set_name, cfn_body)
time.sleep(10)

data = awscmd.describe_change_set(stack_name, set_name)

print("{0:35} {1:65} {2:25} {3:25}".format("ResourceType", "PhysicalResourceId", "Action", "Replacement"))
for i in data['Changes']:
    print("{0:35} {1:65} {2:25} {3:25}".format(
    i['ResourceChange']['ResourceType'],
    i['ResourceChange']['PhysicalResourceId'],
    i['ResourceChange']['Action'],
    i['ResourceChange']['Replacement']))

user_input = raw_input("Please enter Yes if you wish to continue this change, please note anywhere that it says replace. This program will log \
the request and the user that creates the request. Enter No if you do not wish to continue: ")

if 'Y' not in user_input and 'y' not in user_input and 'Yes' not in user_input and 'yes' not in user_input:
    print user_input
    print("This program will now exit")
    exit
else:
    print("Running CloudFormation Update for : {}".format(stack_name))
    cfn(stack_name,cfn_body)
