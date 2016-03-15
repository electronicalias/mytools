#!/usr/bin/env python
import boto3
import urllib2

InstanceId = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read()

ec2 = boto3.resource('ec2',region_name='ap-southeast-1')
instance = ec2.Instance(InstanceId)
sg = ec2.SecurityGroup('sg-0000ec64')

print(instance.instance_type)
print(sg.description)

route = ec2.Route('rtb-ae8fdecb','0.0.0.0/0')
print(route.state)

response = route.replace(
    DryRun=True,
    InstanceId=InstanceId
    )
