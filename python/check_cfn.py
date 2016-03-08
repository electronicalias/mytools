#/usr/bin/env python
import boto3
import argparse

parser = argparse.ArgumentParser(
    prog='Get the status of a CloudFormation Stack or output None if not found',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    Can be used to test if a stack exists or to output the status of a stack
    ''')
parser.add_argument('-rgn','--region_name', required=True)
parser.add_argument('-stk','--stack_name', required=True)
arg = parser.parse_args()

client = boto3.client('cloudformation', arg.region_name)

def check_stack(name):
    try:
        response = client.describe_stacks(
            StackName=name
        )
        for item in response['Stacks']:
            return item['StackStatus']
    except:
        pass


print check_stack(arg.stack_name)
