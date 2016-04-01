#!/usr/bin/env pyhton
import boto3
import argparse
import pprint

parser = argparse.ArgumentParser(
    prog='Stack Output Fetcher',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    Get the stack outputs for the specified stack
    ''')
parser.add_argument('-rgn','--region_name', required=True)
parser.add_argument('-stk','--stack_name', required=True)
arg = parser.parse_args()


cfn = boto3.client('cloudformation', arg.region_name)

def get_outputs(stack):
    stacks = cfn.describe_stacks(
    StackName=stack
    )
    for item in stacks['Stacks']:
        return item

data = get_outputs(arg.stack_name)
for item in data['Outputs']:
    print("{} = {}".format(item['OutputKey'], item['OutputValue']))
