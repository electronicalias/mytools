#!/usr/bin/env python
import argparse
from troposphere import Base64, FindInMap, GetAtt
from troposphere import Parameter, Output, Ref, Template
import troposphere.ec2 as ec2
import boto3

parser = argparse.ArgumentParser(
prog='hpc_stack_creator',
formatter_class=argparse.RawDescriptionHelpFormatter,
description='''This program will build a variable sized cluster''')
parser.add_argument('-ami','--ami_id', help='specify the ID of an HPC Node AMI', required=True)
parser.add_argument('-sec','--security_group', help='Specify the Security Group ID', required=True)
parser.add_argument('-net','--subnet_id', help='Specify the ID of a Subnet', required=True)
parser.add_argument('-key','--key_name', help='Specify an existing Key Name', required=True)
parser.add_argument('-nsz','--node_size', help='Specify a Node Size', required=True)
parser.add_argument('-num','--num_nodes', help='Specify the number of Nodes to use', required=True)
parser.add_argument('-rgn','--region', help='Specify the region this will be deployed in', required=True)
args = parser.parse_args()

min = 0
max = int(args.num_nodes)
ami_id = args.ami_id
node_type = args.node_size
region = args.region

def create_node(num, node_ami, node_size):
    ec2_instance = template.add_resource(ec2.Instance(
        "Node" + str(num),
        ImageId=node_ami,
        InstanceType=node_size,
        KeyName=Ref(keyname_param),
        SecurityGroups=[Ref(securitygroup_param)],
        UserData=Base64("80"),
        SubnetId=Ref(subnet_param),
        Tags=[ 
            { "Key": "Name", "Value": "Node" + str(num) },
            { "Key": "Job", "Value": "OCR"},
        ],
        BlockDeviceMappings=[
            {
                "DeviceName" : "/dev/xvda",
                "Ebs" : {
                    "DeleteOnTermination" : "true",
                    "VolumeSize" : "100",
                    "VolumeType" : "gp2"
                }
            }
        ]
    ))

template = Template()

keyname_param = template.add_parameter(Parameter(
    "KeyName",
    Description="Name of your EC2 Keypair",
    Type="String",
    Default=args.key_name,
))

subnet_param = template.add_parameter(Parameter(
    "SubnetId",
    Description="Subnet Id of the network where nodes are deployed",
    Type="String",
    Default=args.subnet_id,
))

securitygroup_param = template.add_parameter(Parameter(
    "SecurityGroupId",
    Description="The Security Group that the cluster nodes will use",
    Type="String",
    Default=args.security_group,
))

for num in range(min, max):
    create_node(num, ami_id, node_type)


cfn = boto3.client('cloudformation', region)
cfn_body = template.to_json()

response = cfn.create_stack(
    StackName='ClusterNodes',
    TemplateBody=cfn_body,
    Capabilities=[
        'CAPABILITY_IAM',
    ],
    Tags=[
        {
            'Key': 'Name',
            'Value': 'ClusterNodeStack'
        }
     ],
)

print response
