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
import logging		# Used to save all log activity for NAT, logs are found at /var/log/nat.log

logging.basicConfig(filename='/var/log/nat.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')
logging.info('\n')
logging.info('Starting Logging for nat.py')

# Get the AWS Instance ID from the local meta-data and set the variable (requires urllib2)
LocalInstanceId = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read()
# Get the AWS Availability Zone that this instance is provisioned into from the local meta-data
# (requires urllib2)
AvailabilityZone = urllib2.urlopen('http://169.254.169.254/latest/meta-data/placement/availability-zone').read()
# Get the Local IP from the local metadata (requires urllib2)
LocalIp = urllib2.urlopen('http://169.254.169.254/latest/meta-data/local-ipv4').read()

''' This statement will work out the other AZ which is how we find our PeerId and PeerIp to know
if we are running a fault tolerant NAT soltion. '''
#if AvailabilityZone.endswith('a'):
#    PeerAz = str(AvailabilityZone[:-1] + 'b')
#elif AvailabilityZone.endswith('b'):
#    PeerAz = str(AvailabilityZone[:-1] + 'a')

#logging.info('PeerAz=%s', PeerAz)

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

logging.info('Running NAT HA with the following:\nAllocation ID = %s\nRegion = %s\nVpcId = %s', arg.allocation_id, arg.region_name, arg.vpc_id)

''' Setup Class Commands from the cmd class '''
aws = cmd.aws(arg.region_name)
shell = cmd.bash()
hc = cmd.state()


''' First thing to do as an action is to set source/dest to False because this will be a NAT instance '''
aws.source_dest(LocalInstanceId)

''' Find out what we can about our NAT Peer '''
def get_peer_az():
    PeerAz = aws.get_peer_az(arg.vpc_id,LocalInstanceId)
    return PeerAz
def get_peer():
    Peer = aws.get_instance(get_peer_az(),'nat',arg.vpc_id)
    return Peer
def get_peer_id():
    PeerId = get_peer().get('Id', None)
    return PeerId
def get_peer_state():
    PeerAwsState = get_peer().get('State', {}).get('Name', None)
    return PeerAwsState

def set_active(local_id,remote_id,table_id):
    aws.set_tag(local_id,'locked')
    aws.associate_eip(local_id,arg.allocation_id)
    shell.cmd(str('/usr/bin/aws ec2 replace-route --route-table-id ' + table_id + ' --destination-cidr-block 0.0.0.0/0 --instance-id ' + local_id + ' --region ' + arg.region_name))
    aws.set_tag(local_id,'active')
    aws.set_tag(remote_id,'active') 

''' Get the status of our health (the ability to get to 3 public URLs) using the status.py script '''
LocalHcState = hc.check_ha(LocalIp)

logging.info(aws.get_rt_tables(arg.vpc_id,'private'))

for table in aws.get_rt_tables(arg.vpc_id,'private'):
    logging.info('Table:\n%s', table)
    table_id = aws.get_table_id(table)
    logging.info('table_id: %s', table_id)
    for route in table_id.routes:
    	logging.info('route: \n%s', route)
        default = 'NoValue'
        if get_peer_az() is None:
            logging.info('No Peer Discovered')
            set_active(LocalInstanceId,get_peer_id(),table_id.route_table_id)
            logging.info('Moved NAT due to no Live Peer, to: %s', LocalInstanceId)
        if 'locked' in aws.get_tag(LocalInstanceId):
            logging.info('Checked my own tag:HaState and received: locked')
            break
        elif '0.0.0.0' in (route.get('DestinationCidrBlock', default)):
            logging.info('Carrying out actions on default route in table: %s', table_id)

            if 'blackhole' in route.get('State'):
                logging.info('Discovered BlackHole')
                set_active(LocalInstanceId,get_peer_id(),table_id.route_table_id)
                logging.info('Moved NAT due to BlackHole in the route, to: %s', LocalInstanceId)
                break

            elif LocalInstanceId not in route.get('InstanceId') and get_peer_id() not in route.get('InstanceId'):
                logging.info('Neither Active/Standby instance-id discovered in the default route')

                if 'active' not in aws.get_tag(get_peer_id()) and 'new' in aws.get_tag(LocalInstanceId):
                    logging.info('Active is not in the Peer State and New is in my State, setting Peer to locked while I take the routes')
                    aws.set_tag(get_peer_id(),'locked')
                    set_active(LocalInstanceId,get_peer_id(),table_id.route_table_id)
                    aws.set_tag(LocalInstanceId,'active')
                    aws.set_tag(get_peer_id(),'standby')

                elif 'active' not in aws.get_tag(LocalInstanceId) and 'active' not in aws.get_tag(get_peer_id()):
                    logging.info('Active is not in the Local or Peer State, locking peer and setting myself to Active')
                    aws.set_tag(get_peer_id(),'locked')
                    set_active(LocalInstanceId,get_peer_id(),table_id.route_table_id)
                    aws.set_tag(get_peer_id(),'standby')

                elif 'active' in aws.get_tag(LocalInstanceId) and 'standby' in aws.get_tag(get_peer_id()):
                    set_active(LocalInstanceId,get_peer_id(),table_id.route_table_id)

            elif 'running' not in get_peer_state() and 'failed' not in aws.get_tag(LocalInstanceId):
                NewPeer = aws.get_live_peer(get_peer_az(),'nat',arg.vpc_id)
                NewPeerId = NewPeer.get('Id', None)
                NewPeerState = NewPeer.get('State', {}).get('Name', None)
                if 'running' in NewPeerState and 'new' in aws.get_tag(NewPeerId):
                    logging.info('Found a new Peer, setting it to standby, then break')
                    aws.set_tag(NewPeerId,'standby')
                    break

                elif 'running' in NewPeerState and 'standby' in aws.get_tag(NewPeerId):
                    logging.info('Breaking from the process - we are all healthy')
                    break
                    
                logging.info('Peer is not in a running state and the host has not been set to failed yet')
                aws.set_tag(get_peer_id(),'failed')
                set_active(LocalInstanceId,get_peer_id(),table_id.route_table_id)
                shell.cmd(str('/usr/bin/aws ec2 replace-route --route-table-id ' + table_id.route_table_id + ' --destination-cidr-block 0.0.0.0/0 --instance-id ' + LocalInstanceId + ' --region ' + arg.region_name))
                aws.set_tag(LocalInstanceId,'active')
                logging.info('Moved NAT due to no Peer Available: %s', LocalInstanceId)
                break

            elif 'active' in aws.get_tag(get_peer_id()) and 'running' in PeerAwsState and 'new' in aws.get_tag(LocalInstanceId):
                logging.info('All tests passed, setting myself to standby') 
                aws.set_tag(LocalInstanceId,'standby')

            elif 'new' in aws.get_tag(get_peer_id()) and 'new' in aws.get_tag(LocalInstanceId):
                logging.info('Found new state, need to promote a host')
                aws.set_tag(LocalInstanceId,'locked')
                aws.set_tag(get_peer_id(),'standby')
                shell.cmd(str('/usr/bin/aws ec2 replace-route --route-table-id ' + table_id.route_table_id + ' --destination-cidr-block 0.0.0.0/0 --instance-id ' + LocalInstanceId + ' --region ' + arg.region_name))
                aws.set_tag(LocalInstanceId,'active')
                logging.info('Completed promotion from new state')

logging.info('Completed nat.py functions\n')
