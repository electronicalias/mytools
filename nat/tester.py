#!/usr/env/bin python
''' Import Modules '''
import boto3
import urllib
import urllib2
import argparse

''' Set all required Variables '''
url1 = 'http://www.google.co.uk'
url2 = 'http://www.pool.ntp.org'
url3 = 'http://www.github.com'

InstanceId = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read()
LocalIp = urllib2.urlopen('http://169.254.169.254/latest/meta-data/local-ipv4').read()
AvailabilityZone = urllib2.urlopen('http://169.254.169.254/latest/meta-data/placement/availability-zone').read()

''' Setup the Command Line to accept the variables required '''
parser = argparse.ArgumentParser(
    prog='Nat Updater',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    This program is used to re-attach the EIP and set the source-dest-check to false so this instance can take over
    the NAT function.
    ''')
parser.add_argument('-a','--allocation_id', required=True)
arg = parser.parse_args()

''' Connect the clients for Boto '''
client = boto3.client('ec2','ap-southeast-1')
ec2 = boto3.resource('ec2','ap-southeast-1')

''' Build the functions required in the script '''
def source_dest(InstanceId):
    request = ec2.Instance(InstanceId)
    if True ==  request.source_dest_check:
        update = request.modify_attribute(
            SourceDestCheck={
                'Value': False
            })
        return update

def associate_eip(InstanceId,AllocationId):
    response = client.associate_address(
        InstanceId=InstanceId,
        AllocationId=AllocationId,
        AllowReassociation=True
    )
    return response

def update_route(rt_id,dest_blk,ins_id):
    test = boto3.resource('ec2','ap-southeast-1')
    print test
    route = test.Route(rt_id,dest_blk)
    print route
    response = route.replace(
        InstanceId=ins_id
    )
    return response


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
            DestBlock = route.get('DestinationCidrBlock')
            if InstanceId not in route.get('InstanceId'):
                print update_route(route_table,DestBlock,InstanceId)
            else:
                print("We are good to go")
                print(route.get('InstanceId'))

source_dest(InstanceId)
associate_eip(InstanceId,arg.allocation_id)

if (check_url(url1) == 200) or (check_url(url2) == 200) or (check_url(url3) == 200):
    f = open('/var/www/html/index.html', 'w')
    f.write("OK")
    f.close()

OtherServer = urllib2.urlopen('http://localhost/index.html').read()
if 'OK' in OtherServer:
    print("No change reqiured, server is serving NAT")
else:
    print("Changing the shiz")
