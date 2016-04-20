#!/usr/bin/env python
import boto3
import argparse

parser = argparse.ArgumentParser(
    prog='Get the ID of a VPC',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    Give the region and StackType and get a VPC ID back
    ''')
parser.add_argument('-rgn','--region_name', required=True)
parser.add_argument('-stk','--stack_type', required=True)
arg = parser.parse_args()

ec2 = boto3.client('ec2', arg.region_name)

def get_vpc():
    result = ec2.describe_vpcs(
        Filters=[
            {
                'Name': 'tag:StackType',
                'Values': [
                    arg.stack_type,
                ]
            }
        ]
    )
    for vpc in result['Vpcs']:
        return vpc['VpcId']
print get_vpc()
