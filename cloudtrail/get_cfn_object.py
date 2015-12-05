import boto.cloudformation

cf_conn = boto.cloudformation.connect_to_region(region_name='eu-west-1')

class stacks:

	def __init__(self, name, region):
		self.name = name
		self.stacklist = []
		self.regions = []

	def add_stack(self, stack):
		self.stacklist.append(stack)


stacks = cf_conn.describe_stacks('cloudtrail-iams')
if len(stacks) == 1:
    stack = stacks[0]

for output in stack.outputs:
    stacks.add_stack(output.value)
