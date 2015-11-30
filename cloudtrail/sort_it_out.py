import boto.cloudformation
import argparse

arser = argparse.ArgumentParser(prog='Attributes Collection')
parser.add_argument('--iamregion')
parser.add_argument('--stackName')
args = parser.parse_args()

cf_conn = boto.cloudformation.connect_to_region(args.iamregion)

print cf_conn.describe_stack_resources(args.stackName)