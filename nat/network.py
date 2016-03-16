#!/usr/env/bin python
''' Import Modules '''
import boto3
import urllib2
import argparse

InstanceId = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read()
LocalIp = urllib2.urlopen('http://169.254.169.254/latest/meta-data/local-ipv4').read()

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

source_dest(InstanceId)
associate_eip(InstanceId,arg.allocation_id)
