#!/bin/bash
unset AWS_DEFAULT_REGION AWS_ACCESS_KEY_ID AWS_SECRET_KEY_ID
source creds

ACCNUM=$(query "$params" Parameters.Account)
ACCROLE=$(query "$params" Parameters.CrossRole)

CREDS=$(aws sts assume-role \
  --role-arn "arn:aws:iam::${ACCNUM}:role/${ACCROLE}" \
  --role-session-name "test" \
  --output json)

AKI=$(query "${CREDS}" Credentials.AccessKeyId)
SAK=$(query "${CREDS}" Credentials.SecretAccessKey)
TOK=$(query "${CREDS}" Credentials.SessionToken)

unset AWS_ACCESS_KEY_ID AWS_SECRET_KEY_ID AWS_SESSION_TOKEN

export AWS_ACCESS_KEY_ID=$(echo ${AKI})
export AWS_SECRET_ACCESS_KEY=$(echo ${SAK})
export AWS_SESSION_TOKEN=$(echo ${TOK})
