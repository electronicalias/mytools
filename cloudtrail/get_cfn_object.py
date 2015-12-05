import boto.cloudformation

cf_conn = boto.cloudformation.connect_to_region(region_name='eu-west-1')

class stacks:
    
    cf_conn = boto.cloudformation.connect_to_region(region_name='eu-west-1')
	
    def __init__(self, region):
        self.region = region 
        self.stacklist = []
    
    def add_stack(self, stack):
        self.stacklist.append(stack)
        

s = stacks('eu-west-1')
s.add_stack('thefutureofstacking')
s.add_stack('someothername')

print(s.stacklist)
