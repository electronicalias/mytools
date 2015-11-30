import boto.cloudformation

region = 'eu-west-1'

cf_conn = boto.cloudformation.connect_to_region(region)

stack = cf_conn.describe_stacks('test')

for output in stack.outputs:
    print('%s=%s (%s)' % (output.key, output.value, output.description))
