import boto.cloudtrail
import argparse

parser = argparse.ArgumentParser(prog='Attributes Collection')
parser.add_argument('--region')
args = parser.parse_args()


def get_cloudtrail_trail():
    ct_conn = boto.cloudtrail.connect_to_region(region_name=args.region)
    trail_list = ct_conn.describe_trails()
    return trail_list['trailList'][0]['Name']

def create_cloudtrail(name, s3_bucket_name, s3_key_prefix, sns_topic_name, include_global_service_events):
    ct_conn = boto.cloudtrail.connect_to_region(region_name=args.region)
    ct_conn.create_trail(
                name,
                s3_bucket_name,
                s3_key_prefix,
                sns_topic_name,
                include_global_service_events
                )

create_cloudtrail('Default', 'mmc-innovation-centre-logs', 'CloudTrail', 'CloudtrailAlerts', 'True')
