import boto3
import argparse

parser = argparse.ArgumentParser(
    prog='Get the ID of a security group',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    Give the region and appname and get a security group id back
    ''')
parser.add_argument('-iid','--instance_id', required=True)
parser.add_argument('-tak','--tag_key', required=True)
parser.add_argument('-tav','--tag_value', required=True)
arg = parser.parse_args()

ec2 = boto3.client('ec2',arg.region_name)

def set_tags(instance_id):
    tags = client.create_tags(
        Resources=[
            instance_id,
        ],
        Tags=[
            {
                'Key': arg.tag_key,
                'Value': arg.tag_value
            }
        ]
    )
    return tags
