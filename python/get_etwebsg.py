#!/usr/bin/env python
import boto3
import argparse

parser = argparse.ArgumentParser(
    prog='Get the ID of a security group',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    Give the region and appname and get a security group id back
    ''')
parser.add_argument('-rgn','--region_name', required=True)
parser.add_argument('-cst','--customer_name', required=True)
parser.add_argument('-app','--application_name', required=True)
arg = parser.parse_args()

ec2 = boto3.client('ec2', arg.region_name)

def get_sg():
    result = ec2.describe_security_groups(
        Filters=[
            {
                'Name': 'tag:Application',
                'Values': [
                    arg.application_name,
                ]
            },
            {
                'Name': 'tag:Customer',
                'Values': [
                    arg.customer_name,
                ]
            }
        ]
    )
    for sg in result['SecurityGroups']:
        return sg['GroupId']

print get_sg()
