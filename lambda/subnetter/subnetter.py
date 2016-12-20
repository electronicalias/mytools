from cfnlambda import cfn_response, Status, RequestType
import logging
import boto3
from netaddr import *

logging.getLogger().setLevel(logging.DEBUG)

def lambda_handler(event, context):

    netregion = event['ResourceProperties']['Region']
    netvpccidr = event['ResourceProperties']['VpcCidr']
    netvpcid = event['ResourceProperties']['VpcId']
    netmask = int(event['ResourceProperties']['Mask'])
    netsdb = 'ip.subnet.db'

    print event

    nets = []
    subnets = []

    ec2 = boto3.client('ec2', netregion)
    sdb = boto3.client('sdb', netregion)

    def finder(network):
        for i in subnets:
            if network in i:
                nets.remove(network)

    def sdbcheck(domain):
        sdbdomains = sdb.list_domains()
        if len(sdbdomains) >= 1:
            for name in sdbdomains['DomainNames']:
                if name in domain:
                    return True

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

    if event['RequestType'] == RequestType.CREATE:
        if not sdbcheck(netsdb):
            db = sdb.create_domain(
                DomainName=netsdb
                )
            for address in ip.subnet(int(netmask)):
                sdb.put_attributes(
                    DomainName=netsdb,
                    ItemName=address,
                    Attributes=[
                        {
                            'Name': 'exists',
                            'Value': '0',
                            'Replace': True
                        }
                    ]
                )
        subnets = sdb.select(
            SelectExpression='select * from `' + netsdb + '` where exists="0"'
            )
        response = sdb.put_attributes(
            DomainName=netsdb,
            ItemName=subnets['Items'][0]['Name'],
            Attributes=[
                {
                    'Name': 'exists',
                    'Value': '1',
                    'Replace': True
                }])
    if event['RequestType'] == RequestType.DELETE:
        print event['RequestType']



    for cfn_net in data['Subnets']:
        subnets.append(cfn_net['CidrBlock'])
        response = sdb.put_attributes(
            DomainName=netsdb,
            ItemName=cfn_net['CidrBlock'],
            Attributes=[
                {
                    'Name': 'exists',
                    'Value': '1',
                    'Replace': True
                }])

    for address in ip.subnet(int(netmask)):
        nets.append(str(address))
        finder(str(address))

    if event['RequestType'] == RequestType.DELETE:
        result = {'result': 'Deleting Subnet'}
    elif event['RequestType'] == RequestType.UPDATE:
        result = {'result': 'Subnet already up to date, doing nothing'}
    else:
        result = {'result': 'Subnet found',
                  'SubnetCidrBlock': subnets['Items'][0]['Name']}

    cfn_response(event,
                 context,
                 Status.SUCCESS,
                 result)
