import boto3
import argparse

parser = argparse.ArgumentParser(
    prog='Get the ID of a security group',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    Give the region and appname and get a security group id back
    ''')
parser.add_argument('-rgn','--region_name', required=True)
parser.add_argument('-cst','--customer_name', required=True)
parser.add_argument('-img','--image_id', required=True)
parser.add_argument('-net','--subnet_id', required=True)
parser.add_argument('-sec','--sg_id', required=True)
parser.add_argument('-iam','--iam_role', required=True)
parser.add_argument('-key','--key_name', required=True)
parser.add_argument('-iid','--instance_type', required=True)
arg = parser.parse_args()

ec2 = boto3.client('ec2',arg.region_name)

def run_instance():
    data = ec2.run_instances(
        MinCount=1,
        MaxCount=1,
        ImageId=arg.image_id,
        KeyName=arg.key_name,
        InstanceType=arg.instance_type,
        NetworkInterfaces=[
            {
                'DeviceIndex': 0,
                'SubnetId': arg.subnet_id,
                'Groups': [
                    arg.sg_id
                ],
                'AssociatePublicIpAddress': False
            }
        ],
        IamInstanceProfile={
            'Name': arg.iam_role
        }
       
    )
    return data['Instances'][0]['InstanceId']

print run_instance()
