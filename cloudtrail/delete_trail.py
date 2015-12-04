import boto.cloudtrail
import argparse

parser = argparse.ArgumentParser(prog='Attributes Collection')
parser.add_argument('--region')
args = parser.parse_args()


def get_cloudtrail_trail():
    ct_conn = boto.cloudtrail.connect_to_region(region_name=args.region)
    trail_list = ct_conn.describe_trails()
    return trail_list['trailList'][0]['Name']

def delete_cloudtrail(name):
    ct_conn = boto.cloudtrail.connect_to_region(region_name=args.region)
    ct_conn.delete_trail(name)

if args.region in get_cloudtrail_trail():
    delete_cloudtrail(args.region)
