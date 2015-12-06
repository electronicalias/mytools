#!/usr/bin/python

from troposphere import Parameter, Ref, Tags, Template
from troposphere.ec2 import VPC, Subnet, InternetGateway, NetworkAcl, VPCGatewayAttachment, RouteTable, Route, SubnetRouteTableAssociation
from netaddr import IPNetwork
import argparse

parser = argparse.ArgumentParser(prog='Attributes Collection')
parser.add_argument('--companyName')
parser.add_argument('--projectName')
parser.add_argument('--vpcCidr')
parser.add_argument('--privateSubnets')
parser.add_argument('--publicSubnets')
args = parser.parse_args()

pubLimit = '6'
privLimit = '6'

stackType = []
val1 = raw_input('''Choose the type of stack you are creating from:
POC - creates a standard single public subnet with single routing table
WEB - creates 4 zones, public, private, dmz and db and 4 individual routing tables

Enter your choice here: ''')

stackType.append(val1)

if (args.privateSubnets >= privLimit) or (args.publicSubnets >= pubLimit):
     print("Current subnet support is 5 per zone")
     exit (1)

net = IPNetwork(args.vpcCidr)
subnets = list(net.subnet(24))

def create_route_table(name)
    routeTable = t.add_resource(
        RouteTable(
            name,
            VpcId=Ref(VPC),
            Tags=Tags(
                Project=Ref(args.projectName),
                Company=Ref(args.companyName))))
    return routeTable

def create_subnet(name, num, type):
    subnet = t.add_resource(
        Subnet(
            name + str(num),
            CidrBlock=str(subnets[int(num)]),
            VpcId=Ref(VPC),
            Tags=Tags(
                NetType=type,
                Company=Ref(args.companyName),
                Project=Ref(args.projectName))))
    return subnet

def create_subnet_association(name, subnet, num):
    subnetRouteTableAssociation = t.add_resource(
        SubnetRouteTableAssociation(
            name + str(num),
            SubnetId=Ref(subnet),
            RouteTableId=Ref(routeTable),
        ))
    return subnetRouteTableAssociation

t = Template()

t.add_version('2010-09-09')

t.add_description ("""\
Base template to build out of band Jenkins and Public, Private, Dmz and DB subnets.""")


VPC = t.add_resource(
    VPC(
        'VPC',
        CidrBlock=Ref(args.vpcCidr),
        Tags=Tags(
            Company=Ref(args.companyName),
            Project=Ref(args.projectName))))

internetGateway = t.add_resource(
    InternetGateway(
        'InternetGateway',
        Tags=Tags(
            Project=Ref(args.projectName),
            Company=Ref(args.companyName))))

gatewayAttachment = t.add_resource(
    VPCGatewayAttachment(
        'AttachGateway',
        VpcId=Ref(VPC),
        InternetGatewayId=Ref(internetGateway)))

if 'POC' in stackType[0]:

    routeTable = t.add_resource(
        RouteTable(
            'RouteTable',
            VpcId=Ref(VPC),
            Tags=Tags(
                Project=Ref(args.projectName),
                Company=Ref(args.companyName))))
    route = t.add_resource(
        Route(
            'InternetRoute',
            DependsOn='AttachGateway',
            GatewayId=Ref('InternetGateway'),
            DestinationCidrBlock='0.0.0.0/0',
            RouteTableId=Ref(routeTable),
        ))

count = 1
while count <= int(args.privateSubnets):
    subnet = create_subnet('PrivateSubnet', count, 'private')
    subnetRouteTableAssociation = create_subnet_association('PrivateSubnetAssociation', subnet, count)
    count = count + 1

count = 1
while count <= int(args.publicSubnets):
    subnet = create_subnet('PublicSubnet', count, 'public')
    subnetRouteTableAssociation = create_subnet_association('PublicSubnetAssociation', subnet, count)
    count = count + 1

print(t.to_json())
