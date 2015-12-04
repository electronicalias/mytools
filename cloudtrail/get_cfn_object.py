import boto.cloudformation

cf_conn = boto.cloudformation.connect_to_region(region_name='eu-west-1')

stacks = cf_conn.describe_stacks('cloudtrail-iams')
if len(stacks) == 1:
    stack = stacks[0]

for output in stack.outputs:
    print('%s' % (output.value))
