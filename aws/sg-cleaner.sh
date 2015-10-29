#!/bin/bash
# Author:       philip.smith@nordcloud.com
# Version:      1.0
# Script can be used to remove any instance of a security group from the source of other groups
# Useful notation of --query command:
# aws ec2 describe-security-groups --region eu-west-1 --query 'SecurityGroups[?IpPermissions[?UserIdGroupPairs[?GroupId=='${sg}']]].[IpPermissions[?UserIdGroupPairs[?GroupId=='${sg}']].ToPort, IpPermissions[?UserIdGroupPairs[?GroupId=='${sg}']].UserIdGroupPairs[].GroupId]' --output text
#
# Script expects the following variables:
# $Region - specify the region to run the command against
# $SecurityGroupId - value taken from the console/system/aws for a security group that you wish to remove from the source of other groups
SgId=$(echo "\`${SecurityGroupId}\`")

function find_groups() {
        echo $(aws ec2 describe-security-groups --region ${Region} \
        --query 'SecurityGroups[?IpPermissions[?UserIdGroupPairs[?GroupId=='${1}']]].GroupId' \
        --output text)
}

function find_ports() {
        echo $(aws ec2 describe-security-groups --region ${Region} \
        --query 'SecurityGroups[?GroupId=='${1}'].[IpPermissions[?UserIdGroupPairs[?GroupId=='${2}']].ToPort]' \
        --output text)
}


for RULE in $(find_groups ${SgId}); do
  SGRULE=$(echo "\`${RULE}\`")
  for PORT in $(find_ports ${SGRULE} ${SgId}); do
  	aws ec2 revoke-security-group-ingress --group-id ${RULE} --protocol tcp --port ${PORT} --source-group ${SecurityGroupId} --region ${Region}
  	echo -e "Removed the following Rules from ${RULE} \n
  	Source: \t \t ${SecurityGroupId} \n
  	Port: \t \t ${PORT} \n \n \n"
  done
  SGRULE=''
done