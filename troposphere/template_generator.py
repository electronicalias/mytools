#!/usr/bin/python

from troposphere import Parameter, Ref, Tags, Template, Join
from troposphere.ec2 import VPC, Subnet, InternetGateway, NetworkAcl, VPCGatewayAttachment, RouteTable, Route, SubnetRouteTableAssociation
from netaddr import IPNetwork
import argparse
import boto.cloudformation

parser = argparse.ArgumentParser(prog='Attributes Collection')
parser.add_argument('--profileName')
parser.add_argument('--companyName')
parser.add_argument('--projectName')
parser.add_argument('--vpcCidr')
parser.add_argument('--privateSubnets')
parser.add_argument('--publicSubnets')
parser.add_argument('--dmzSubnets')
parser.add_argument('--dbSubnets')
parser.add_argument('--stackType')
args = parser.parse_args()

pubLimit = '6'
privLimit = '6'

stackAttributes = []
stackAttributes.append(args.stackType)
stackAttributes.append(args.privateSubnets)
stackAttributes.append(args.publicSubnets)
stackAttributes.append(args.dmzSubnets)
stackAttributes.append(args.dbSubnets)


if (args.privateSubnets >= privLimit) or (args.publicSubnets >= pubLimit):
     print("Current subnet support is 5 per zone")
     exit (1)

net = IPNetwork(args.vpcCidr)
subnets = list(net.subnet(24))

def create_vpc(vpc_name):
    MyVPC = t.add_resource(
        VPC(
            vpc_name,
            CidrBlock=args.vpcCidr,
            Tags=Tags(
                Company=args.companyName,
                Project=args.projectName)))
    return MyVPC

def create_internet_gateway():
    internetGateway = t.add_resource(
        InternetGateway(
            'InternetGateway',
            Tags=Tags(
                Project=args.projectName,
                Company=args.companyName)))
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
                Project=args.projectName,
                Company=args.companyName)))
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


def create_subnet(name, num, net_num, type, az):
    azones = ['NoValue', 'a', 'b', 'c', 'a', 'b', 'c']
    subnet = t.add_resource(
        Subnet(
            name + str(num),
            CidrBlock=str(subnets[int(net_num)]),
            AvailabilityZone=Join("", [ Ref("AWS::Region"), azones[int(az)] ] ),
            VpcId=Ref(VPC),
            Tags=Tags(
                NetType=type,
                Company=args.companyName,
                Project=args.projectName)))
    return subnet

def create_subnet_association(name, subnet, num):
    subnetRouteTableAssociation = t.add_resource(
        SubnetRouteTableAssociation(
            name + str(num),
            SubnetId=Ref(subnet),
            RouteTableId=Ref(routeTable),
        ))
    return subnetRouteTableAssociation

def create_stack(region, stack_name, template_body, profile):
    '''Create a stack'''
    cf_conn = boto.cloudformation.connect_to_region(region, profile_name=profile)
    print("Creating {} Stack in {}".format(stack_name, region))
    try:
        cf_conn.create_stack(
                       stack_name,
                       template_body,
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

if 'POC' in stackAttributes[0]:
    VPC = create_vpc('PocVpc')
    internetGateway = create_internet_gateway()
    gatewayAttachment = create_gateway_attachment(VPC, internetGateway)
    routeTable = create_route_table('PocRouteTable', VPC)
    route = create_route('InternetRoute', 'AttachGateway', internetGateway, '0.0.0.0/0', routeTable)
    count = 1
    while count <= int(args.publicSubnets):
        subnet = create_subnet('PublicSubnet', count, 'public')
        subnetRouteTableAssociation = create_subnet_association('PublicSubnetAssociation', subnet, count)
        count = count + 1

    cfn_body = str(t.to_json())
    create_stack('eu-west-1', 'tp-poc', cfn_body, args.profileName)

elif 'WEB' in stackAttributes[0]:
    zoneList = ['Private', 'Public', 'Dmz', 'Db']
    VPC = create_vpc('WebStackVpc')
    internetGateway = create_internet_gateway()
    gatewayAttachment = create_gateway_attachment(VPC, internetGateway)
    for zone in zoneList:
        routeTable = create_route_table(zone + 'RouteTable', VPC)
        if 'Public' or 'Dmz' in zone:
            route = create_route(zone + 'InternetRoute', 'AttachGateway', internetGateway, '0.0.0.0/0', routeTable)
        
        count = 1
        if 'Public' in zone:
            net_count = 100
        elif 'Private' in zone:
            net_count = 130
        elif 'Dmz' in zone:
            net_count = 160
        elif 'Db' in zone:
            net_count = 190
        def get_var(the_zone):
            if 'private' in the_zone:
                var = 1
            if 'public' in the_zone:
                var = 2
            if 'dmz' in the_zone:
                var = 3
            if 'db' in the_zone:
                var = 4
            return stackAttributes[int(var)]
        while count <= int(get_var(zone.lower())):
            subnet = create_subnet(zone + 'Subnet', count, net_count, 'public', count)
            subnetRouteTableAssociation = create_subnet_association(zone + 'SubnetAssociation', subnet, count)
            count = count + 1
            net_count = net_count + 1

    cfn_body = str(t.to_json())
    create_stack('eu-west-1', 'tp-poc', cfn_body, args.profileName)


