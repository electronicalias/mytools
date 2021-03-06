#!/bin/bash
Bucket=$(query "$params" CloudFormation.Bucket)
Folder=$(query "$params" CloudFormation.Folder)
KeyName=$(query "$params" CloudFormation.KeyName)
StackType=$(query "$params" CloudFormation.StackType)
Project=$(query "$params" CloudFormation.Project)
Peering=$(query "$params" CloudFormation.Peering)
PublicIp=$(query "$params" CloudFormation.PublicIp)
AmiId=$(source ami_grabber.sh)


aws cloudformation create-stack \
  --stack-name ${Project} \
  --template-url https://s3-eu-west-1.amazonaws.com/nordcloud-${bucket}/${folder}/master.template \
  --region eu-west-1 \
  --capabilities CAPABILITY_IAM \
  --parameters \
  ParameterKey=AmiId,ParameterValue=${AmiId} \
  ParameterKey=Bucket,ParameterValue=${Bucket} \
  ParameterKey=Folder,ParameterValue=${Folder} \
  ParameterKey=KeyName,ParameterValue=${KeyName} \
  ParameterKey=StackType,ParameterValue=${StackType} \
  ParameterKey=Project,ParameterValue=${Project} \
  ParameterKey=Peering,ParameterValue=${Peering} \
  ParameterKey=PublicIp,ParameterValue=${PublicIp}
