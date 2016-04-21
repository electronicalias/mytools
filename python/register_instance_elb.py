import boto3
import argparse

parser = argparse.ArgumentParser(
    prog='Get the Name of the customers from the instances that are running as a particular Product',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''This tool will require the region and the application name''')
parser.add_argument('-rgn','--region_name', required=True)
parser.add_argument('-elb','--elb_name', required=True)
parser.add_argument('-iid','--instance_id', required=True)
arg = parser.parse_args()

elb = boto3.client('elb',arg.region_name)

def register_instance():
    data = elb.register_instances_with_load_balancer(
        LoadBalancerName=arg.elb_name,
        Instances=[
            {
                'InstanceId': arg.instanceid
            }
        ])
        return data

register_instance()
