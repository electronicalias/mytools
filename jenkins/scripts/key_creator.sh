#!/bin/bash
aws ec2 create-key-pair --key-name "${1}" > key_json
