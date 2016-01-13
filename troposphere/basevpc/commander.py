#!/bin/python
import argparse
import boto.cloudformation


class commands:
    """
    Usage:
    If you import this as a module then you can call all of the parameters stored in the command line
    """
    
    def __init__(self):
        self.data = []

    def stack_cmd(self):
        parser = argparse.ArgumentParser(
        prog='stack_creator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''
        Welcome to the BaseVpc tool, in order to use this tool, there are a few things you should do. Whilst this is still very much 'in development',
        it would be better to view the details for this tool in Bitbucket, on this link:

        https://bitbucket.org/nordcloud/cloud-in-a-box/basevpc

        ''')
        parser.add_argument('-azs','--availability-zones', nargs='+', help='specify the region azs, like a b c d etc', required=True)
        parser.add_argument('-nzs','--network-zones', nargs='+', help='see the long help message or look in the BitBucket Repo for clearer help', required=True)
        parser.add_argument('-con','--company-name')
        parser.add_argument('-prn','--project-name')
        parser.add_argument('-vcr','--vpc-cidr', required=True)
        parser.add_argument('-stk','--stack-type')
        parser.add_argument('-rgn','--region-name', required=True)
        parser.add_argument('-snm','--stack-name', required=True)
        ns = parser.parse_args()
        return ns

    def security_cmd(self):
        secparse = argparse.ArgumentParser(
        prog='security_creator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''
        add stuff here
        ''')
        secparse.add_argument('-csg','--component-security-groups', nargs='+', required=True)
        secparse.add_argument('-vpc','--vpc-id', required=True)
        secparse.add_argument('-rli','--rule-list', nargs='+')
        ns = secparse.parse_args()
        return ns

    def test(self):
        print("I don't understand Python yet!!")

class aws:

    def __init__(self, region):
        self.region = region
        self.cf_conn = boto.cloudformation.connect_to_region(region)

    def create_stack(self, stack_name, template_body):
        '''Create a stack'''
        
        print("Creating {} Stack in {}".format(stack_name, self.region))
        try:
            self.cf_conn.create_stack(
                           stack_name,
                           template_body,
                           capabilities=['CAPABILITY_IAM'],
                           tags=None
                           )
        except Exception as error:
            print("Error creating {}: ****StackTrace: {} ***".format(stack_name, error))
            return (1)

    def update_stack(self, stack_name, template_body):
        '''Update a stack'''
        
        print("Updating {} Stack in {}".format(stack_name, self.region))
        try:
            self.cf_conn.update_stack(
                           stack_name,
                           template_body,
                           capabilities=['CAPABILITY_IAM'],
                           tags=None
                           )
        except Exception as error:
            print("Error updating {}: ****StackTrace: {} ***".format(stack_name, error))
            return (1)

    def get_stack_status(self, region, stack_name):
        ''' This is required to create a wait condition in the script while the stack is
        creating before the script then tries to read the stack attributes'''

        stacks = self.cf_conn.describe_stacks(
                                    stack_name
                                    )
        if len(stacks) == 1:
            stack = stacks[0]
        else:
            print ("No stacks found")
        return stack.stack_status

    def get_stacks(self, stack_name):
        stacks = self.cf_conn.describe_stacks(stack_name)
        return stacks[0].stack_name

    def get_stack_data(self, stack_name):
        ''' Hopefully this will return the VPC we want to use from the name given '''
        stacks = self.cf_conn.describe_stacks(stack_name)
        if len(stacks) == 1:
            stack = stacks[0]
        return stack


if __name__ == "__main__":
    cmd = commands()
    print("Printing entire Namespace: {}".format(cmd.stack_cmd()))
    stack_attribute = cmd.stack_cmd()
    print("Printing single attribute stack_attribute.availability_zones[1]: {}".format(stack_attribute.availability_zones[1]))
