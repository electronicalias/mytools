import boto.cloudtrail
import boto.logs
import argparse
import boto.ec2
import boto.sns
import boto.iam
import boto.cloudformation

parser = argparse.ArgumentParser(prog='Attributes Collection')
parser.add_argument('--region')
parser.add_argument('--status')
parser.add_argument('--profile')
args = parser.parse_args()

iamRoleName = 'CloudwatchLogsRole'
snsTopicName = 'CloudtrailAlerts'
stackName = 'CloudtrailStack'
templateUrl = 'https://some-bucket'


ct_conn = boto.cloudtrail.connect_to_region(args.region, profile_name=args.profile)
logs_conn = boto.logs.connect_to_region(args.region, profile_name=args.profile)
sns_conn = boto.sns.connect_to_region(args.region, profile_name=args.profile)
iam_conn = boto.iam.connect_to_region(args.region, profile_name=args.profile)
s3_conn = boto.s3.connect_to_region(args.region, profile_name=args.profile)
cf_conn = boto.cloudformation.connect_to_region(region, profile_name=profile)

def getRegions():
    try:
        regions = boto.ec2.regions()
        return regions
    except Exception as error:
        print("Error with getting Regions: ****StackTrace: {} ***".format(error))
        return (1)

def getSnsTopics(snsTopicName):
    try:
        topics = sns_conn.get_all_topics()['ListTopicsResponse']['ListTopicsResult']['Topics']
        for topic in topics:
            if snsTopicName in topic['TopicArn']:
               return True
            else:
               return False
        return topics
    except Exception as error:
        print("Error with getting SNS Topics: ****StackTrace: {} ***".format(error))
        return (1)

def getIamRoles(iamRoleName):
    try:
        roles = iam_conn.list_roles()['list_roles_response']['list_roles_result']['roles']
        for role in roles:
            if iamRoleName in role['role_name']:
                return True
            else:
                return False
    except Exception as error:
        print("Error with getting IAM Role: ****StackTrace: {} ***".format(error))
        return (1)

def getStacks(stackName):
    try:
        stacks = cf_conn.list_stacks(stack_status_filters=Active)
    except Exception as error:
        print("Error with getting the Stack List: ****StackTrace: {} ***".format(error))
        return (1)

regions = getRegions()
topics = getSnsTopics(snsTopicName)
roles = getIamRoles(iamRoleName)
stacks = getStacks(stackName)

for region in regions:
    print ("Printing details for: {}".format(region.name))
    print topics
    print stacks



def getstackstatus(stackname):
    stacks = cf_conn.describe_stacks(stackname)
    if len(stacks) == 1:
        stack = stacks[0]
    else:
        print ("No stacks found")
    return stack.stack_status
