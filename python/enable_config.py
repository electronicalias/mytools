import boto3

# List all regions
client = boto3.client('ec2')
regions = client.describe_regions()['Regions']

def delete_recorder(config,name):
    print("Deleting recorder with incorrect name for: {}".format(name))
    response = config.delete_configuration_recorder(
        ConfigurationRecorderName=name
    )

def clean_config(region):
    config = boto3.client('config',region)
    recorders = config.describe_configuration_recorders()['ConfigurationRecorders']
    if len(recorders) == 0:
        print "No entries found."
    elif 'aws-config' not in recorders[0]['name']:
        print(recorders[0]['name'])
        delete_recorder(config, recorders[0]['name'])

def enable_region(region):
    config = boto3.client('config',region)
    recorder = config.put_configuration_recorder(
        ConfigurationRecorder={
            'name': 'aws-config',
            'roleARN': 'arn:aws:iam::039522162354:role/service-role/kfc-config-role',
            'recordingGroup': {
                'allSupported': True,
                'includeGlobalResourceTypes': True,
            }
        }
    )

    channel = config.put_delivery_channel(
        DeliveryChannel={
            'name': 'default',
            's3BucketName': 'kfc-config',
            'configSnapshotDeliveryProperties': {
                'deliveryFrequency': 'One_Hour'
            }
        }
    )

    state = config.start_configuration_recorder(
        ConfigurationRecorderName='aws-config'
    )

for region in regions:
    print("Enabling Config for: {}".format(region['RegionName']))
    clean_config(region['RegionName'])
    enable_region(region['RegionName'])
