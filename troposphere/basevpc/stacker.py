#!/bin/python
import commander
import cloudformer
from troposphere import Parameter, Ref, Tags, Template, Join
from troposphere.ec2 import VPC, Subnet, InternetGateway, NetworkAcl, VPCGatewayAttachment, RouteTable, Route, SubnetRouteTableAssociation
from netaddr import IPNetwork
import boto.cloudformation
import time

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

def set_octet(zones):
    num_zones = len(zones)
    operator =  subnetworking.get(num_zones)
    for zone_id in range(0, num_zones):
    	octet =  operator * zone_id
    	zones[zone_id - 1].append('range=' + str(octet))
    return zones



cmd = commander.commands()
awscmd = commander.aws('eu-west-1', 'travel_republic')
attribs = cmd.stack_cmd()

network_zones = attribs.network_zones
availability_zones =  attribs.availability_zones
company_name = attribs.company_name
project_name = attribs.project_name
vpc_cidr = attribs.vpc_cidr

net = IPNetwork(vpc_cidr)
subnets = list(net.subnet(24))

zones = list(item.split(",") for item in network_zones)
aws_cmd = cloudformer.aws_resources()


VPC = aws_cmd.create_vpc(project_name + 'Vpc', company_name, project_name, vpc_cidr)
IGW = aws_cmd.create_internet_gateway(company_name, project_name, 'InternetGateway')
IGWATT = aws_cmd.create_gateway_attachment(project_name + 'Vpc', 'InternetGateway')

zone_list = set_octet(zones)
for record in range(0, len(zones)):
    name = zone_list[record][0].split("=")[1]
    num_of_nets = zone_list[record][1].split("=")[1]
    public = zone_list[record][2].split("=")[1]
    net_range = zone_list[record][3].split("=")[1]
    
    route_table = aws_cmd.create_route_table(name + 'RouteTable', company_name, project_name, project_name + 'Vpc')
    if 'true' in public:
    	public_route = aws_cmd.create_route(name + 'Route', 'AttachGateway', 'InternetGateway', '0.0.0.0/0', name + 'RouteTable')

    count = 0
    for seq in range(0, int(num_of_nets)):
        network =  subnets[int(seq) + int(net_range)]
        if count <= int(len(availability_zones) - 1):
            az = availability_zones[int(count)]
            count = count + 1
        elif count > int(len(availability_zones) - 1):
            count = 0
            az = availability_zones[int(count)]
            count = count + 1
        subnet = aws_cmd.create_subnet(name + 'Subnet' + str(int(seq) + 1), project_name + 'Vpc', str(network), public, az, company_name, project_name)
        associate_subnet = aws_cmd.create_subnet_association(name + 'Subnet' + str(int(seq + 1)) + 'Association', subnet, route_table)




cfn_body = aws_cmd.complete_cfn()
print cfn_body
awscmd.create_stack('test-poc-2', cfn_body)
time.sleep(60)
awscmd.get_stack_status('eu-west-1', 'test-poc-2')