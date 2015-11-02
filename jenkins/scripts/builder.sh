#!/bin/bash
source query_function.sh

# Read the parameters for the company being setup
params=$(cat parameters)

# Set the credentials by grabbing their role ID
source set_credentials.sh
source create_bucket.sh


source get_vpc.sh
source subnet_fetcher.sh

echo -e "Creating CloudFormation Stacks..."
source stack_builder.sh
