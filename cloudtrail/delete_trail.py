import boto.cloudtrail
import argparse

parser = argparse.ArgumentParser(prog='Attributes Collection')
parser.add_argument('--region')
parser.add_argument('--ctname')
args = parser.parse_args()

def delete_cloudtrail(name):
    ct_conn = boto.cloudtrail.connect_to_region(region_name=args.region)
    ct_conn.delete_trail(name)

delete_cloudtrail(args.ctname)
