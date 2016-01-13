from netaddr import *
mycidr = IPNetwork('10.0.0.0/18')

for line in mycidr.subnet(26):
    print line

