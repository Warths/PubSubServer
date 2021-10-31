class TopicPool:
    def __init__(self, *args):
        self.topics = [*args]

    def add_topics(self, *args):
        """
        Adds a topics object to the pool
        """
        for topic in args:
            self.topics.append(topic)

    def get_topic(self, name):
        """
        Retrieve topic by name
        """
        for topic in self.topics:
            if topic.name == name:
                return topic
