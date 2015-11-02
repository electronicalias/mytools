#!/bin/bash
VPC=$(aws ec2 describe-vpcs --output json | jq '.[] | .[]') 
query "${VPC}" VpcId
