#!/bin/bash
UseKey=$(aws ec2 describe-key-pairs --query "KeyPairs[?KeyName=='"${1}"'].KeyName" --output text)

if [ "${1}" != "${UseKey}" ]; then
  echo "Creating key for ${1}"
  aws ec2 create-key-pair --key-name ${1} --query KeyMaterial --output text > ${1}.pem
  echo "Created ${1} key"
else
  echo "Key already created for ${1}"
fi
