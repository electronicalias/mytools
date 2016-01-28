#!/usr/bin/env python
import argparse
import detailer
from troposphere import Base64, FindInMap, GetAtt, AWSHelperFn, AWSObject, AWSProperty, Join
from troposphere import Parameter, Output, Ref, Template
import troposphere.autoscaling as asc
import troposphere.ec2 as ec2


''' Collect all of the command line variables '''
parser = argparse.ArgumentParser(
prog='Web Stack Creator',
formatter_class=argparse.RawDescriptionHelpFormatter,
description='''This program will build a variable sized webstack in any region''')
parser.add_argument('-rgn','--region', help='Specify the region this will be deployed in', required=True)
args = parser.parse_args()

cmd = detailer.resource(args.region)

resources = {}

for i in cmd.az('production', 'public'):
    resources[str(i['SubnetId'])] = str(i['AvailabilityZone'])

print resources
len(resources)

count = 1

t = Template()

for key, value in resources.iteritems():
    subnet_param = template.add_parameter(Parameter(
        "SubnetId",
        Description="Subnet Id of the network where nodes are deployed",
        Type="String",
        Default=args.subnet_id,
        ))
    return subnet_param

print(t.to_json())