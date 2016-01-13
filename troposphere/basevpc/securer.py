#!/bin/python
import commander
import cloudformer
from netaddr import IPNetwork
import boto.cloudformation
import time

cmd = commander.commands()
attribs = cmd.security_cmd()

sg_names =  attribs.component_security_groups
vpc_id = attribs.vpc_id
rule_list = attribs.rule_list


awscmd = commander.aws('eu-west-1')

aws_cmd = cloudformer.aws_resources()

for name in sg_names:
    aws_cmd.create_sg(name, vpc_id, 'Some Descriptions about the ' + name)
    
for line in rule_list:
    rule = line.split(":")
    print("Source: {} Dest: {}".format(rule[1], rule[2]))
    aws_cmd.create_sg_ingress(rule[0], rule[3], rule[4], rule[1], rule[5])

cfn_body = aws_cmd.complete_cfn()
print cfn_body
# awscmd.create_stack('test-poc-security', cfn_body)
