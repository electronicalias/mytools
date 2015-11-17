import boto
import boto.cloudformation
import os
import sys

profile=sys.argv[1]
region=sys.argv[2]
stackName=sys.argv[3]

cf_conn = boto.cloudformation.connect_to_region(region, profile_name=profile)


def getStackResource(stackName):
# Function to get a Database Stack ID created in a CF stack. Requires the stackname for which you are trying to get the Database Stack from.
    try:
        stackResource=cf_conn.describe_stack_resources(stackName)
        for resource in stackResource:
            if 'Database' in resource.physical_resource_id:
                stackid = resource.physical_resource_id
                stackname = stackid.split("/")
        return stackname[1]
    except Exception as error:
        print("Error when getting information about stack resource {} in stack {}. ****Stack Trace: {} ****".format(stackName,error))
        return (1)

# Here, we query the master stack for the ID of the database stack. We pass this value into the Jenkins job to carry to the next job.
dbstack = getStackResource(stackName)
