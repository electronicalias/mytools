#!/bin/bash
dir=/Users/psmith/mytools/lambda/subnetter

rm -rf $dir/subnetter.zip
cd $dir && zip -r $dir/subnetter.zip *

aws --region eu-west-1 s3 cp $dir/subnetter.zip s3://siemens-dgs-deployment/lambdas/subnetter.zip
