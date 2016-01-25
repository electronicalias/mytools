#!/usr/bin/env python
import argparse
import boto3

parser = argparse.ArgumentParser(
prog='hpc_stack_deleter',
formatter_class=argparse.RawDescriptionHelpFormatter,
description='''This program will delete the stack with the name provided''')
parser.add_argument('-stk','--stack_name', required=True)
parser.add_argument('-rgn','--region_name', required=True)
args = parser.parse_args()


cfn = boto3.client('cloudformation', args.region_name)

def get_stack_state(stack):
    response = cfn.describe_stacks(
        StackName=stack,
    )
    return response['Stacks'][0]['StackStatus']

var = 1
while var == 1 :
    if 'CREATE_COMPLETE' in get_stack_state(args.stack_name):
        print("Passed Stack Build")
        break
    elif 'ROLLBACK_COMPLETE' in get_stack_state(args.stack_name):
        raise SystemExit

