import boto.cloudformation
import boto.ec2
import boto.logs
import argparse
import time
import boto.cloudtrail
import boto.sns
import boto.iam

parser = argparse.ArgumentParser(prog='Attributes Collection')
parser.add_argument('--iamregion')
parser.add_argument('--stackName')
parser.add_argument('--stackAction')
parser.add_argument('--alarmStackName')
args = parser.parse_args()

IamInstalled = 'False'

iam_file = open('create_iam.json')
iam_cfn_body = iam_file.read()
iam_file.close()
alarm_file = open('create_alarms.json')
alarms_cfn_body = alarm_file.read()
alarm_file.close()

cf_conn = boto.cloudformation.connect_to_region(args.iamregion)
ct_conn = boto.cloudtrail.connect_to_region(args.iamregion)
sns_conn = boto.sns.connect_to_region(args.iamregion)
iam_conn = boto.iam.connect_to_region(args.iamregion)
logs_conn = boto.logs.connect_to_region(args.iamregion)

def get_regions():
    try:
        regions = boto.ec2.regions()
        return regions
    except Exception as error:
        print("Error with getting Regions: ****StackTrace: {} ***".format(error))
        return (1)

def create_iam_stack(stack_name, template_body):
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

def create_alarm_stack(stack_name, template_body):
    print("Creating Alarm Stack")
    cf_conn.create_stack(
                       stack_name,
                       template_body,
                       parameters=[
                                   ('AlarmEmail','electronicalias@gmail.com')
                                   ],
                       capabilities=['CAPABILITY_IAM'],
                       tags=None
                       )

def delete_iam_stack(stack_name):
    print("Deleting {} Stack".format(stack_name))
    cf_conn.delete_stack(
                       stack_name
                       )

def get_stack_status(stack_name):
    stacks = cf_conn.describe_stacks(
                                    stack_name
                                    )
    if len(stacks) == 1:
        stack = stacks[0]
    else:
        print ("No stacks found")
    return stack.stack_status

def get_sns_topic():
    try:
        topics = sns_conn.get_all_topics()['ListTopicsResponse']['ListTopicsResult']['Topics']
        for topicname in topics:
            if 'CloudtrailAlerts' in topicname['TopicArn']:
                return topicname['TopicArn']
    except Exception as error:
        print("Error with getting SNS Topics: ****StackTrace: {} ***".format(error))
        return (1)

def get_cloudtrail_trail():
    trail_list = ct_conn.describe_trails()
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

def get_loggroup_arn(logArn):
    cloudtrail_log_arn = logs_conn.describe_log_groups()['logGroups']
    for logGroup in cloudtrail_log_arn:
        if logArn in logGroup['arn']:
            return logGroup['arn']

def configure_trail(name, sns_topic_name, cloud_watch_logs_log_group_arn, cloud_watch_logs_role_arn):
    print name
    print sns_topic_name
    print cloud_watch_logs_log_group_arn
    print cloud_watch_logs_role_arn

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

configure_trail('Default', sns_topic, ct_loggroup_arn, cloudwatch_iam_role)

