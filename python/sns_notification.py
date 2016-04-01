#!/usr/bin/env python
import boto3
import argparse
import pprint

parser = argparse.ArgumentParser(
    prog='Send a Message via SNS',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
    Get the stack outputs for the specified stack
    ''')
parser.add_argument('-rgn','--region_name', required=True)
parser.add_argument('-arn','--topic_name', required=True)
parser.add_argument('-dat','--build_data', required=True)
parser.add_argument('-sbj','--subject_text', required=True)
arg = parser.parse_args()

sns = boto3.client('sns', arg.region_name)

def topic_arn():
    arn = sns.list_topics()
    for item in arn['Topics']:
        if arg.topic_name in item['TopicArn']:
            return item['TopicArn']

def send_message(arn, message, subject):
    sns.publish(
        TopicArn=arn,
        Message=message,
        Subject=subject
    )

topic = topic_arn()
send_message(topic, arg.build_data, arg.subject_text)
