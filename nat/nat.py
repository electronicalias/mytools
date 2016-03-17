#!/usr/env/bin python
''' 
This script only works with:
boto3 == 1.2.6
'''

''' Import Modules '''
import urllib2
import argparse
import cmd
import syslog

InstanceId = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read()
AvailabilityZone = urllib2.urlopen('http://169.254.169.254/latest/meta-data/placement/availability-zone').read()
LocalIp = urllib2.urlopen('http://169.254.169.254/latest/meta-data/local-ipv4').read()
if AvailabilityZone.endswith('a'):
    PeerAz = str(AvailabilityZone[:-1] + 'b')
elif AvailabilityZone.endswith('b'):
    PeerAz = str(AvailabilityZone[:-1] + 'a')

''' Setup the Command Line to accept the variables required '''
parser = argparse.ArgumentParser(
    prog='Nat Updater',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    This program is used to re-attach the EIP and set the source-dest-check to false so this instance can take over
    the NAT function.
    ''')
parser.add_argument('-a','--allocation_id', required=True)
parser.add_argument('-r','--region_name', required=True)
parser.add_argument('-v','--vpc_id', required=True)
arg = parser.parse_args()

def state_check(host):
    try:
        response = urllib2.urlopen(str('http://' + host + '/index.html')).read()
        return response
    except:
    	return str('FAIL')

aws = cmd.aws(arg.region_name)
shell = cmd.bash()

''' First thing to do as an action is to set source/dest to False because this will be a NAT instance '''
aws.source_dest(InstanceId)
PeerId = aws.get_peer(PeerAz,'nat',arg.vpc_id)
PeerIp = aws.instance_ip(PeerId)

''' Get the status of our health (the ability to get to 3 public URLs) using the status.py script '''
LocalState = state_check(LocalIp)
PeerState = state_check(PeerIp)

for table in aws.get_rt_tables(arg.vpc_id,'private'):
    print("Getting the table")
    table_id = aws.get_table_id(table)
    for route in table_id.routes:
        print("Going through the routes")
        default = 'NoValue'
        if 'locked' in aws.get_tag(InstanceId):
            print("I was locked so I broke out")
            break
        elif '0.0.0.0' in (route.get('DestinationCidrBlock', default)):
            print("Found a 0.0.0.0 route")
            if 'blackhole' in route.get('State'):
                print("Has black hole, will set to myself then break")
                aws.associate_eip(InstanceId,arg.allocation_id)
                shell.cmd(str('/usr/bin/aws ec2 replace-route --route-table-id ' + table_id.route_table_id + ' --destination-cidr-block 0.0.0.0/0 --instance-id ' + InstanceId + ' --region ' + arg.region_name))
                aws.set_tag(InstanceId,'active')
                syslog.syslog(str('Moved NAT due to BlackHole in the route, to: ' + InstanceId))    
                break    
            DestBlock = route.get('DestinationCidrBlock')
            print PeerId
            print PeerIp
            print state_check(PeerIp)
            print route.get('InstanceId')
            if PeerId in route.get('InstanceId') and 'OK' in state_check(PeerIp):
                print("Checking remote peer, if found will set standby")
                syslog.syslog(str('Healthcheck OK and Route owned by: ' + PeerId))
                aws.set_tag(InstanceId,'standby')
            elif InstanceId in route.get('InstanceId') and 'OK' in state_check(LocalIp):
                print("other server not active, I am active, I am route, I am router")
                syslog.syslog(str('Healthcheck OK and Route owned by: ' + InstanceId))
            elif InstanceId not in route.get('InstanceId') and PeerId not in route.get('PeerId'):
                print("NoValue found for either myself or peer in the route table, something is wrong!")
                if 'active' in aws.get_tag(PeerId) and 'new' in aws.get_tag(InstanceId):
                    print("Active was in peer, standby was in myself")
                    syslog.syslog('I am Standby, setting tag to Standby')
                    aws.set_tag(InstanceId,'standby')
                    aws.set_tag(PeerId,'active')
                elif 'active' not in aws.get_tag(PeerId) and 'new' in aws.get_tag(InstanceId):
                    aws.set_tag(PeerId,'locked')
                    aws.associate_eip(InstanceId,arg.allocation_id)
                    shell.cmd(str('/usr/bin/aws ec2 replace-route --route-table-id ' + table_id.route_table_id + ' --destination-cidr-block 0.0.0.0/0 --instance-id ' + InstanceId + ' --region ' + arg.region_name))
                    aws.set_tag(InstanceId,'active')
                    aws.set_tag(PeerId,'standby')
            	elif 'active' not in aws.get_tag(InstanceId) and 'active' not in aws.get_tag(PeerId):
                    aws.set_tag(PeerId,'locked')
                    syslog.syslog(str('Neither instance has the route, taking EIP/Route and assigning to: ' + InstanceId))
                    aws.associate_eip(InstanceId,arg.allocation_id)
                    shell.cmd(str('/usr/bin/aws ec2 replace-route --route-table-id ' + table_id.route_table_id + ' --destination-cidr-block 0.0.0.0/0 --instance-id ' + InstanceId + ' --region ' + arg.region_name))
                    syslog.syslog(str('Moved NAT to: ' + InstanceId))
                    aws.set_tag(PeerId,'standby')
                    syslog.syslog(str('Set standby to: ' + PeerId))


