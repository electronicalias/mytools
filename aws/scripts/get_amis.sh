#!/bin/bash

function get_amis() {
  local region_name="$1"
  aws ec2 describe-images \
    --filters \
      Name=owner-alias,Values=amazon \
      Name=name,Values="Windows_Server-2008-R2_SP1-English-64Bit-Base-*" \
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

if [ -z "$1" ]; then
  for region_name in $(aws ec2 describe-regions --region eu-west-1 --query "sort(Regions[].RegionName)" --output text); do
    get_amis ${region_name}
  done
else
  case "$1" in
    -r|--region)
      shift
      region_name="$1"
      ;;
    *)
      echo "usage: get_amis [-r | --region]" 1>&2
      exit 1
  esac
  get_amis ${region_name}
fi
