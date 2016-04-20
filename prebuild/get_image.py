import boto3
import argparse
from datetime import date, timedelta

parser = argparse.ArgumentParser(
    prog='Get the ID of a security group',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    Give the region and appname and get a security group id back
    ''')
parser.add_argument('-rgn','--region_name', required=True)
parser.add_argument('-app','--application_name', required=True)
parser.add_argument('-ver','--application_version', required=True)
arg = parser.parse_args()

ec2 = boto3.client('ec2',arg.region_name)


def get_image():
    data = ec2.describe_images(
        Owners=[
            'self',
        ],
        Filters=[
            {
                'Name': 'tag:Application',
                'Values': [
                    arg.application_name
                ]
            },
            {
                'Name': 'tag:Version',
                'Values': [
                    arg.application_version
                ]
            }
        ]
    )
    for record in data['Images']:
        return record['ImageId']

print get_image()
