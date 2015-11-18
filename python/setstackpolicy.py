import boto
import boto.cloudformation
import os

boto.set_stream_logger('foo')

status = os.environ.get('PolicyState')
stackName = os.environ.get('ParentStack')
profile = os.environ.get('AuthProfile')
region = os.environ.get('Region')
disable_url='https://s3-eu-west-1.amazonaws.com/gcrebid-deployment/cfn/policies/disable.policy'
enable_url='https://s3-eu-west-1.amazonaws.com/gcrebid-deployment/cfn/policies/enable.policy'

cf_conn = boto.cloudformation.connect_to_region(region, profile_name=profile)

def getStackName(stackName):
# Function to get a Database Stack ID created in a CF stack. Requires the stackname for which you are trying to get the Database Stack from.
    try:
        stackResource=cf_conn.describe_stack_resources(stackName)
        for resource in stackResource:
            if 'Database' in resource.physical_resource_id:
                stackarn = resource.physical_resource_id
                stacksplit = stackarn.split("/")
                stackId = stacksplit[1]
                def test(stackId):
                    try:
                        if 'disable' in status:
                            cf_conn.set_stack_policy(stackId, stack_policy_url=disable_url)
                        elif 'enable' in status:
                            cf_conn.set_stack_policy(stackId, stack_policy_url=enable_url)
                    except Exception as error:
                        print("Error setting the stack_policy for {}. ****Stack Trace: {} ****".format(test,error))
                        return (1)
                test(stackId)
    except Exception as error:
        print("Error when getting information about stack resource {} in stack {}. ****Stack Trace: {} ****".format(stackName,error))
        return (1)

# Here, we query the master stack for the ID of the database stack. We pass this value into the Jenkins job to carry to the next job.
getStackName(stackName)
