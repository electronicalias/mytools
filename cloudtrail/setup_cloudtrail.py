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


ct_conn = boto.cloudtrail.connect_to_region(args.region, profile_name=args.profile)
logs_conn = boto.logs.connect_to_region(args.region, profile_name=args.profile)
sns_conn = boto.sns.connect_to_region(args.region, profile_name=args.profile)
iam_conn = boto.iam.connect_to_region(args.region, profile_name=args.profile)
s3_conn = boto.s3.connect_to_region(args.region, profile_name=args.profile)
cf_conn = boto.cloudformation.connect_to_region(args.region, profile_name=profile)

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

regions = getRegions()
topics = getSnsTopics(snsTopicName)
roles = getIamRoles(iamRoleName)

print roles

for region in regions:
    print ("Printing details for: {}".format(region.name))
    print topics

def updatestack(stack_name, environment, bastian_host_ami, code_base_a, code_base_a_ami, code_base_a_change, code_base_b, code_base_b_ami, code_base_b_change):
  print("Updateing Stack")
  cf_conn.update_stack(
                       stack_name,
                       use_previous_template=True,
                       parameters=[
                                   ('Environment',environment,True),
                                   ('AEnvWebAppAMI',code_base_a_ami,code_base_a_change),
                                   ('BastianHostAMI',bastian_host_ami,True),
                                   ('BEnvWebAppAMI',code_base_b_ami,code_base_b_change),
                                   ('AEnvCodeVersion',code_base_a,code_base_a_change),
                                   ('BEnvCodeVersion',code_base_b,code_base_b_change),
                                   ('DatabasePassword','null',True)
                                   ],
                       capabilities=['CAPABILITY_IAM'],
                       tags=None
                       )

def getstackstatus(stackname):
    stacks = cf_conn.describe_stacks(stackname)
    if len(stacks) == 1:
        stack = stacks[0]
    else:
        print ("No stacks found")
    return stack.stack_status
