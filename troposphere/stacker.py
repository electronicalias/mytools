#!/bin/python
import commander
import cloudformer
from troposphere import Parameter, Ref, Tags, Template, Join
from troposphere.ec2 import VPC, Subnet, InternetGateway, NetworkAcl, VPCGatewayAttachment, RouteTable, Route, SubnetRouteTableAssociation
from netaddr import IPNetwork
import boto.cloudformation

cmd = commander.commands()
attribs = cmd.stack_cmd()
""" From this list, you can get:
    list
    test """
network_zones = attribs.network_zones
availability_zones =  attribs.availability_zones
company_name = attribs.company_name
project_name = attribs.project_name
vpc_cidr = attribs.vpc_cidr


net = IPNetwork(vpc_cidr)
subnets = list(net.subnet(24))

aws_cmd = cloudformer.aws_resources()



VPC = aws_cmd.create_vpc(project_name + 'Vpc', company_name, project_name, vpc_cidr)
IGW = aws_cmd.create_internet_gateway(company_name, project_name, 'InternetGateway')
IGWATT = aws_cmd.create_gateway_attachment(project_name + 'Vpc', 'InternetGateway')
PUBRTT = aws_cmd.create_route_table('PublicRouteTable', company_name, project_name, project_name + 'Vpc')
PROUTE = aws_cmd.create_route('PublicRoute', 'AttachGateway', 'InternetGateway', '0.0.0.0/0', 'PublicRouteTable')

aws_cmd.complete_cfn()

