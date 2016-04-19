import boto3
import argparse

parser = argparse.ArgumentParser(
    prog='Get the Name of the customers from the instances that are running as a particular Product',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''This tool will require the region and the application name''')
parser.add_argument('-rgn','--region_name', required=True)
parser.add_argument('-app','--application_name', required=True)
arg = parser.parse_args()



ec2 = boto3.client('ec2',arg.region_name)

def get_instances():
    data = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Application',
                'Values': [arg.application_name]
            }
        ]
    )
    for i in data['Reservations']:
        for line in i['Instances']:
            for entry in line['Tags']:
                if 'Customer' in entry['Key'] and entry['Value'] is not None:
                    print entry['Value']
                    


get_instances()
