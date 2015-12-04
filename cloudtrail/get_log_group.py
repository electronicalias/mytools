import boto.logs
import argparse

parser = argparse.ArgumentParser(prog='Attributes Collection')
parser.add_argument('--region')
args = parser.parse_args()

connection = boto.logs.connect_to_region(args.region)

cloudtrail_log_arn = connection.describe_log_groups()
print cloudtrail_log_arn

