from .authentication import is_authorized

class Topic:
    def __init__(self, name, publishers, subscribers, persistent=True, appended=tuple(), spec=None):
        """
        Topic can be used to template topics to subscribe/publish to.
        :param: persistant ; Boolean. Determines if the data persists after being emitted
        If any client subscribe to a persistant topic, he will receive the last state on subscription
        """
        self.name = name
        self.publishers = publishers
        self.subscribers = subscribers
        self.persistent = persistent
        self.appended = appended
        self.last_publish = None
        self.spec = spec
        self.appended_names = []
        self.add_appended_to_spec()

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
        authorization = {}
        if "authorization" in message:
            authorization = message["authorization"]
        result = is_authorized(self.publishers, authorization)
        return result

    def validate_payload(self, payload):
        """
        Uses the spec to validate a publication. Optionnal
        """
        if self.spec is None:
            return True

        # Verifying that values in spec are in payload
        for key, value in self.spec.items():
            if key not in payload["message"]:
                raise AttributeError("Value '{}' must be set in payload".format(key))

            if type(payload["message"][key]) != value:
                raise AttributeError("Value '{}' must be of type {}".format(key, value))

        # Verifying that no other values are included
        for key in payload["message"]:
            if key not in self.spec:
                raise AttributeError("Value '{}' is not valid in this topic.".format(key))


    def identify(self, message):
        return self.can_publish(message)

    def get_payload(self, message):
        payload = {
            "message": message["message"],
            "publisher": self.identify(message),
            "topic": self.name,

        }

        payload['message'].update(self.appended_result())
        return payload

    def appended_result(self):
        result = {}
        for func in self.appended:
            result.update(func())
        return result

    def add_appended_to_spec(self):
        for func in self.appended:
            for k, v in func().items():
                if self.spec is None:
                    pass
                    # self.spec = {}
                self.spec[k] = type(v)
                self.appended_names.append(k)

    @staticmethod
    def get_filters(payload):
        return payload["publisher"]

    def verbose(self):
        print(f"TOPIC NAME : {self.name}")
        if self.spec is None:
            print("    No spec.")
            return
        print(f"    Fields :")
        for field in self.spec:
            suffix = "(implicit)" if field in self.appended_names else "(required)"
            print(f"        {suffix} {field}: {self.spec[field].__name__}")


