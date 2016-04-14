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
parser.add_argument('-cst','--customer_name', required=True)
arg = parser.parse_args()


yesterday = date.today() - timedelta(1)
yday = yesterday.strftime('%Y%m%d')

ec2 = boto3.client('ec2',arg.region_name)


def get_image():
    data = ec2.describe_images(
        Owners=[
            'self',
        ],
        Filters=[
            {
                'Name': 'tag:Customer',
                'Values': [
                    arg.customer_name
                ]
            },
            {
                'Name': 'tag:Date',
                'Values': [
                    yday
                ]
            }
        ]
    )
    for record in data['Images']:
        return record['ImageId']

print get_image()
