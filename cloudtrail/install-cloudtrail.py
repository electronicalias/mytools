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
    if args.iamRegion in region:
        IamInstalled = 'True'
    else:
    	IamInstalled = 'False'
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


def create_alarm_stack(region, stack_name, template_body):
    ''' Create the stack in all cloudtrail regions that turns on the alarms for cloudtrail '''

    connection = boto.cloudformation.connect_to_region(region_name=region)
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
	if args.iamRegion in region:
            create_iam_stack(region, args.iamStackName, iam_cfn_body)
            time.sleep(60)
            create_alarm_stack(region, args.alarmStackName, alarms_cfn_body)
	else:
            iam_role = get_iam_role(args.iamRegion)
            logs_supported = 'True'
            create_alarm_stack(region, args.alarmStackName, alarms_cfn_body)
            time.sleep(60)
