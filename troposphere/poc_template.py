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

def create_vpc(vpc_name):
    MyVPC = t.add_resource(
        VPC(
            vpc_name,
            CidrBlock=Ref(args.vpcCidr),
            Tags=Tags(
                Company=Ref(args.companyName),
                Project=Ref(args.projectName))))
    return MyVPC

def create_internet_gateway():
    internetGateway = t.add_resource(
        InternetGateway(
            'InternetGateway',
            Tags=Tags(
                Project=Ref(args.projectName),
                Company=Ref(args.companyName))))
    return internetGateway

def create_gateway_attachment(vpc_name, igw_name):
    gatewayAttachment = t.add_resource(
        VPCGatewayAttachment(
            'AttachGateway',
            VpcId=Ref(vpc_name),
            InternetGatewayId=Ref(igw_name)))
    return gatewayAttachment

def create_route_table(name, vpc_name):
    routeTable = t.add_resource(
        RouteTable(
            name,
            VpcId=Ref(vpc_name),
            Tags=Tags(
                Project=Ref(args.projectName),
                Company=Ref(args.companyName))))
    return routeTable

def create_route(name, depends, igw_name, dst_block, rt_id):
    route = t.add_resource(
        Route(
            name,
            DependsOn=depends,
            GatewayId=Ref(igw_name),
            DestinationCidrBlock=dst_block,
            RouteTableId=Ref(rt_id),
        ))
    return route


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

def create_iam_stack(region, stack_name, template_body):
    '''Create the IAM resources required for CloudTrail'''
    IamInstalled = 'True'
    cf_conn = boto.cloudformation.connect_to_region(region)
    print("Creating {} Stack in {}".format(stack_name, region))
    try:
        cf_conn.create_stack(
                       stack_name,
                       template_body,
                       parameters=[
                                   ('InstallIamRole',IamInstalled)
                                   ],
                       capabilities=['CAPABILITY_IAM'],
                       tags=None
                       )
    except Exception as error:
        print("Error creating {}: ****StackTrace: {} ***".format(stack_name, error))
        return (1)

t = Template()

t.add_version('2010-09-09')

t.add_description ("""\
Base template to build out of band Jenkins and Public, Private, Dmz and DB subnets.""")

''' Section to create POC '''

if 'POC' in stackType[0]:
    VPC = create_vpc('PocVpc')
    internetGateway = create_internet_gateway()
    gatewayAttachment = create_gateway_attachment(VPC, internetGateway)
    routeTable = create_route_table('PocRouteTable', VPC)
    route = create_route('InternetRoute', gatewayAttachment, internetGateway, '0.0.0.0/0', routeTable)
    count = 1
    while count <= int(args.publicSubnets):
        subnet = create_subnet('PublicSubnet', count, 'public')
        subnetRouteTableAssociation = create_subnet_association('PublicSubnetAssociation', subnet, count)
        count = count + 1
    with open('templates/POC.json', 'w') as f:
        f.write(str(t.to_json()))
elif 'WEB' in stackType[0]:
    zoneList = ['Public', 'Private', 'Dmz', 'Db']
    VPC = create_vpc('WebStackVpc')
    internetGateway = create_internet_gateway()
    gatewayAttachment = create_gateway_attachment(VPC, internetGateway)
    for zone in zoneList:
        routeTable = create_route_table( zone + 'RouteTable', VPC)
    with open('templates/WEB.json', 'w') as f:
        f.write(str(t.to_json()))
