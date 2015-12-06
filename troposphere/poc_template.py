#!/usr/bin/python

from troposphere import Parameter, Ref, Tags, Template
from troposphere.ec2 import VPC, Subnet, InternetGateway, NetworkAcl, VPCGatewayAttachment, RouteTable, Route
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


if (args.privateSubnets >= privLimit) or (args.publicSubnets >= pubLimit):
     print("Current subnet support is 5 per zone")
     exit (1)

net = IPNetwork(args.vpcCidr)
subnets = list(net.subnet(24))

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
    subnet = t.add_resource(
        Subnet(
            'PrivateSubnet' + str(count),
            CidrBlock=str(subnets[int(count)]),
            VpcId=Ref(VPC),
            Tags=Tags(
                Company=Ref(args.companyName),
                Project=Ref(args.projectName))))
    count = count + 1

count = 1
while count <= int(args.publicSubnets):
    subnet = t.add_resource(
        Subnet(
            'PublicSubnet' + str(count),
            CidrBlock=str(subnets[int(count + 20)]),
            VpcId=Ref(VPC),
            Tags=Tags(
                Company=Ref(args.companyName),
                Project=Ref(args.projectName))))
    count = count + 1

print(t.to_json())
