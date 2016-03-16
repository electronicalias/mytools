#!/usr/env/bin python
import cmd
import argparse

''' Setup the Command Line to accept the variables required '''
parser = argparse.ArgumentParser(
    prog='Nat Updater',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    This program will do a HTTP GET to the status file /var/www/html/index.html on the Peer Server, to be successful
    we should receive 'OK', if the instance can't get to the internet it will give a 'FAIL'.
    ''')
parser.add_argument('-r','--region_name', required=True)
parser.add_argument('-v','--vpc_id', required=True)
arg = parser.parse_args()

InstanceId = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read()
AvailabilityZone = urllib2.urlopen('http://169.254.169.254/latest/meta-data/placement/availability-zone').read()
LocalIp = urllib2.urlopen('http://169.254.169.254/latest/meta-data/local-ipv4').read()
if AvailabilityZone.endswith('a'):
    PeerAz = str(AvailabilityZone[:-1] + 'b')
elif AvailabilityZone.endswith('b'):
    PeerAz = str(AvailabilityZone[:-1] + 'a')

def state_check(host):
    try:
        response = urllib2.urlopen(str('http://' + host + '/index.html')).read()
        return response
    except:
    	return str('FAIL')

aws = cmd.aws(arg.region_name)

PeerId = aws.get_peer(PeerAz,'nat',arg.vpc_id)
PeerIp = aws.instance_ip(PeerId)

print state_check(PeerIp)