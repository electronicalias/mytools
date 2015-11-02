#!/bin/bash
SUBNET=$(aws ec2 describe-subnets --output json) 
query "${SUBNET}" "Subnets[?MapPublicIpOnLaunch].SubnetId | [0]"
