#!/usr/env/bin python
''' Import Modules '''
import urllib2
import argparse
import cmd

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

aws.associate_eip(InstanceId,arg.allocation_id)
PeerId = aws.get_peer(PeerAz,'nat',arg.vpc_id)
PeerIp = aws.instance_ip(PeerId)


LocalState = state_check(LocalIp)
print LocalState

PeerState = state_check(PeerIp)
print PeerState

for table in aws.get_rt_tables(arg.vpc_id,'private'):
    table_id = aws.get_table_id(table)
    for route in table_id.routes:
    	default = 'NoValue'
        if '0.0.0.0' in (route.get('DestinationCidrBlock', default)):
            DestBlock = route.get('DestinationCidrBlock')
            if InstanceId not in route.get('InstanceId'):
                print ("I'm not the win!")
            else:
                print("Other Instance is Win!")

print(aws.eip_allociation(arg.allocation_id))

# shell.cmd(str('/usr/bin/aws ec2 describe-instances --region ' + arg.region_name))