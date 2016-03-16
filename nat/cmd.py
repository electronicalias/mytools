#!/usr/bin/env python
import boto3
from subprocess import call

class aws:
    '''
    Usage: can be imported as a module for the following functions:
    Attach EIP, requires Instance Id
    Set Source/Dest Check, requires Instance Id
    '''

    def __init__(self,region):
        self.region = region
        self.ec2_client = boto3.client('ec2',region)
        self.ec2_resource = boto3.resource('ec2',region)

    def associate_eip(self,InstanceId,AllocationId):
        ''' Associate the given InstanceId to the AllocationId '''
        response = self.ec2_client.associate_address(
            InstanceId=InstanceId,
            AllocationId=AllocationId,
            AllowReassociation=True
        )
        return response

    def source_dest(InstanceId):
        instance = self.ec2_resource.Instance(InstanceId)
        if True ==  instance.source_dest_check:
            update = instance.modify_attribute(
                SourceDestCheck={
                    'Value': False
                })
            return update

    def get_peer(self,AvailabilityZone,Application,VpcId):
        peer = self.ec2_client.describe_instances(
            Filters=[
                {
                    'Name': 'availability-zone',
                    'Values': [
                        AvailabilityZone,
                    ]
                },
                {
                    'Name': 'tag:Application',
                    'Values': [
                        Application,
                    ]
                },
                {
                    'Name': 'vpc-id',
                    'Values': [
                        VpcId,
                    ]
                }
            ]
        )
        for instances in peer['Reservations']:
        	for id in instances['Instances']:
        		return id['InstanceId']

    def instance_ip(self,InstanceId):
    	instance = self.ec2_resource.Instance(InstanceId)
    	return(instance.private_ip_address)

    def get_rt_tables(self,VpcId,Zone):
        PrivateRouteTables = self.ec2_client.describe_route_tables(
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
            ]
        )
        return PrivateRouteTables['RouteTables']

    def get_table_id(self,tables):
        for table in tables:
            return self.ec2_resource.RouteTable(table['RouteTableId'])


class bash:
    '''
    Usage: Execute the 'cmd' supplied in a bash terminal
    '''

    def __init__(self):
        self.data = []

    def cmd(self,command):
        call(command,shell=True)