import boto.cloudformation
import boto.ec2
import argparse
import time
import boto.cloudtrail
import boto.sns

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

def getRegions():
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

def getSnsTopics():
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

def get_iam_role(stack_name):
  iam_role = cf_conn.describe_stack_resource(stack_name, 'CloudwatchLogsRole')['DescribeStackResourceResponse']['DescribeStackResourceResult']['StackResourceDetail']['LogicalResourceId']
  return iam_role

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
    if len(iam_role) > 0:
        alarm_stack = create_alarm_stack(args.alarmStackName, alarms_cfn_body)
        print("Waiting for the {} stack to finish creating...".format(args.alarmStackName))
        while get_stack_status(args.alarmStackName) != 'CREATE_COMPLETE':
            time.sleep(10)
        print("{} has been successfully created.".format(args.alarmStackName))
    else:
        print "NoooooooOOOOOooOOOoOOOOo!"
elif args.stackAction =='delete':
    delete_iam_stack(args.alarmStackName)

trails = get_cloudtrail_trail()
print trails

sns_topics =  getSnsTopics()
print sns_topics

cloudwatch_iam_role = get_iam_role(stackName)
print cloudwatch_iam_role

