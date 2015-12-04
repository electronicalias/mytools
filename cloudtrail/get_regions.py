import boto.ec2

dir(boto.ec2.regioninfo)

def get_cloudtrail_regions():
    """ Return list of names of regions where CloudTrail is available """

    cloudtrail_regioninfo_list = boto.ec2.regions()
    
    cloudtrail_regioninfo_list.remove('cn-north-1')
    cloudtrail_regioninfo_list.remove('us-gov-west-1')
    return cloudtrail_regioninfo_list

for item in get_cloudtrail_regions():
    print item.name
