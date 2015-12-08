#!/bin/python
from troposphere import Parameter, Ref, Tags, Template, Join
from troposphere.ec2 import VPC, Subnet, InternetGateway, NetworkAcl, VPCGatewayAttachment, RouteTable, Route, SubnetRouteTableAssociation




class aws_resources:
    
    def __init__(self):
        self.data = []
        self.t = Template()
        self.t.add_version('2010-09-09')
        self.t.add_description ("""Base template to build out of band Jenkins and Public, Private, Dmz and DB subnets.""")

    def create_vpc(self, vpc_name, company, project, cidr):
        aVPC = self.t.add_resource(
            VPC(
                vpc_name,
                CidrBlock=cidr,
                Tags=Tags(
                    Company=company,
                    Project=project)))
        self.data.append(aVPC)

    def create_internet_gateway(self, company, project, igw_name):
        internetGateway = self.t.add_resource(
            InternetGateway(
                igw_name,
                Tags=Tags(
                    Project=company,
                    Company=project)))
        self.data.append(internetGateway)

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
                    Project=company,
                    Company=project)))
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

    def create_sg(self, name, description, vpc_id, project, company):
        myvpcsecuritygroup = self.t.add_resource(SecurityGroup(
            name,
            GroupDescription=description,
            VpcId=Ref(vpc_name),
            Tags=Tags(
                    Name=name,
                    Project=company,
                    Company=project)))
            ))


    def complete_cfn(self):
        return(self.t.to_json())            

