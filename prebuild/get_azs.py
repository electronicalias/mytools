#!/usr/bin/env python
import boto3
import argparse
import pprint

parser = argparse.ArgumentParser(
    prog='Get the ID of a security group',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    Give the region and appname and get a security group id back
    ''')
parser.add_argument('-rgn','--region_name', required=True)
parser.add_argument('-zne','--zone_name', required=True)
parser.add_argument('-are','--area_name', required=True)
arg = parser.parse_args()

ec2 = boto3.client('ec2', arg.region_name)

def get_azs():
    result = ec2.describe_subnets(
        Filters=[
            {
                'Name': 'tag:Zone',
                'Values': [
                    arg.zone_name,
                ]
            },
            {
                'Name': 'tag:Area',
                'Values': [
                    arg.area_name,
                ]
            }
        ]
    )
    for sg in result['Subnets']:
        print sg['AvailabilityZone']

get_azs()
