import boto3
import argparse

parser = argparse.ArgumentParser(
    prog='Get the Name of the customers from the instances that are running as a particular Product',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''This tool will require the region and the application name''')
parser.add_argument('-rgn','--region_name', required=True)
arg = parser.parse_args()

elb = boto3.client('elb',arg.region_name)

def get_elb_names():
    data = elb.describe_load_balancers()
    return data

def get_elb_tags(elbname):
    tags = elb.describe_tags(
        LoadBalancerNames=[
            elbname,
        ]
    )
    return tags

elbs = get_elb_names()

for result in elbs['LoadBalancerDescriptions']:
    elbtags = get_elb_tags(result['LoadBalancerName'])
    for eachtag in elbtags['TagDescriptions']:
        for atag in eachtag['Tags']:
            if 'Customer' in atag['Key']:
                print atag['Value']
