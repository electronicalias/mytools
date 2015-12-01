import boto.cloudformation
import argparse
import time

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

if args.stackAction == 'create' and args.iamregion == 'eu-west-1':
    iam_stack = create_iam_stack(args.stackName, iam_cfn_body)
    print "Waiting for the stack to finish creating..."
    while get_stack_status(args.stackName) != 'CREATE_COMPLETE':
        time.sleep(10) 
    print "Stack Created, getting the values for the IAM Role"
    iam_role = cf_conn.describe_stack_resource(args.stackName, 'CloudwatchLogsRole')['DescribeStackResourceResponse']['DescribeStackResourceResult']['StackResourceDetail']['PhysicalResourceId']
    print iam_role
elif args.stackAction == 'delete':
    delete_iam_stack(args.stackName)

''' some multilineer 
that doesn't do this
ever '''
if args.stackAction == 'create':
    if len(iam_role) > 0:
        alarm_stack = create_alarm_stack(args.alarmStackName, alarms_cfn_body)
    else:
        print "NoooooooOOOOOooOOOoOOOOo!"
elif args.stackAction =='delete':
    delete_iam_stack(args.alarmStackName)

