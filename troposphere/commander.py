#!/bin/python
import argparse

class commands:

    def __init__(self):
        self.data = []

    def stack_cmd(self):
        parser = argparse.ArgumentParser(
        prog='stack_creator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''
        add stuff here
        ''')
        parser.add_argument('-azs','--availability-zones', nargs='+', help='specify the region azs, like a b c d etc', required=True)
        parser.add_argument('-nzs','--network-zones', nargs='+', help='specify network zones, like public private dmz etc', required=True)
        parser.add_argument('-con','--company-name')
        parser.add_argument('-prn','--project-name')
        parser.add_argument('-vcr','--vpc-cidr')
        parser.add_argument('-prs','--private-subnets')
        parser.add_argument('-pus','--public-subnets')
        parser.add_argument('-dms','--dmz-subnets')
        parser.add_argument('-dbs','--db-subnets')
        parser.add_argument('-stk','--stack-type')
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

if __name__ == "__main__":
    cmd = commands()
    print("Printing entire Namespace: {}".format(cmd.stack_cmd()))
    stack_attribute = cmd.stack_cmd()
    print("Printing single attribute stack_attribute.availability_zones[1]: {}".format(stack_attribute.availability_zones[1]))
