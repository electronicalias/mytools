#!/usr/bin/env pythoA
import datetime
import boto.ec2
import boto.ec2.cloudwatch

ec2 = boto.ec2.connect_to_region('sa-east-1')
cloudwatch = boto.ec2.cloudwatch.connect_to_region('sa-east-1')


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

reservations = ec2.get_all_reservations(filters={"tag:Type" : "HPC", "tag:NodeType" : "compute"})

ave_count = 0
cpu_value = 0

for reservation in reservations:
    for instance in reservation.instances:
        for metric in (metric_series(instance.id)):
            print(metric['Average'])
            cpu_value = cpu_value + metric['Average']
            ave_count = ave_count + 1

print ave_count
print cpu_value
print('The average value of CPU over 100 minutes is: {}'.format(cpu_value / ave_count))


