#!/usr/bin/env python
import boto3

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
        request = ec2.Instance(InstanceId)
        if True ==  request.source_dest_check:
            update = request.modify_attribute(
                SourceDestCheck={
                    'Value': False
                })
            return update