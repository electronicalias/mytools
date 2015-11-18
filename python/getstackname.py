import boto
import boto.cloudformation
import os

profile='default'
region='eu-west-1'
stackName='uat'

cf_conn = boto.cloudformation.connect_to_region(region, profile_name=profile)


def getStackResource(stackName):
#Function to get a resource ID created in a CF stack. Required Stack Name, and the Name of the Resouce it created.
#Will Return ID of the resource specified or '1' if resource doesnt exist.
    try:
        stackResource=cf_conn.describe_stack_resources(stackName)
        for resource in stackResource:
            if 'Database' in resource.physical_resource_id:
                stackid = resource.physical_resource_id
                stackname = stackid.split("/")
                print stackname[1]
        return stackResource
    except Exception as error:
        print("Error when getting information about stack resource {} in stack {}. ****Stack Trace: {} ****".format(stackName,error))
        return (1)

#Hear, we query the master stack for the ID of the database stack, and then \
# within the same command query the database stack for the RDS Database ID.
# databaseid=getStackResource(getStackResource(stackName,"DatabaseStack"),"RDSDatabase")
getStackResource(stackName)

# Use this to just get the name of the database stack...
#getStackResource(stackName,"DatabaseStack")

# print("DatabaseID is: {}".format(databaseid))
# print("Database Stack name is: {}".format(dbstackname))

#Write the databaseid to a file called database_id, so this can be read in later...
# with open('database_id', 'w') as database_id:
#    database_id.write(databaseid)
