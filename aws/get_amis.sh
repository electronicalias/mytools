#!/bin/bash

function get_amis() {
  local region_name="$1"
  aws ec2 describe-images \
    --filters \
      Name=owner-alias,Values=amazon \
      Name=name,Values="Windows_Server-2008-SP2-English-64Bit-Base-*" \
      Name=architecture,Values=x86_64 \
      Name=virtualization-type,Values=hvm \
      Name=root-device-type,Values=ebs \
    --region "$region_name" \
    --query "reverse(sort_by(Images[? !contains(Name, 'rc')], &CreationDate))
             [*].[ImageId,CreationDate]" \
    --output text \
    | awk '{ print $1 }' \
    | head -1
}

for region in $(aws ec2 describe-regions --region eu-west-1 --query "sort(Regions[].RegionName)" --output text); do
  echo  -e "${region} $(get_amis ${region})"
done
