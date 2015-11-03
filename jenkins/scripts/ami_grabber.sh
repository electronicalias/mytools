#!/bin/bash -x
aws ec2 describe-images \
  --filters \
      Name=owner-alias,Values=amazon \
      Name=name,Values="amzn-ami-hvm-*-ebs" \
      Name=architecture,Values=x86_64 \
      Name=virtualization-type,Values=hvm \
      Name=root-device-type,Values=ebs \
  --query \
    "reverse(sort_by(Images, &CreationDate))[0].{ImageId: ImageId}" \
  --output text
