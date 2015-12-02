import boto.cloudtrail
ct_conn = boto.cloudtrail.connect_to_region(region_name='eu-west-1')

def get_cloudtrail_trail():
    trail_list = ct_conn.describe_trails()
    print trail_list['trailList'][0]['TrailARN']

trails = get_cloudtrail_trail()    
