'''
Purpose:        This script will assist in turning on Logging for CloudTrail in AWS. Requires an existing bucket.
Creator:        Phil Smith (electronicalias@gmail.com)
Boto Version:   2.38
'''

''' Import required modules '''
import boto.cloudformation
import argparse
import time


''' Collect the command line parameters with 'iamregion' being the account that will keep the logs for CloudTrail '''
parser = argparse.ArgumentParser(prog='Attributes Collection')
parser.add_argument('--iamRegion')
parser.add_argument('--iamStackName')
parser.add_argument('--stackAction')
parser.add_argument('--alarmStackName')
args = parser.parse_args()


''' Read the template bodies:
  create_iam.json to create a role for CloudTrail to use
  create_alarms.json to create the sns topic/policy and the alarms in cloudwatch used to alert for events from CloudTrail
  '''

iam_file = open('create_iam.json')
iam_cfn_body = iam_file.read()
iam_file.close()
alarm_file = open('create_alarms.json')
alarms_cfn_body = alarm_file.read()
alarm_file.close()


def create_iam_stack(region, stack_name, template_body):
    '''Create the IAM resources required for CloudTrail'''
    IamInstalled = 'True'
    cf_conn = boto.cloudformation.connect_to_region(region)
    print("Creating {} Stack in {}".format(stack_name, region))
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


def create_alarm_stack(region, stack_name, template_body, iam_role):
    ''' Create the stack in all cloudtrail regions that turns on the alarms for cloudtrail '''

    connection = boto.cloudformation.connect_to_region(region_name=region)
    # Create the alarms required in CloudWatch, set the SNS Topic and Open SNS Topic Policy
    logs_supported = 'True'
    print("Creating {} Stack in {}".format(stack_name, region))
    try:
        connection.create_stack(
                       stack_name,
                       template_body,
                       parameters=[
                                   ('AlarmEmail','electronicalias@gmail.com'),
                                   ('LogsSupported', logs_supported),
                                   ('IamLogsRole', iam_role)
                                   ],
                       capabilities=['CAPABILITY_IAM'],
                       tags=None
                       )
    except Exception as error:
        print("Error creating {} in region {}: ****StackTrace: {} ***".format(stack_name, region, error))
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


def get_iam_role(region, iamStackName):
    ''' This function gets the IAM Role that is required for CloudTrail to send logs to
    CloudWatch Logs '''
    cf_conn = boto.cloudformation.connect_to_region(region_name=region)
    
    try:
        stacks = cf_conn.describe_stacks(iamStackName)
        if len(stacks) == 1:
            stack = stacks[0]
        for output in stack.outputs:
            return('%s' % (output.value))
    except Exception as error:
        print("Error getting IAM Role: ****StackTrace: {} ***".format(error))
        return (1)



ct_regions = ['eu-west-1', 'ap-southeast-1']

for region in ct_regions:
    if args.iamRegion in region and 'create' == args.stackAction:
        create_iam_stack(region, args.iamStackName, iam_cfn_body)
        while get_stack_status(region, args.iamStackName) != 'CREATE_COMPLETE':
            time.sleep(10)
        iam_role = get_iam_role(args.iamRegion, args.iamStackName)
        create_alarm_stack(region, args.alarmStackName, alarms_cfn_body, iam_role)
        while get_stack_status(region, args.alarmStackName) != 'CREATE_COMPLETE':
            time.sleep(10)
    elif args.iamRegion not in region and 'create' == args.stackAction:
        iam_role = get_iam_role(args.iamRegion, args.iamStackName)
        create_alarm_stack(region, args.alarmStackName, alarms_cfn_body, iam_role)
        while get_stack_status(region, args.alarmStackName) != 'CREATE_COMPLETE':
            time.sleep(10)
    elif args.iamRegion not in region and 'delete' == args.stackAction:
        delete_stack(region, args.alarmStackName)
    elif args.iamRegion in region and 'delete' == args.stackAction:
        delete_stack(region, args.alarmStackName)
        delete_stack(region, args.iamStackName)


