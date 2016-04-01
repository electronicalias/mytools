#/usr/bin/env python

import boto3
import pprint
region = boto3.client('ec2', 'us-east-1')
regions = region.describe_regions()


attributes = dict()

def add_subnet(region, subnets):
    attributes[region] = { 'Values' : subnets }

def get_tags(region, resource_id):
    ec2 = boto3.client('ec2', region)
    tags = ec2.describe_tags(
        Filters=[
            {
                'Name': 'resource-id',
                'Values': [
                    resource_id,
                ]
            },
            {
                'Name': 'key',
                'Values': [
                    'Name',
                ]
            },
        ],
    )
    for item in tags['Tags']:
        return item['Value']

for region in regions['Regions']:
    ec2 = boto3.client('ec2', region['RegionName'])
    data = ec2.describe_subnets(
        Filters=[
            {
                'Name': 'tag:Company',
                'Values': [
                    'lumesse',
                ]
            },
            {
                'Name': 'tag:Project',
                'Values': [
                    'production',
                ]
            },
        ], 
    )
    attributes[region['RegionName']] = { 'Values' : '' }
    count = 1
    subnets = dict()
    for id in data['Subnets']:
        # attributes.update({ region['RegionName'] : { 'Values' : { 'Subnets' : { 'SubnetId' + str(count) : id['SubnetId'] }}}})
        # add_subnet(region['RegionName'], 'SubnetId' + str(count), id['SubnetId'])
        subnets[ get_tags(region['RegionName'], id['SubnetId']) ] = id['SubnetId']
        add_subnet(region['RegionName'], subnets)
        count = count + 1  
    for subnetid in data['Subnets']:
        if region['RegionName'] == 'us-east-1':
            pprint.pprint(get_tags(region['RegionName'], subnetid['SubnetId']))

pprint.pprint(attributes)
