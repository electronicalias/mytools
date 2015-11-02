#!/bin/bash
source set_credentials.sh

 
VPC=$(aws ec2 describe-vpcs --output json | jq '.[] | .[]') 
VPCID=$(query "${VPC}" VpcId)

