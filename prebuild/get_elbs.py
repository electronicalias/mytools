import boto3
import argparse

parser = argparse.ArgumentParser(
    prog='Get the Name of the customers from the instances that are running as a particular Product',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''This tool will require the region and the application name''')
parser.add_argument('-rgn','--region_name', required=True)
parser.add_argument('-app','--application_name', required=True)
arg = parser.parse_args()



ec2 = boto3.client('elb',arg.region_name)

def get_elb_names():
    data = ec2.describe_load_balancers()
    for elb in data['LoadBalancerDescriptions']:
        print elb['LoadBalancerName']

get_elb_names()
