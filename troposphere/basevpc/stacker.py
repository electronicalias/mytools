#!/bin/python
import commander
import cloudformer
from troposphere import Parameter, Ref, Tags, Template, Join
from troposphere.ec2 import VPC, Subnet, InternetGateway, NetworkAcl, VPCGatewayAttachment, RouteTable, Route, SubnetRouteTableAssociation
from netaddr import IPNetwork
import boto.cloudformation
import time

""" Set values that can be used as an operator for subnetting. For example, here, if you're using only 2 subnets
you can safely use 0, 128 as the 3rd octet of an IP range, like:
   172.26.0.0/17
   172.26.128.0/17

Although this segment is used more for 'cycling' through /16 networks, slicing them up based on how many networks are required and then
using the value returned as the operator by which to multiply octet 3. In all cases, the subnetting for this script will opt for /24
subnets. """

subnetworking = {
    1: 0,
    2: 128,
    3: 64,
    4: 64,
    5: 32,
    6: 32,
    7: 32,
    8: 32
    }

""" This function is called in order to set the operator and insert it into the list that makes up each subnet:
Original:
['name=public', 'subnets=N', 'internet=true']

Result:
['name=public', 'subnets=N', 'internet=true', 'network=32']
"""

def set_octet(zones):
    num_zones = len(zones)
    operator =  subnetworking.get(num_zones)
    for zone_id in range(0, num_zones):
    	octet =  operator * zone_id
    	zones[zone_id - 1].append('range=' + str(octet))
    return zones


cmd = commander.commands()
attribs = cmd.stack_cmd()
network_zones = attribs.network_zones
availability_zones =  attribs.availability_zones
company_name = attribs.company_name
project_name = attribs.project_name
vpc_cidr = attribs.vpc_cidr
region_name = attribs.region_name
stack_name = attribs.stack_name


awscmd = commander.aws(region_name)

net = IPNetwork(vpc_cidr)
subnets = list(net.subnet(26))

zones = list(item.split(",") for item in network_zones)
aws_cmd = cloudformer.aws_resources()


VPC = aws_cmd.create_vpc(project_name, company_name, project_name, vpc_cidr)
IGW = aws_cmd.create_internet_gateway(company_name, project_name, 'InternetGateway')
IGWATT = aws_cmd.create_gateway_attachment(project_name, 'InternetGateway')

zone_list = set_octet(zones)
for record in range(0, len(zones)):
    name = zone_list[record][0].split("=")[1]
    num_of_nets = zone_list[record][1].split("=")[1]
    public = zone_list[record][2].split("=")[1]
    net_range = zone_list[record][3].split("=")[1]
    
    route_table = aws_cmd.create_route_table(name + 'RouteTable', company_name, project_name, project_name)
    if 'true' in public:
    	public_route = aws_cmd.create_route(name + 'Route', 'AttachGateway', 'InternetGateway', '0.0.0.0/0', name + 'RouteTable')

    count = 0
    for seq in range(0, int(num_of_nets)):
        network = subnets[int(seq) + int(net_range)]
        if count <= int(len(availability_zones) - 1):
            az = availability_zones[int(count)]
            count = count + 1
        elif count > int(len(availability_zones) - 1):
            count = 0
            az = availability_zones[int(count)]
            count = count + 1
        subnet = aws_cmd.create_subnet(name + 'Subnet' + str(int(seq) + 1), project_name, str(network), public, az, company_name, project_name)
        associate_subnet = aws_cmd.create_subnet_association(name + 'Subnet' + str(int(seq + 1)) + 'Association', subnet, route_table)




cfn_body = aws_cmd.complete_cfn()
# print cfn_body
# awscmd.create_stack(stack_name, cfn_body)
# time.sleep(60)
if stack_name in awscmd.get_stacks():
    # awscmd.update_stack(stack_name, cfn_body)
    print "I found the stack"
else:
    # awscmd.create_stack(stack_name, cfn_body)
    print "It doesn't exist!"
