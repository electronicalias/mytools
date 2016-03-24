#!/usr/env/bin python

import boto3
import urllib2      # Used for testing URLs in the healthcheck


region = 'us-east-1'
vpcid = 'vpc-756c1e11'
LocalInstanceId = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read()

client = boto3.client('ec2','us-east-1')

def get_instance(region, vpcid):
        nats = client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Application',
                    'Values': [
                        'nat',
                    ]
                },
                {
                    'Name': 'tag:Location',
                    'Values': [
                        vpcid,
                    ]
                }
            ]
        )
        data = {}
        for res in nats['Reservations']:
            for i in res['Instances']:
                data[i['InstanceId']] = i['Placement']['AvailabilityZone']
        return data

def get_peer_az(instance_id):
    peer_az = get_instance(region,vpcid)
    for key, value in peer_az.iteritems():
        if instance_id not in key:
            print value

get_peer_az(LocalInstanceId)
