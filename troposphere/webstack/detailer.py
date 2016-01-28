#!/usr/bin/env python
__author__ = 'Philip Smith'

""" 
Versions: boto3
Usage:

Pulls out all the details from the stack
"""
import boto3


class resource:
    """Initialise the class used to collect resource ids"""
    def __init__(self, region_name):
        self.data = []
        self.ec2 = boto3.client('ec2', region_name)
    
    """Find availability zone names"""
    
    def az(self, project, zone):
        response = self.ec2.describe_subnets(
            Filters=[
                {
                    'Name': 'tag:Zone',
                    'Values': [
                        zone,
                    ]
                },
                {
                    'Name': 'tag:Project',
                    'Values': [
                        project,
                    ]
                },
            ]
        )
        return response['Subnets']

