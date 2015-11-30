Enable Cloudtrail logging for (multiple) Regions in a single AWS account

1) Setup S3 bucket for storing Cloudtrail logs

Create cloudformation stack "cloudtrail-logs" from cloudtrailbucket.json -template
on the AWS account that you want to store the logs at any single region you choose.
Idealy S3 bucket should be in the same region where you plant to log global events.

Stack takes 2 parameters

- S3 bucket name
- Log expiration time (in days)

Logs are deleted when they get older than log expiration time. You can change expiration
by doing stack update but bucket name can not be changed.

2) Configure and enable Cloudtrail on all regions (for all accounts)

Configure your AWS CLI with API key/secret for all accounts you want to configure.
Then run the following command for each of accounts

% ./enableCloudTrail.sh accountName s3bucket cloudwatchLogsArn [awsRegion [alertEmail]]

where

- accountName is the name account as you configured it for AWS CLI
- s3Bucket is the name S3 bucket you created at step 1
- cloudwatchLogsArn is the ARN you got from stack output at step 1
- alertEmail where Cloudwatch should send alerts
(optional, if not specified then no cloudwatch alerts are created)
- awsRegion is the region where you want to log global events
(i.e. the same region where you created the cloudformation stack as step 1, defaults to eu-west-1)

e.g. enableCloudTrailAllRegions.sh customername customername-cloudtrail arn:aws:iam::NNNNNNNNNNNN:role/cloudtrailbucket-CloudwatchLogsRole-156XVF7KMTBTK myemail@domain.com eu-west-1

Repeat the command for all accounts you want to enable Cloudtrail.

3) Done!

