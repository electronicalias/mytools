#!/usr/env/bin python
import cmd
import argparse
import urllib2
import time
import syslog

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

def state_check():
    try:
        Peer = aws.get_instance(PeerAz,'nat',arg.vpc_id)
        if 'running' not in Peer.get('State', {}).get('Name', None):
            return str('FAIL')
        elif 'running' in Peer.get('State', {}).get('Name', None):
            PeerId = Peer.get('Id')
            PeerIp = aws.instance_ip(PeerId)
            request = urllib2.Request('http://' + PeerIp + '/index.html')
            response = urllib2.urlopen(request, timeout=4)
            content = response.read()
            if 'OK' in content:
                syslog.syslog(str('Response from host is OK'))
                return content
    except:
    	return str('FAIL')

aws = cmd.aws(arg.region_name)
shell = cmd.bash()

PeerAz = aws.get_peer_az(arg.vpc_id,InstanceId)

while True:
    if "OK" not in state_check():
        syslog.syslog(str('Peer has failed, running the nat.py function'))
        shell.cmd(str('/usr/local/bin/take_nat.sh'))
    time.sleep(10)
