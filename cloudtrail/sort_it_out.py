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
parser.add_argument('--iamregion')
parser.add_argument('--stackName')
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
cf_conn = boto.cloudformation.connect_to_region(args.iamregion)
ct_conn = boto.cloudtrail.connect_to_region(args.iamregion)
sns_conn = boto.sns.connect_to_region(args.iamregion)
iam_conn = boto.iam.connect_to_region(args.iamregion)
logs_conn = boto.logs.connect_to_region(args.iamregion)

def get_cloudtrail_regions():
    """ Return list of names of regions where CloudTrail is available """

    cloudtrail_regioninfo_list = boto.regioninfo.get_regions('cloudtrail')
    return [r.name for r in cloudtrail_regioninfo_list]

def create_iam_stack(stack_name, template_body):
    # Create the IAM resources required for CloudTrail
    print("Creating IAM Stack")
    cf_conn.create_stack(
                       stack_name,
                       template_body,
                       parameters=[
                                   ('IamRoleInstalled',IamInstalled)
                                   ],
                       capabilities=['CAPABILITY_IAM'],
                       tags=None
                       )

def create_alarm_stack(region, stack_name, template_body):
    connection = boto.cloudformation.connect_to_region(region)
    # Create the alarms required in CloudWatch, set the SNS Topic and Open SNS Topic Policy
    print("Creating Alarm Stack")
    connection.create_stack(
                       stack_name,
                       template_body,
                       parameters=[
                                   ('AlarmEmail','electronicalias@gmail.com')
                                   ],
                       capabilities=['CAPABILITY_IAM'],
                       tags=None
                       )

def update_alarm_stack(region, stack_name, template_body):
    connection = boto.cloudformation.connect_to_region(region)
    # Update the SNS Policy in the stack to only allow the local account
    print("Creating Alarm Stack")
    connection.update_stack(
                       stack_name,
                       template_body,
                       parameters=[
                                   ('AlarmEmail','electronicalias@gmail.com')
                                   ],
                       capabilities=['CAPABILITY_IAM'],
                       tags=None
                       )

def delete_stack(region, stack_name):
    connection = boto.cloudformation.connect_to_region(region)
    print("Deleting {} Stack".format(stack_name))
    connection.delete_stack(
                       stack_name
                       )

def get_stack_status(region, stack_name):
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
    connection = boto.sns.connect_to_region(region)
    try:
        topics = connection.get_all_topics()['ListTopicsResponse']['ListTopicsResult']['Topics']
        for topicname in topics:
            if 'CloudtrailAlerts' in topicname['TopicArn']:
                return topicname['TopicArn']
    except Exception as error:
        print("Error with getting SNS Topics: ****StackTrace: {} ***".format(error))
        return (1)

def get_cloudtrail_trail():
    connection = boto.cloudtrail.connect_to_region(region, args.iamregion)
    trail_list = connection.describe_trails()
    return trail_list['trailList'][0]['TrailARN']

def get_iam_role(iam_role_name):
    try:
        roles = iam_conn.list_roles()['list_roles_response']['list_roles_result']['roles']
        for role in roles:
            if iam_role_name in role['arn']:
                return role['arn']
    except Exception as error:
        print("Error with getting IAM Role: ****StackTrace: {} ***".format(error))
        return (1)

def get_loggroup_arn(region, logArn):
    connection = boto.logs.connect_to_region(region)
    cloudtrail_log_arn = connection.describe_log_groups()['logGroups']
    for logGroup in cloudtrail_log_arn:
        if logArn in logGroup['arn']:
            return logGroup['arn']

def configure_trail(region, name, s3_bucket_name, s3_key_prefix, sns_topic_name, include_global_service_events, cloud_watch_logs_log_group_arn, cloud_watch_logs_role_arn):
    connection = boto.cloudtrail.connect_to_region(region)
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
        print("Error with configuring CloudTrail: ****StackTrace: {} ***".format(error))
        return (1)
''' Logic has changed, removed section.
if args.stackAction == 'create' and args.iamregion == 'eu-west-1':
    iam_stack = create_iam_stack(args.stackName, iam_cfn_body)
    print "Waiting for the stack to finish creating..."
    while get_stack_status(args.stackName) != 'CREATE_COMPLETE':
        time.sleep(10) 
    print "Stack Created, getting the values for the IAM Role"
elif args.stackAction == 'delete':
    delete_iam_stack(args.stackName)


if args.stackAction == 'create':
    alarm_stack = create_alarm_stack(args.alarmStackName, alarms_cfn_body)
    print("Waiting for the {} stack to finish creating...".format(args.alarmStackName))
    while get_stack_status(args.alarmStackName) != 'CREATE_COMPLETE':
        time.sleep(10)
    print("{} has been successfully created.".format(args.alarmStackName))
elif args.stackAction =='delete':
    delete_iam_stack(args.alarmStackName)

trails = get_cloudtrail_trail()
sns_topic =  get_sns_topic()
cloudwatch_iam_role = get_iam_role(args.stackName + '-CloudwatchLogsRole')
ct_loggroup_arn = get_loggroup_arn(args.alarmStackName + '-CloudTrailLogGroup')
'''

if args.stackAction == 'create':
    print "Creating SNS Policy"
    configure_trail('Default', 'mmc-innovation-centre-logs', 'CloudTrail', 'CloudtrailAlerts', 'True', ct_loggroup_arn, cloudwatch_iam_role)
    print "Policy Created"
    time.sleep(2)
    print "Attempting to update the stack SNS Topic Policy"
    update_alarm_stack(args.alarmStackName, update_sns_cfn_body)

for region in get_cloudtrail_regions():
    if args.stackAction == 'create' and region == args.iamregion:
        iam_stack = create_iam_stack(args.stackName, iam_cfn_body)
        print "Waiting for the stack to finish creating..."
        while get_stack_status(args.stackName) != 'CREATE_COMPLETE':
            time.sleep(10) 
        print "Stack Created, getting the values for the IAM Role"
    if args.stackAction == 'create'
        alarm_stack = create_alarm_stack(region, args.alarmStackName, alarms_cfn_body)
        print("Waiting for the {} stack to finish creating...".format(args.alarmStackName))
        while get_stack_status(region, args.alarmStackName) != 'CREATE_COMPLETE':
            time.sleep(10)
        print("{} has been successfully created.".format(args.alarmStackName))
        trails = get_cloudtrail_trail()
        sns_topic =  get_sns_topic(region)
        cloudwatch_iam_role = get_iam_role(args.stackName + '-CloudwatchLogsRole')
        ct_loggroup_arn = get_loggroup_arn(region, args.alarmStackName + '-CloudTrailLogGroup')
        print "Creating SNS Policy"
        configure_trail(region, 'Default', 'mmc-innovation-centre-logs', 'CloudTrail', 'CloudtrailAlerts', 'True', ct_loggroup_arn, cloudwatch_iam_role)
        time.sleep(2)
        update_alarm_stack(region, args.alarmStackName, update_sns_cfn_body)
    elif args.stackAction == 'delete':
        delete_stack(region, args.alarmStackName)
        delete_stack('eu-west-1', args.stackName)





