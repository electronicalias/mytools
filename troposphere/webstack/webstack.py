#!/usr/bin/env python
import argparse
import detailer


''' Collect all of the command line variables '''
parser = argparse.ArgumentParser(
prog='Web Stack Creator',
formatter_class=argparse.RawDescriptionHelpFormatter,
description='''This program will build a variable sized webstack in any region''')
parser.add_argument('-rgn','--region', help='Specify the region this will be deployed in', required=True)
args = parser.parse_args()

cmd = detailer.resource(args.region)

resources = {}

for i in cmd.az('production', 'public'):
    resources[str(i['SubnetId'])] = str(i['AvailabilityZone'])

print resources

for key, value in resources.iteritems():
    print value 
