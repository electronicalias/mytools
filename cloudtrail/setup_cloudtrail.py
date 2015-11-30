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
stackName = 'cloudtrail-stack'
templateUrl = 'https://some-bucket'


ct_conn = boto.cloudtrail.connect_to_region(args.region, profile_name=args.profile)
logs_conn = boto.logs.connect_to_region(args.region, profile_name=args.profile)
sns_conn = boto.sns.connect_to_region(args.region, profile_name=args.profile)
iam_conn = boto.iam.connect_to_region(args.region, profile_name=args.profile)
s3_conn = boto.s3.connect_to_region(args.region, profile_name=args.profile)
cf_conn = boto.cloudformation.connect_to_region(args.region, profile_name=args.profile)

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
        stacks = cf_conn.describe_stack_resources(stackName)
    except Exception as error:
        return (1)

regions = getRegions()
topics = getSnsTopics(snsTopicName)
roles = getIamRoles(iamRoleName)
stacks = getStacks(stackName)

def isStackAvailable(stacks):
    try:
        if stacks != 0:
            return False
        else:
            return True
    except Exception as error:
        print("Error with getting IAM Role: ****StackTrace: {} ***".format(error))
        return (1)

if isStackAvailable(stacks) != False:
    print("The stack exists, please manually delete the stack before preceding: {}".format(isStackAvailable(stacks)))
else:
    print("Current cloudtrail-stack status: {}".format(isStackAvailable(stacks)))
    if getIamRoles(iamRoleName) != False:
        print("Should be true: {}".format(getIamRoles(iamRoleName)))
    else:
        print("Current status of the IAM Role for cloudtrail cloudwatch logs: {}".format(getIamRoles(iamRoleName)))
        if getSnsTopics(snsTopicName) != False:
            print("SNS Topic already exists")
        else:
            print("Current status of the SNS Topic for cloudtrail alerts: {}".format(getSnsTopics(snsTopicName))) 
            print "Creating cloudtrail-logs stack"
            def createCtStack():
                try:
                    print "I WOULD LOVE TO INSTALL A STACK PLEASE!"
                except Exception as error:
                    print("Error with getting IAM Role: ****StackTrace: {} ***".format(error))
                    return (1)
            createCtStack()


