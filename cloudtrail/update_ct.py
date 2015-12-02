import boto.cloudtrail

ct_conn = boto.cloudtrail.connect_to_region(region_name='eu-west-1')


def configure_trail(name, s3_bucket_name, s3_key_prefix, sns_topic_name, include_global_service_events, cloud_watch_logs_log_group_arn, cloud_watch_logs_role_arn):
    try:
        ct_conn.update_trail(
            name,
            s3_bucket_name,
            s3_key_prefix,
            sns_topic_name,
            include_global_service_events,
            cloud_watch_logs_log_group_arn,
            cloud_watch_logs_role_arn
            )
    except Exception as error:
        print("Error with configuring CloudTrail: ****StackTrace: {} ***".format(error))
        return (1)

configure_trail('Default', 'mmc-innovation-centre-logs', 'CloudTrail', 'CloudtrailAlerts', 'True', 'arn:aws:logs:eu-west-1:707983519786:log-group:cloudtrail-alarms-CloudTrailLogGroup-BJ3HJO8IO9YO:*', 'arn:aws:iam::707983519786:role/cloudtrail-iams-CloudwatchLogsRole-HDZW9Y4PXDYD')
