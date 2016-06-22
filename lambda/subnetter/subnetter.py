from cfnlambda import cfn_response, Status, RequestType
import logging
import boto3
from netaddr import *

logging.getLogger().setLevel(logging.INFO)

def lambda_handler(event, context):
    netregion = event['ResourceProperties']['Region']
    netvpccidr = event['ResourceProperties']['VpcCidr']
    netvpcid = event['ResourceProperties']['VpcId']
    netmask = int(event['ResourceProperties']['Mask'])

    print netregion
    print netvpccidr
    print netvpcid
    print netmask

    nets = []
    subnets = []

    ec2 = boto3.client('ec2', netregion)

    def finder(network):
        for i in subnets:
            if network in i:
                nets.remove(network)

    ip = IPNetwork(netvpccidr)

    data = ec2.describe_subnets(
        Filters=[
            {
                'Name' : 'vpc-id',
                'Values' : [
                    netvpcid,
                ]
            }
        ]
    )

    for cfn_net in data['Subnets']:
        subnets.append(cfn_net['CidrBlock'])

    for address in ip.subnet(int(netmask)):
        nets.append(str(address))
        finder(str(address))

    if event['RequestType'] == RequestType.DELETE:
        result = {'result': 'Deleting Subnet'}
    elif event['RequestType'] == RequestType.UPDATE:
        result = {'result': 'Subnet already up to date, doing nothing'}
    else:
        result = {'result': 'Subnet found',
                  'SubnetCidrBlock': nets[0]}

    cfn_response(event,
                 context,
                 Status.SUCCESS,
                 result)
