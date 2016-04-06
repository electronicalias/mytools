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
parser.add_argument('-num','--net_selection', required=True)
parser.add_argument('-are','--area_name', required=True)
arg = parser.parse_args()

ec2 = boto3.client('ec2', arg.region_name)

def get_subnet():
    result = ec2.describe_subnets(
        Filters=[
            {
                'Name': 'tag:Zone',
                'Values': [
                    arg.zone_name,
                ]
            },
            {
                'Name': 'tag:Project',
                'Values': [
                    arg.area_name,
                ]
            }
        ]
    )
    count = 1
    data = {}
    for sg in result['Subnets']:
        data['net' + str(count)] = {}
        data['net' + str(count)]['subnet'] = sg['SubnetId']
        data['net' + str(count)]['az'] = sg['AvailabilityZone']
        count += 1
    return data

def print_net(selection):
    data = get_subnet()
    print str(data['net' + (str(selection))]['subnet']) + ',' + str(data['net' + (str(selection))]['az'])

print_net(arg.net_selection)
