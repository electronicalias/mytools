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
print(len(resources))

count = 1
def subnet(value):
    string = t.add_parameter(Parameter(
        "SubnetId" + str(count),
        Description="Subnet Id of the network where nodes are deployed",
        Type="String",
        Default=value,
        ))
    return "SunbetId" + str(count) 

t = Template()

params = {}
for num in range(len(resources) + 1):
    params[str([num])] = ''

for key, value in resources.iteritems():
    subnet(value)
    count += 1

subnets = []
azs = []

for key, value in resources.iteritems():
    subnets.append(value)

for key, value in resources.iteritems():
    azs.append(key)

autoscaling_group = t.add_resource(asc.AutoScalingGroup(
    "AutoscalingGroup",
    DesiredCapacity=0,
    Tags=[
        asc.Tag("Environment", "HPC", True),
        asc.Tag("RequestedBy", "psmith", True),
        asc.Tag("Job", "hpc-spot", True),
    ],
    LaunchConfigurationName="somelc",
    MinSize=0,
    MaxSize=0,
    VPCZoneIdentifier=[ subnets ],
    AvailabilityZones=[ azs ],
    HealthCheckType="EC2",
))
print(t.to_json())
print params
