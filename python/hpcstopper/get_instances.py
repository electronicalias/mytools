#!/usr/bin/env pythoA
import argparse
import datetime
import boto.ec2
import boto.ec2.cloudwatch

parser = argparse.ArgumentParser(
    prog='HPC_OPTIMIZER',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    Welcoe to the HPC Cluster Optimizer, this optimizer works on the basis that you are using a tag called 'Usage', the value of which
    can be used to query running instances to see if they have finished processing. If they have it will stop the instances.
    ''')
parser.add_argument('-rgn','--region_name', required=True)
parser.add_argument('-tag','--tag_name', required=True)
arg = parser.parse_args()

region = arg.region_name
tag = arg.tag_name

ec2 = boto.ec2.connect_to_region(region)
cloudwatch = boto.ec2.cloudwatch.connect_to_region(region)


def metric_series(instance_id):
    metric = cloudwatch.get_metric_statistics(
        '300',
        datetime.datetime.utcnow() - datetime.timedelta(seconds=1800),
        datetime.datetime.utcnow(),
        'CPUUtilization',
        'AWS/EC2',
        'Average',
        dimensions={'InstanceId':instance_id},
        unit='Percent'
    )
    return metric

reservations = ec2.get_all_reservations(filters={'instance-state-name': 'running', 'tag:Usage' : tag})

ave_count = 0
cpu_value = 0

for reservation in reservations:
    for instance in reservation.instances:
        for metric in (metric_series(instance.id)):
            cpu_value = cpu_value + metric['Average']
            ave_count = ave_count + 1

average = cpu_value / ave_count

print('The average value of CPU over 30 minutes is: {}'.format(average))

if average < 10:
    print "We're all going to die!!"
else:
    print "Still processing!!"

cloudwatch.put_metric_data(
    'HPC',
    'CPU',
    value = average,
    timestamp = datetime.datetime.utcnow(),
    unit = 'Percent'
    )
