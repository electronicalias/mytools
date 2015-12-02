import boto.logs

logs_conn = boto.logs.connect_to_region(region_name='eu-west-1')

cloudtrail_log_arn = logs_conn.describe_log_groups()['logGroups']

for logGroup in cloudtrail_log_arn:
    if 'CloudTrail' in logGroup['arn']:
        print logGroup['arn']
