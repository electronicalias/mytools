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

response = cfn.delete_stack(
    StackName=args.stack_name,
)

print response 

