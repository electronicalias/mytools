#!/usr/bin/env python
import argparse
from troposphere import Base64, FindInMap, GetAtt, AWSHelperFn, AWSObject, AWSProperty, Join
from troposphere import Parameter, Output, Ref, Template
from troposphere.cloudwatch import Alarm, MetricDimension
import troposphere.autoscaling as asc
import troposphere.ec2 as ec2


''' Collect all of the command line variables '''
parser = argparse.ArgumentParser(
prog='alarm creater',
formatter_class=argparse.RawDescriptionHelpFormatter,
description='''This program will build an alarm stack.''')
parser.add_argument('-rgn','--region_name', required=True)
args = parser.parse_args()

def param(name):
    name = t.add_parameter(Parameter(
        name,
        Description="Auto Generated Param",
        Type="String",
        Default=name,
    ))

def elb(name):
    name = t.add_resource(
        Alarm(
            name,
            AlarmDescription="Alarm if queue depth grows beyond 10 messages",
            Namespace="AWS/ELB",
            MetricName="SurgeQueueLength",
            Dimensions=[
                MetricDimension(
                    Name="LoadBalancerName",
                    Value=Ref(name)
                ),
            ],
            Statistic="Maximum",
            Period="60",
            EvaluationPeriods="3",
            Threshold="100",
            ComparisonOperator="GreaterThanOrEqualToThreshold",
            AlarmActions=["snstopic"],
            InsufficientDataActions=[],
        )
    )

t = Template()

param_count = 1
for i in range(1,10):
    param('test' + str(param_count))
    elb('test' + str(param_count))
    param_count = param_count + 1


alarm_for = t.add_resource(
    Alarm(
        "ELBSurgeQueueLenth",
        AlarmDescription="Alarm if queue depth grows beyond 10 messages",
        Namespace="AWS/ELB",
        MetricName="SurgeQueueLength",
        Dimensions=[
            MetricDimension(
                Name="LoadBalancerName",
                Value="ELBNAME"
            ),
        ],
        Statistic="Maximum",
        Period="60",
        EvaluationPeriods="3",
        Threshold="100",
        ComparisonOperator="GreaterThanOrEqualToThreshold",
        AlarmActions=["snstopic"],
        InsufficientDataActions=[],
    )
)


print(t.to_json())
