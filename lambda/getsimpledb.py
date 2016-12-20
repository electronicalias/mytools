import boto3
sdb = boto3.client('sdb', 'eu-west-1')

sdbdomains = sdb.list_domains()

ipsdb = 'testdomip'

if len(sdbdomains) >= 1:
    print "found a domain"
    for name in sdbdomains['DomainNames']:
       if name in ipsdb:
           print name
else:
    print "found no domain"
