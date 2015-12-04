import boto.cloudtrail
import argparse

parser = argparse.ArgumentParser(prog='Attributes Collection')
parser.add_argument('--region')
args = parser.parse_args()


def get_cloudtrail_regions():
    """ Return list of names of regions where CloudTrail is available """

    cloudtrail_regioninfo_list = boto.regioninfo.get_regions('cloudtrail')
    return [r.name for r in cloudtrail_regioninfo_list]

def get_cloudtrail_trail(region):
    ct_conn = boto.cloudtrail.connect_to_region(region_name=region)
    trail_list = ct_conn.describe_trails()
    for line in trail_list['trailList']:
        if line == 'None':
            return ("Failed")
        else:
            return trail_list['trailList'][0]['Name']

print(get_cloudtrail_trail(args.region))
