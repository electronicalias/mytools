#!/usr/bin/env python
import argparse
import boto3
from troposphere import Base64, FindInMap, GetAtt, AWSHelperFn, AWSObject, AWSProperty, Join
from troposphere import Parameter, Output, Ref, Template
import troposphere.autoscaling as asc
import troposphere.ec2 as ec2

parser = argparse.ArgumentParser(
    prog='ID Grabber',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    Grab the id of various things
    ''')
parser.add_argument('-rgn','--region_name', required=True)
arg = parser.parse_args()


ec2 = boto3.client('ec2', arg.region_name)

def get_vals(zone, project, resource):
    response = ec2.describe_subnets(
        Filters=[
            {
                'Name': 'tag:Zone',
                'Values': [
                    zone,
                ]
            },
            {
                'Name': 'tag:Project',
                'Values': [
                    project,
                ]
            },
        ]
    )
    return response['Subnets']

# t = Template()


azs = get_vals('public', 'production', 'AvailabilityZone')
for az in azs:
    print(az['AvailabilityZone'] + " " + az['SubnetId'])



# print(t.to_json())
