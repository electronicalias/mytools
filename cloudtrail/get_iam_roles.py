import boto.iam
import boto.cloudformation

iam_conn = boto.iam.connect_to_region(region_name='ap-southeast-1')
cf_conn = boto.cloudformation.connect_to_region(region_name='eu-west-1')


def getIamRoles(iamRoleName):
    try:
        roles = iam_conn.list_roles()['list_roles_response']['list_roles_result']['roles']
        for role in roles:
            if iamRoleName in role['arn']:
                return role['arn']
    except Exception as error:
        print("Error with getting IAM Role: ****StackTrace: {} ***".format(error))
        return (1)

print(getIamRoles('CloudwatchLogsRole'))
