#!/bin/bash
# Create trails in all AWS standard regions with the AWS CLI and Linux.
# Lets extend this to also enable CloudWatch Logs in each region:
# http://docs.aws.amazon.com/awscloudtrail/latest/userguide/send-cloudtrail-events-to-cloudwatch-logs.html

# Usage: enableCloudTrail.sh awsProfile s3bucket cloudwatch-logs-arn [region-for-global-events [alert-email]]

PROFILE=${1:-""}
BUCKET=${2:-""}
CLOUDWATCH_LOGS_ROLE_ARN=${3:-""}
REGION_FOR_GLOBAL_EVENTS=${4:-"eu-west-1"}
ALERT_EMAIL=${5:-""}

CLOUDWATCH_TEMPLATE=cloudwatch.json

if [ -z "$PROFILE" -o -z "$BUCKET" -o -z "$CLOUDWATCH_LOGS_ROLE_ARN" ]; then
	echo "Usage: $0 awsProfile s3bucket cloudwatch-logs-arn [[region-for-global-events] alert-email]"
	exit 1
fi 

#Get a list of all AWS Regions
regionlist=($(aws --profile "$PROFILE" --region "$REGION_FOR_GLOBAL_EVENTS" ec2 describe-regions --query Regions[*].RegionName --output text))

for REGION in "${regionlist[@]}"; do
 
 	echo "Configuring Cloudtrail for ${PROFILE}@${REGION} ..."
  	
	# Is this the region I want to log global events?
	LOG_GLOBAL_EVENTS="--no-include-global-service-events"	
	if [ "$REGION" = "$REGION_FOR_GLOBAL_EVENTS" ]; then 
		LOG_GLOBAL_EVENTS="--include-global-service-events"
	fi
	
	# First try update trail ...
	aws --profile "$PROFILE" --region "${REGION}" cloudtrail update-trail \
	 --name "${REGION}" --s3-bucket-name "${BUCKET}" "${LOG_GLOBAL_EVENTS}" 2> /dev/null
	if [ "$?" != "0" ]; then
		# If update fails, lets create a new trail
		aws --profile "$PROFILE" --region "${REGION}" cloudtrail create-trail \
		 --name "${REGION}" --s3-bucket-name "${BUCKET}" "${LOG_GLOBAL_EVENTS}" 2> /dev/null
	fi

	# Setting up Cloudwatch Logs & Alerts for Cloudtrail logs;
	# Logs and Alerts are region specific and you can not send
    	# alert to SNS topic in another region so each region must
    	# have it's own topic.

    	# UPDATE: SNS topic is now created from the same template that
    	# does setup for Cloudwatch alerts. Email update will trigger
    	# re-create for topic and all alerts linked to it.

	# Create log group 
	aws --profile "$PROFILE" --region "$REGION" logs create-log-group --log-group-name "cloudtrail-${REGION}"
	LOG_GROUP_ARN=`aws --profile "$PROFILE" --region "$REGION" logs describe-log-groups --log-group-name-prefix "cloudtrail-${REGION}" --query 'logGroups[].arn' --output text`

	# Update Cloudtrail with Cloudwatch Logs
	aws --profile "$PROFILE" --region "$REGION" cloudtrail update-trail --name "${REGION}" \
	 --cloud-watch-logs-log-group-arn "$LOG_GROUP_ARN" --cloud-watch-logs-role-arn "$CLOUDWATCH_LOGS_ROLE_ARN"
	
	# Update stack of Cloudwatch Alarms for Cloudtrail logs ...
        # (only if ALERT_EMAIL is set)
	if [ "$ALERT_EMAIL" != "" ]; then
		aws --profile "$PROFILE" --region "$REGION" cloudformation update-stack --stack-name cloudtrail-alarms \
	 	--template-body file://${CLOUDWATCH_TEMPLATE} --parameters ParameterKey=LogGroupName,ParameterValue=cloudtrail-${REGION} ParameterKey=AlarmEmail,ParameterValue=${ALERT_EMAIL} > /dev/null 2>&1
		if [ "$?" != "0" ]; then
			# If update fails, lets create a new stack
			aws --profile "$PROFILE" --region "$REGION" cloudformation create-stack --stack-name cloudtrail-alarms \
		 	--template-body file://${CLOUDWATCH_TEMPLATE} --parameters ParameterKey=LogGroupName,ParameterValue=cloudtrail-${REGION} ParameterKey=AlarmEmail,ParameterValue=${ALERT_EMAIL} > /dev/null 2>&1
		fi
	fi

	# Enable Cloudtrail logging
	aws --profile "$PROFILE" --region "${REGION}" cloudtrail start-logging --name "${REGION}"
done 
