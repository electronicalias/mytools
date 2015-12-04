import boto.sns
sns_conn = boto.sns.connect_to_region(region_name='eu-west-1')

def getSnsTopics():
    try:
        topics = sns_conn.get_all_topics()['ListTopicsResponse']['ListTopicsResult']['Topics']
        for topicname in topics:
            if 'CloudtrailAlerts' in topicname['TopicArn']:
                return topicname['TopicArn']
    except Exception as error:
        print("Error with getting SNS Topics: ****StackTrace: {} ***".format(error))
        return (1)

def getSnsTopicAttribs(topic):
    try:
        topics = sns_conn.get_topic_attributes(topic)
        return topics
    except Exception as error:
        print("Error with getting SNS Topic Attributes: ****StackTrace: {} ***".format(error))
        return (1)

sns_topics = getSnsTopics()
sns_topic_attribs = getSnsTopicAttribs(sns_topics)
print("Here are the details of the following Topic: {}".format(sns_topics))
print sns_topic_attribs
