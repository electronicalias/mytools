import boto3
import argparse

parser = argparse.ArgumentParser(
    prog='Get the ID of a security group',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    Give the region and appname and get a security group id back
    ''')
parser.add_argument('-rgn','--region_name', required=True)
parser.add_argument('-iid','--instance_id', required=True)
arg = parser.parse_args()



ec2 = boto3.resource('ec2',arg.region_name)
instance = ec2.Instance(arg.instance_id)

print instance.state['Name']
