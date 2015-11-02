#!/bin/bash -x
bucket=$(query "$params" Parameters.BucketName)
folder=$(query "$params" Parameters.Folder)
WORKSPACE="../.."

if [ -z "$(aws s3 ls | awk '{ print $3 }' | grep nordcloud-${bucket})" ]; then
  aws s3 mb s3://nordcloud-${bucket}
  echo "Created the bucket 's3://nordcloud-${bucket}'"
else
  echo "The bucket 's3://nordcloud-${bucket}' was already created..."
fi

echo "Syncing files from Templates folder to s3://nordcloud-${bucket}/${folder}"
aws s3 sync $WORKSPACE/templates s3://nordcloud-${bucket}/${folder}
echo "Sync Completed.."
