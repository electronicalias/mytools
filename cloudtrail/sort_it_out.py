'''
Purpose:        This script will assist in turning on Logging for CloudTrail in AWS. Requires an existing bucket.
Creator:        Phil Smith (electronicalias@gmail.com)
Boto Version:   2.38
'''

# Import all of the modules required to run the  commands in the script
import boto.cloudformation
import boto.ec2
import boto.logs
import argparse
import time
import boto.cloudtrail
import boto.sns
import boto.iam

# Collect the command line parameters with 'iamregion' being the account that will keep the logs for CloudTrail
parser = argparse.ArgumentParser(prog='Attributes Collection')
parser.add_argument('--iamRegion')
parser.add_argument('--iamStackName')
parser.add_argument('--stackAction')
parser.add_argument('--alarmStackName')
args = parser.parse_args()

# Force a condition so that the script will set the condition in the template and ensures CloudFormation will run
IamInstalled = 'False'

# Read the template bodies:
#  create_iam.json to create a role for CloudTrail to use
#  create_alarms.json to create the sns topic/policy and the alarms in cloudwatch used to alert for events from CloudTrail
#  update_sns_policy.json is required to set security on the SNS Policy after it has been attached to CloudTrail
iam_file = open('create_iam.json')
iam_cfn_body = iam_file.read()
iam_file.close()
alarm_file = open('create_alarms.json')
alarms_cfn_body = alarm_file.read()
alarm_file.close()
update_sns_file = open('update_sns_policy.json')
update_sns_cfn_body = update_sns_file.read()
update_sns_file.close()

# Create connections to all of the services
cf_conn = boto.cloudformation.connect_to_region(args.iamRegion)
ct_conn = boto.cloudtrail.connect_to_region(args.iamRegion)
sns_conn = boto.sns.connect_to_region(args.iamRegion)
iam_conn = boto.iam.connect_to_region(args.iamRegion)
logs_conn = boto.logs.connect_to_region(args.iamRegion)

''' Set up the functions required to provide the information necessary for the
    CloudTrail configuration to point to CloudWatch Logs and the global S3 Bucket '''

def get_cloudtrail_regions():
    """ Return list of names of regions where CloudTrail is available """

    cloudtrail_regioninfo_list = boto.regioninfo.get_regions('cloudtrail')
    return [r.name for r in cloudtrail_regioninfo_list]


def get_logs_regions():
    """ Return list of names of regions where CloudTrail is available """

    cloudtrail_regioninfo_list = boto.regioninfo.get_regions('logs')
    return [r.name for r in cloudtrail_regioninfo_list]


def create_iam_stack(stack_name, template_body):
    '''Create the IAM resources required for CloudTrail'''

    print("Creating {} Stack in {}".format(stack_name, args.iamRegion))
    try:
        cf_conn.create_stack(
                       stack_name,
                       template_body,
                       parameters=[
                                   ('IamRoleInstalled',IamInstalled)
                                   ],
                       capabilities=['CAPABILITY_IAM'],
                       tags=None
                       )
    except Exception as error:
        print("Error creating {}: ****StackTrace: {} ***".format(stack_name, error))
        return (1)


def create_alarm_stack(region, stack_name, template_body):
    ''' Create the stack in all cloudtrail regions that turns on the alarms for cloudtrail '''

    if region in get_logs_regions():
        logs_supported = 'True'
    else:
        logs_supported = 'False'

    connection = boto.cloudformation.connect_to_region(region)
    # Create the alarms required in CloudWatch, set the SNS Topic and Open SNS Topic Policy
    print("Creating {} Stack in {}".format(stack_name, region))
    try:
        connection.create_stack(
                       stack_name,
                       template_body,
                       parameters=[
                                   ('AlarmEmail','electronicalias@gmail.com'),
                                   ('LogsSupported', logs_supported)
                                   ],
                       capabilities=['CAPABILITY_IAM'],
                       tags=None
                       )
    except Exception as error:
        print("Error creating {} in region {}: ****StackTrace: {} ***".format(stack_name, region, error))
        return (1)


def update_alarm_stack(region, stack_name, template_body):
    ''' Update stack is required to update the SNS Topic Policy after the link to it from CloudTrail
    has been made '''

    connection = boto.cloudformation.connect_to_region(region)
    # Update the SNS Policy in the stack to only allow the local account
    print("Creating {} Stack in {}".format(stack_name, region))
    try:
        connection.update_stack(
                       stack_name,
                       template_body,
                       parameters=[
                                   ('AlarmEmail','electronicalias@gmail.com')
                                   ],
                       capabilities=['CAPABILITY_IAM'],
                       tags=None
                       )
    except Exception as error:
        print("Error updating {} in {}: ****StackTrace: {} ***".format(stack_name, region, error))
        return (1)


def delete_stack(region, stack_name):
    ''' This is used to clean up from within the script, this leaves logging on and doesn't
    reconfigure cloudtrail, so there will be a role left in cloudtrail '''

    connection = boto.cloudformation.connect_to_region(region)
    print("Deleting {} Stack".format(stack_name))
    try:
        connection.delete_stack(
                       stack_name
                       )
        print("Deleted {} Stack in {}".format(stack_name, region))
    except Exception as error:
        print("Error deleting {} in {}: ****StackTrace: {} ***".format(stack_name, region, error))
        return (1)


def get_stack_status(region, stack_name):
    ''' This is required to create a wait condition in the script while the stack is
    creating before the script then tries to read the stack attributes'''

    connection = boto.cloudformation.connect_to_region(region)
    stacks = connection.describe_stacks(
                                    stack_name
                                    )
    if len(stacks) == 1:
        stack = stacks[0]
    else:
        print ("No stacks found")
    return stack.stack_status


def get_sns_topic(region):
    ''' This is required for setting the Topic on the CloudTrail (Default Entry) '''

    connection = boto.sns.connect_to_region(region)
    try:
        topics = connection.get_all_topics()['ListTopicsResponse']['ListTopicsResult']['Topics']
        for topicname in topics:
            if 'CloudtrailAlerts' in topicname['TopicArn']:
                return topicname['TopicArn']
    except Exception as error:
        print("Error getting SNS Topics in {}: ****StackTrace: {} ***".format(region, error))
        return (1)


def get_cloudtrail_arn(region):
    ''' This is required for the configuration of the CloudTrail settings, in particular
    this script get's the arn for the trail to provide to the later function '''

    connection = boto.cloudtrail.connect_to_region(region)
    try:
        trail_list = connection.describe_trails()
        return trail_list['trailList'][0]['TrailARN']
    except Exception as error:
        print("Error describing trails in {}: ****StackTrace: {} ***".format(region, error))
        return (1)


def get_cloudtrail_name(region):

    ct_conn = boto.cloudtrail.connect_to_region(region)
    trail_list = ct_conn.describe_trails()
    if trail_list > 0:
        return trail_list['trailList'][0]['Name']
    else:
        return 'NoValue'


def delete_cloudtrail(name, region):
    ct_conn = boto.cloudtrail.connect_to_region(region)
    ct_conn.delete_trail(name)


def get_iam_role(iam_role_name):
    ''' This function gets the IAM Role that is required for CloudTrail to send logs to
    CloudWatch Logs '''

    try:
        roles = iam_conn.list_roles()['list_roles_response']['list_roles_result']['roles']
        for role in roles:
            if iam_role_name in role['arn']:
                return role['arn']
    except Exception as error:
        print("Error getting IAM Role: ****StackTrace: {} ***".format(error))
        return (1)


def get_loggroup_arn(region, logArn):
    ''' This function is required to get the Log Group ARN to provide to the CloudTrail
    configuration '''

    connection = boto.logs.connect_to_region(region)
    try:
        cloudtrail_log_arn = connection.describe_log_groups()['logGroups']
        for logGroup in cloudtrail_log_arn:
            if 'CloudTrailLogGroup' in logGroup['arn']:
                return logGroup['arn']
    except Exception as error:
        print("Error getting LogGroup Name in {}: ****StackTrace: {} ***".format(region, error))
        return (1)

def configure_trail(region, name, s3_bucket_name, s3_key_prefix, sns_topic_name, include_global_service_events, cloud_watch_logs_log_group_arn, cloud_watch_logs_role_arn, action):
    ''' This function is required for setting the CloudTrail configuration and points the
    Logs function at the CloudWatch LogGroup, it appears that this cannot be carried out
    unless there are sufficient privileges on the SNS Topic Policy, unfortunately that 
    leaves the topic open to anyone to publish, the subsequent CloudFormation update should
    replace the open policy and prevent non-approved publsh actions, however this doesn't work
    as expected '''

    connection = boto.cloudtrail.connect_to_region(region)
    
    if 'update' in action:
        try:
            connection.update_trail(
                name,
                s3_bucket_name,
                s3_key_prefix,
                sns_topic_name,
                include_global_service_events,
                cloud_watch_logs_log_group_arn,
                cloud_watch_logs_role_arn
                )
        except Exception as error:
            print("Error configuring CloudTrail in {}: ****StackTrace: {} ***".format(region, error))
            return (1)

    elif 'create' in action:
        try:
            connection.create_trail(
                name,
                s3_bucket_name,
                s3_key_prefix,
                sns_topic_name,
                include_global_service_events,
                cloud_watch_logs_log_group_arn,
                cloud_watch_logs_role_arn
                )
        except Exception as error:
            print("Error configuring CloudTrail in {}: ****StackTrace: {} ***".format(region, error))
            return (1)

    elif 'nologs' in action:
        try:
            connection.create_trail(
                name,
                s3_bucket_name,
                s3_key_prefix,
                sns_topic_name,
                include_global_service_events
                )
        except Exception as error:
            print("Error configuring CloudTrail in {}: ****StackTrace: {} ***".format(region, error))
            return (1)

    elif 'recreatenologs' in action:
        try:
            connection.update_trail(
                name,
                s3_bucket_name,
                s3_key_prefix,
                sns_topic_name,
                include_global_service_events
                )
        except Exception as error:
            print("Error configuring CloudTrail in {}: ****StackTrace: {} ***".format(region, error))
            return (1)


if args.stackAction == 'create':
    iam_stack = create_iam_stack(args.iamStackName, iam_cfn_body)
    print("Waiting for the {} Stack in {} to finish creating...".format(args.iamStackName, args.iamRegion))
    while get_stack_status(args.iamRegion, args.iamStackName) != 'CREATE_COMPLETE':
        time.sleep(10) 
    print("{} Stack created".format(args.iamStackName))
elif args.stackAction == 'delete':
            delete_stack(args.iamRegion, args.iamStackName)

ct_regions = get_cloudtrail_regions()

for ct_region in ct_regions:
    if args.stackAction == 'create':
        create_alarm_stack(ct_region, args.alarmStackName, alarms_cfn_body)
        print("Waiting for the {} Stack in {} to finish creating...".format(args.alarmStackName, ct_region))
        while get_stack_status(ct_region, args.alarmStackName) != 'CREATE_COMPLETE':
            time.sleep(10)
        print("{} Stack has been successfully created in {} with final status of: {}".format(args.alarmStackName, ct_region, get_stack_status(ct_region, args.alarmStackName)))
        time.sleep(20)
        trails = get_cloudtrail_arn(ct_region)
        sns_topic =  get_sns_topic(ct_region)
        cloudwatch_iam_role = get_iam_role(args.iamStackName + '-CloudwatchLogsRole')

        if ct_region in get_logs_regions():
            ct_loggroup_arn = get_loggroup_arn(ct_region, args.alarmStackName + '-CloudTrailLogGroup')

        print("Creating SNS Policy for {}".format(ct_region))


        if ct_region in get_logs_regions():
            if 'Default' not in get_cloudtrail_name(ct_region):
                delete_cloudtrail(ct_region, ct_region)
                configure_trail(ct_region, 'Default', 'mmc-innovation-centre-logs', 'CloudTrail', 'CloudtrailAlerts', 'True', ct_loggroup_arn, cloudwatch_iam_role, 'create')
                time.sleep(2)

            elif 'Default' in get_cloudtrail_name(ct_region):
                configure_trail(ct_region, 'Default', 'mmc-innovation-centre-logs', 'CloudTrail', 'CloudtrailAlerts', 'True', ct_loggroup_arn, cloudwatch_iam_role, 'update')
                time.sleep(2)
        else:
            if 'Default' not in get_cloudtrail_name(ct_region):
                delete_cloudtrail(ct_region, ct_region)
                configure_trail(ct_region, 'Default', 'mmc-innovation-centre-logs', 'CloudTrail', 'CloudtrailAlerts', 'True', 'NONE', 'NONE', 'recreatenologs')
                time.sleep(2)

            elif 'NoValue' in get_cloudtrail_name(ct_region):
                configure_trail(ct_region, 'Default', 'mmc-innovation-centre-logs', 'CloudTrail', 'CloudtrailAlerts', 'True', 'NONE', 'NONE', 'recreatenologs')
                time.sleep(2)

            elif 'Default' in get_cloudtrail_name(ct_region):
                configure_trail(ct_region, 'Default', 'mmc-innovation-centre-logs', 'CloudTrail', 'CloudtrailAlerts', 'True', 'NONE', 'NONE', 'nologs')
                time.sleep(2)



        print("Updating {} in {}".format(args.alarmStackName, ct_region))
        # update_alarm_stack(ct_region, args.alarmStackName, update_sns_cfn_body)
        trails = ''
        sns_topic = ''
        cloudwatch_iam_role = ''
        ct_loggroup_arn = ''
        ct_region = ''
    elif args.stackAction == 'delete':
        delete_stack(ct_region, args.alarmStackName)
        ct_region = ''
