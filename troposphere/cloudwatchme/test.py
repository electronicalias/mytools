import boto3
import boto.cloudformation

cfn = boto3.client('cloudformation','ap-southeast-1')
cfn2 = boto.cloudformation.connect_to_region('ap-southeast-1')

stacks = cfn.describe_stacks(
                                    StackName = 'CloudWatch-Alarms'
                                    )
print stacks['Stacks'][0]['StackId']
print len(stacks['Stacks'])
if len(stacks) == 2:
    stack = stacks['Stacks'][0]
else:
    print ("No stacks found")
    #print stack.stack_status
print stack['StackStatus']
