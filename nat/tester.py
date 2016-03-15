#!/usr/env/bin python

import boto3
import urllib
import urllib2

url1 = 'http://www.google.co.uk'
url2 = 'http://www.pool.ntp.org'
url3 = 'http://www.github.com'

client = boto3.client('ec2','ap-southeast-1')
ec2 = boto3.resource('ec2','ap-southeast-1')

def check_url(url):
    request = urllib2.urlopen(url)
    return request.code

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
    route_table = ec2.RouteTable(RouteTable['RouteTableId'])
    for route in route_table.routes:
        default = 'NoValue'
        if '0.0.0.0' in (route.get('DestinationCidrBlock', default)):
            if 'BlackHole' in route.get('State'):
                print("This sucks!")
            else:
                print("We are good to go")
                print(route.get('InstanceId'))

InstanceId = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read()
LocalIp = urllib2.urlopen('http://169.254.169.254/latest/meta-data/local-ipv4').read()
AvailabilityZone = urllib2.urlopen('http://169.254.169.254/latest/meta-data/placement/availability-zone').read()

print InstanceId
print LocalIp
print AvailabilityZone

if (check_url(url1) == 200) or (check_url(url2) == 200) or (check_url(url3) == 200):
    print("Connectivity is OK")
