#!/bin/python
__author__ = 'Philip Smith'

""" 
Usage:

This module can be used to create a cloudformation template and uses troposhere to do so, this tool is aimed at creating VPCs
that have Zones, Subnets, Internet Gateways and Routes
"""


from troposphere import Parameter, Ref, Tags, Template, Join
from troposphere.ec2 import VPC, Subnet, InternetGateway, NetworkAcl, VPCGatewayAttachment, RouteTable, Route, SubnetRouteTableAssociation, SecurityGroup, SecurityGroupIngress

class aws_resources:
    """Initialise the class and start the creationg of the CloudFormation Template"""
    def __init__(self):
        self.data = []
        self.t = Template()
        self.t.add_version('2010-09-09')
        self.t.add_description ("""Base template to build out of band Jenkins and Public, Private, Dmz and DB subnets.""")
    
    """Consume the arguments provided to create the VPC specification"""
    def create_vpc(self, vpc_name, company, project, cidr):
        aVPC = self.t.add_resource(
            VPC(
                vpc_name,
                CidrBlock=cidr,
                Tags=Tags(
                    Name=vpc_name + '-' + company + '-' + project,
                    Company=company,
                    Project=project)))
        self.data.append(aVPC)
    
    """Create an InternetGateway in the template"""
    def create_internet_gateway(self, company, project, igw_name):
        internetGateway = self.t.add_resource(
            InternetGateway(
                igw_name,
                Tags=Tags(
                    Name=igw_name + '-' + company + '-' + project,
                    Project=company,
                    Company=project)))
        self.data.append(internetGateway)

    """Create a Gateway Attachment"""
    def create_gateway_attachment(self, vpc_name, igw_name):
        gatewayAttachment = self.t.add_resource(
            VPCGatewayAttachment(
                'AttachGateway',
                VpcId=Ref(vpc_name),
                InternetGatewayId=Ref(igw_name)))
        self.data.append(gatewayAttachment)

    def create_route_table(self, name, company, project, vpc_name):
        routeTable = self.t.add_resource(
            RouteTable(
                name,
                VpcId=Ref(vpc_name),
                Tags=Tags(
                    Name=name + '-' + company + '-' + project,
                    Project=company,
                    Company=project)))
        self.data.append(routeTable)
        return routeTable

    def create_route(self, name, depends, igw_name, dst_block, rt_id):
        route = self.t.add_resource(
            Route(
                name,
                DependsOn=depends,
                GatewayId=Ref(igw_name),
                DestinationCidrBlock=dst_block,
                RouteTableId=Ref(rt_id),
            ))
        self.data.append(route)
        return route

    def create_subnet(self, name, vpc_name, network, type, az, company, project):
        subnet = self.t.add_resource(
            Subnet(
                name,
                CidrBlock=network,
                AvailabilityZone=Join("", [ Ref("AWS::Region"), az ] ),
                VpcId=Ref(vpc_name),
                Tags=Tags(
                    Name=name,
                    Public=type,
                    Project=project,
                    Company=company)))
        self.data.append(subnet)
        return subnet

    def create_subnet_association(self, name, subnet, rt_id):
        subnetRouteTableAssociation = self.t.add_resource(
            SubnetRouteTableAssociation(
                name,
                SubnetId=Ref(subnet),
                RouteTableId=Ref(rt_id),
            ))
        self.data.append(subnetRouteTableAssociation)

    def create_sg(self, name, vpc_id, description):
        vpcSecurityGroup = self.t.add_resource(
            SecurityGroup(
                name,
                VpcId=vpc_id,
                GroupDescription=description,
                Tags=Tags(
                    Name=name + '-security-group'
            )))
        self.data.append(vpcSecurityGroup)
        return vpcSecurityGroup

    def create_sg_ingress(self, name, from_port, to_port, source_sg, protocol):
        vpcSecurityGroupIngress = self.t.add_resource(
            SecurityGroupIngress(
                name,
                FromPort=from_port,
                ToPort=to_port,
                IpProtocol=protocol,
                SourceSecurityGroupName=Ref(source_sg)
                ))
        self.data.append(SecurityGroupIngress)
        return vpcSecurityGroupIngress

    def complete_cfn(self):
        return(self.t.to_json())            

