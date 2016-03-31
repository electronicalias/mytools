import boto3

class aws:

    def __init__(self, region):
        self.region = region
        self.cf_conn = boto3.client('cloudformation',region)

    def create_change_set(self, stack_name, set_name, template_body):
        try:
            self.cf_conn.create_change_set(
                StackName = stack_name,
                ChangeSetName = set_name,
                TemplateBody = template_body)
        except Exception as error:
            print("Error creating a change set for {}: ****StackTrace: {} ****".format(stack_name, error))
            return (1)

    def describe_change_set(self, stack_name, set_name):
        try:
            data = self.cf_conn.describe_change_set(
                StackName = stack_name,
                ChangeSetName = set_name)
            return data
        except Exception as error:
            print("Error describing a change set for {}: ****StackTrace: {} ****".format(stack_name, error))
            return (1)

    def create_stack(self, stack_name, template_body):
        '''Create a stack'''
        
        print("Creating {} Stack in {}".format(stack_name, self.region))
        try:
            self.cf_conn.create_stack(
                StackName = stack_name,
                TemplateBody = template_body,
                Capabilities=['CAPABILITY_IAM'],
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': stack_name
                    },
                    {
                        'Key': 'RequestedBy',
                        'Value': 'Philip Smith'
                    }
             ])
        except Exception as error:
            print("Error creating {}: ****StackTrace: {} ***".format(stack_name, error))
            return (1)

    def update_stack(self, stack_name, template_body):
        '''Update a stack'''
        
        print("Updating {} Stack in {}".format(stack_name, self.region))
        try:
            self.cf_conn.update_stack(
                StackName = stack_name,
                TemplateBody = template_body,
                Capabilities=['CAPABILITY_IAM'],
                Tags=[
                     {
                         'Key': 'Name',
                         'Value': stack_name
                     },
                     {
                         'Key': 'RequestedBy',
                         'Value': 'Philip Smith'
                     }
                ])
        except Exception as error:
            print("Error updating {}: ****StackTrace: {} ***".format(stack_name, error))
            return (1)

    def get_stack_status(self, stack_name):
        ''' This is required to create a wait condition in the script while the stack is
        creating before the script then tries to read the stack attributes'''

        stacks = self.cf_conn.describe_stacks(
            StackName = stack_name
        )
        if len(stacks['Stacks']) == 1:
            stack = stacks['Stacks'][0]
        else:
            print ("No stacks found")
        return stack['StackStatus']

    def get_stacks(self):
        stacks = self.cf_conn.describe_stacks()
        if len(stacks) == 1:
            return stacks[0].stack_name
        else:
            return ""

    def get_stack_data(self, stack_name):
        ''' Hopefully this will return the VPC we want to use from the name given '''
        stacks = self.cf_conn.describe_stacks(stack_name)
        if len(stacks) == 1:
            stack = stacks[0]
        return stack
