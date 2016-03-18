#!/usr/env/bin python
''' 
This script only works with:
boto3 == 1.2.6

This dependency is deployed by the CloudFormation script that accompanies this program. The solution supports mulitple AZs and
subnets provided they are tagged correctly as follows:

Key				Value
Application		[some app name]
Zone 			[a zone name you choose]
Type 			[private, or some other indicator]
Location 		[used to differentiate between multiple VPCs running this stack - insert VPC Id]

The solution uses 2 EC2 instances each provisioned by their own Auto-Scaling group. 
'''

# Import Modules
import urllib2 		# Used for testing URLs in the healthcheck
import argparse 	# Used for collecitng command line params
import cmd 			# Module created for interacting with AWS and the shell
import syslog 		# Will be deprecated for logging instead
import logging		# Used to save all log activity for NAT

logging.basicConfig(filename='/var/log/nat.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')

# Get the AWS Instance ID from the local meta-data and set the variable (requires urllib2)
LocalInstanceId = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read()
# Get the AWS Availability Zone that this instance is provisioned into from the local meta-data
# (requires urllib2)
AvailabilityZone = urllib2.urlopen('http://169.254.169.254/latest/meta-data/placement/availability-zone').read()
# Get the Local IP from the local metadata (requires urllib2)
LocalIp = urllib2.urlopen('http://169.254.169.254/latest/meta-data/local-ipv4').read()

''' This statement will work out the other AZ which is how we find our PeerId and PeerIp to know
if we are running a fault tolerant NAT soltion. '''
if AvailabilityZone.endswith('a'):
    PeerAz = str(AvailabilityZone[:-1] + 'b')
elif AvailabilityZone.endswith('b'):
    PeerAz = str(AvailabilityZone[:-1] + 'a')

logging.info('PeerAz=%s', PeerAz)

''' Setup the Command Line to accept the variables:

Key				Value
allocation_id   [The value of the EIP you wish to assign to this stack]
region_name		[The region for which this is being provisioned into]
vpc_id			[The VPC where this is being deployed]
'''
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

logging.info('Running NAT HA with the following: Allocation ID = %s, Region = %s, VpcId = %s', arg.allocation_id, arg.region_name, arg.vpc_id)

''' Setup Class Commands from the cmd class '''
aws = cmd.aws(arg.region_name)
shell = cmd.bash()
hc = cmd.state()

''' First thing to do as an action is to set source/dest to False because this will be a NAT instance '''
aws.source_dest(LocalInstanceId)

''' Find out what we can about our NAT Peer '''
Peer = aws.get_instance(PeerAz,'nat',arg.vpc_id)
PeerId = Peer.get('Id', None)
print PeerId
PeerAwsState = Peer.get('State', {}).get('Name', None)
print PeerAwsState


''' Get the status of our health (the ability to get to 3 public URLs) using the status.py script '''
LocalHcState = hc.check_ha(LocalIp)

for table in aws.get_rt_tables(arg.vpc_id,'private'):
    print("Getting the table")
    table_id = aws.get_table_id(table)
    for route in table_id.routes:
        default = 'NoValue'
        if 'locked' in aws.get_tag(LocalInstanceId):
            print("I was locked so I broke out")
            break
        elif '0.0.0.0' in (route.get('DestinationCidrBlock', default)):
            print("Found a 0.0.0.0 route")
            if 'blackhole' in route.get('State'):
                print("Has black hole, will set to myself then break")
                aws.associate_eip(LocalInstanceId,arg.allocation_id)
                shell.cmd(str('/usr/bin/aws ec2 replace-route --route-table-id ' + table_id.route_table_id + ' --destination-cidr-block 0.0.0.0/0 --instance-id ' + LocalInstanceId + ' --region ' + arg.region_name))
                aws.set_tag(LocalInstanceId,'active')
                syslog.syslog(str('Moved NAT due to BlackHole in the route, to: ' + LocalInstanceId))    
                break 
            elif 'running' not in PeerAwsState and 'failed' not in aws.get_tag(LocalInstanceId):
                print("Peer is currently failing, I should take routes!")
                aws.set_tag(PeerId,'failed')
                aws.associate_eip(LocalInstanceId,arg.allocation_id)
                shell.cmd(str('/usr/bin/aws ec2 replace-route --route-table-id ' + table_id.route_table_id + ' --destination-cidr-block 0.0.0.0/0 --instance-id ' + LocalInstanceId + ' --region ' + arg.region_name))
                aws.set_tag(LocalInstanceId,'active')
                syslog.syslog(str('Moved NAT due to no Peer Available: ' + LocalInstanceId))    
                break 
            DestBlock = route.get('DestinationCidrBlock')
            if PeerId in route.get('InstanceId') and 'active' in aws.get_tag(LocalInstanceId):
                print("Checking remote peer, if found will set standby")
                syslog.syslog(str('Healthcheck OK and Route owned by: ' + PeerId))
                aws.set_tag(LocalInstanceId,'standby')
            elif LocalInstanceId in route.get('InstanceId') and 'OK' in LocalHcState:
                print("other server not active, I am active, I am route, I am router")
                syslog.syslog(str('Healthcheck OK and Route owned by: ' + LocalInstanceId))
            elif LocalInstanceId not in route.get('InstanceId') and PeerId not in route.get('InstanceId'):
                print("NoValue found for either myself or peer in the route table, something is wrong!")
                if 'active' in aws.get_tag(PeerId) and 'new' in aws.get_tag(LocalInstanceId):
                    print("Active was in peer, standby was in myself")
                    syslog.syslog('I am Standby, setting tag to Standby')
                    aws.set_tag(LocalInstanceId,'standby')
                    aws.set_tag(PeerId,'active')
                elif 'active' not in aws.get_tag(PeerId) and 'new' in aws.get_tag(LocalInstanceId):
                    print("Active not in Peer State, New in LocalState")
                    aws.set_tag(PeerId,'locked')
                    aws.associate_eip(LocalInstanceId,arg.allocation_id)
                    shell.cmd(str('/usr/bin/aws ec2 replace-route --route-table-id ' + table_id.route_table_id + ' --destination-cidr-block 0.0.0.0/0 --instance-id ' + LocalInstanceId + ' --region ' + arg.region_name))
                    aws.set_tag(LocalInstanceId,'active')
                    aws.set_tag(PeerId,'standby')
            	elif 'active' not in aws.get_tag(LocalInstanceId) and 'active' not in aws.get_tag(PeerId):
            	    print("Active not in LocalState, Active not in PeerState")
                    aws.set_tag(PeerId,'locked')
                    syslog.syslog(str('Neither instance has the route, taking EIP/Route and assigning to: ' + LocalInstanceId))
                    aws.associate_eip(LocalInstanceId,arg.allocation_id)
                    shell.cmd(str('/usr/bin/aws ec2 replace-route --route-table-id ' + table_id.route_table_id + ' --destination-cidr-block 0.0.0.0/0 --instance-id ' + LocalInstanceId + ' --region ' + arg.region_name))
                    syslog.syslog(str('Moved NAT to: ' + LocalInstanceId))
                    aws.set_tag(PeerId,'standby')
                    syslog.syslog(str('Set standby to: ' + PeerId))
