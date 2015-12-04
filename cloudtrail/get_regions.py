import boto.ec2
import boto.logs

def get_regions():
    # Get the list of regions for the loop that will apply the template to each region
    try:
        regions = boto.ec2.regions()
        return regions
    except Exception as error:
        print("Error with getting Regions: ****StackTrace: {} ***".format(error))
        return (1)

def get_cloudtrail_regions():
    """ Return list of names of regions where CloudTrail is available """

    cloudtrail_regioninfo_list = boto.regioninfo.get_regions('logs')
    return [r.name for r in cloudtrail_regioninfo_list]

for region in get_regions():
    print region

for item in get_cloudtrail_regions():
    print item

test = boto.logs.regions()
print test
