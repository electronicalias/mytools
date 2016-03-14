#!/usr/env/bin python

import boto3
import urllib
import urllib2

testurls = ["http://www.google.co.uk", "http://www.pool.ntp.org", "http://www.github.com"]

client = boto3.client('ec2','ap-southeast-1')

def get_private_route_tables():
    PrivateRouteTables = client.describe_route_tables(
        Filters=[
            {
                'Name': 'vpc-id',
                'Values': [
                    'vpc-ca681faf',
                ]
            },
            {
                'Name': 'tag:Zone',
                'Values': [
                    'private'
                ]
            }
        ])
    return PrivateRouteTables['RouteTables']

for RouteTable in get_private_route_tables():
    print RouteTable['RouteTableId']
    ec2 = boto3.resource('ec2','ap-southeast-1')
    route_table = ec2.RouteTable(RouteTable['RouteTableId'])
    for route in route_table:
        print(route_table.routes['DestinationCidrBlock'])

for url in testurls:
    request = urllib2.urlopen(url)
    print request.code

InstanceId = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read()
LocalIp = urllib2.urlopen('http://169.254.169.254/latest/meta-data/local-ipv4').read()
AvailabilityZone = urllib2.urlopen('http://169.254.169.254/latest/meta-data/placement/availability-zone').read()

print InstanceId
print LocalIp
print AvailabilityZone
