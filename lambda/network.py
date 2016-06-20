from netaddr import *

ip = IPNetwork('10.0.0.0/16')
subnets = [ '10.0.0.0/23', '10.0.2.0/23', '10.0.252.0/23' ]
nets = []

def finder(network):
    for i in subnets:
        if network in i:
            nets.remove(network)


for address in ip.subnet(23):
    nets.append(str(address))
    finder(str(address))

print nets
