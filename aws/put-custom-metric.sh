#!/bin/bash
# Auther: electronicalias@gmail.com
# Purpose: Put a single metric into an AWS CloudWatch Metric that can then be used for 
#          alarms, auto-scaling or general monitoring.



# Collect the metric that will be used in the CloudWatch Metric
function get_metric() {
  # The command below can be used to get any metric, here as an example it creates a random number
  echo $((RANDOM%200+100))
}

# Format and capture the date each time the script runs, this sets the timestamp in CloudWatch
function get_date() {
  echo $(date +"%Y-%m-%dT%T.000Z")
}

# Insert metric to CloudWatch
aws cloudwatch put-metric-data --metric-name PageViewCount --namespace "PSmithService" --value $(get_metric) --timestamp $(get_date) --region eu-west-1
