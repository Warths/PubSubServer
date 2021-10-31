from .authentication import is_authorized

class Topic:
    def __init__(self, name, publishers, subscribers, persistent=True):
        """
        Topic can be used to template topics to subscribe/publish to.
        :param: persistant ; Boolean. Determines if the data persists after being emitted
        If any client subscribe to a persistant topic, he will receive the last state on subscription
        """
        self.name = name
        self.publishers = publishers
        self.subscribers = subscribers
        self.persistent = persistent
        self.last_publish = None

    def can_subscribe(self, message):
        """
        Uses authentication core to check if payload works for subscription
        """
        if "authorization" in message:
            authorization = message["authorization"]
        else:
            authorization = None
        return is_authorized(self.subscribers, authorization)


    def can_publish(self, message):
        """
        Uses authentication core to check if payload works for publish
        """
        if "authorization" in message:
            authorization = message["authorization"]
        else:
            authorization = None
        return is_authorized(self.publishers, authorization)

    def identify(self, message):
        return self.can_publish(message)

    def get_payload(self, message):
        payload = {
            "message": message["message"],
            "publisher": self.identify(message),
            "topic": self.name,
        }
        return payload

    def get_filters(self, payload):
        return payload["publisher"]



