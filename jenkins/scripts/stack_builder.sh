#!/bin/bash
StackType=$(query "$params" CloudFormation.StackType)
Project=$(query "$params" CloudFormation.Project)


aws cloudformation create-stack \
  --stack-name ${Project}-test \
  --template-url https://s3-eu-west-1.amazonaws.com/nordcloud-${bucket}/${folder}/vpc.template \
  --region eu-west-1 \
  --capabilities CAPABILITY_IAM \
  --parameters \
  ParameterKey=StackType,ParameterValue=${StackType} \
  ParameterKey=Project,ParameterValue=${Project}
