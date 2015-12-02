def configure_trail(name, sns_topic_name, cloud_watch_logs_log_group_arn, cloud_watch_logs_role_arn):
    print name
    print sns_topic_name
    print cloud_watch_logs_log_group_arn
    print cloud_watch_logs_role_arn

configure_trail('Default', 'test', 'something', 'tes12')
