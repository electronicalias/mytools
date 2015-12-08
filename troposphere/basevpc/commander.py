#!/bin/python
import argparse
import boto.cloudformation


class commands:

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
        parser.add_argument('-con','--company-name', required=True)
        parser.add_argument('-prn','--project-name', required=True)
        parser.add_argument('-vcr','--vpc-cidr', required=True)
        parser.add_argument('-stk','--stack-type', required=True)
        ns = parser.parse_args()
        return ns

    def other_cmd(self):
        parser = argparse.ArgumentParser(
        prog='stack_creator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''
        add stuff here
        ''')
        parser.add_argument('-stk','--stack-type')
        ns = parser.parse_args()
        return ns

    def test(self):
        print("I don't understand Python yet!!")

class aws:

    def __init__(self, region, profile):
        self.region = region
        self.cf_conn = boto.cloudformation.connect_to_region(region, profile_name=profile)

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
            self.cf_conn.create_stack(
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


if __name__ == "__main__":
    cmd = commands()
    print("Printing entire Namespace: {}".format(cmd.stack_cmd()))
    stack_attribute = cmd.stack_cmd()
    print("Printing single attribute stack_attribute.availability_zones[1]: {}".format(stack_attribute.availability_zones[1]))