#!/usr/env/bin python
''' Import Modules '''
import urllib2
import argparse
import cmd

InstanceId = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read()

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
arg = parser.parse_args()

aws = cmd.aws(arg.region_name)
aws.associate_eip(InstanceId,arg.allocation_id)