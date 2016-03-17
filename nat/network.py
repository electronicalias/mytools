#!/usr/env/bin python
''' Import Modules '''
import boto3
import urllib2

InstanceId = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read()

''' Connect the clients/resources for Boto '''
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


source_dest(InstanceId)