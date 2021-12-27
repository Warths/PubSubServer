import traceback
from .client import Client, ClientPool
from .topic import TopicPool
from .getlogger import getLogger
from .exceptions import *
from .rules import RuleSet
from threading import Thread
import time

class PubSubHub:
    def __init__(self, http, ws, http_route="/publish/", ws_route="/", name="PubSub"):
        """
        :param http: Flask Http server
        :param ws: Flask-Sockets WS server
        :param http_route: http address root
        :param ws_route: ws address root
        """
        self.name = name
        self.log = getLogger(name)
        self._http = http
        self._ws = ws
        self._populate(http_route, ws_route)
        self.rule_set = RuleSet()
        self.client_pool = ClientPool()
        self.topic_pool = TopicPool()
        self.handling = {
            "PING": self.handle_ping,
            "SUBSCRIBE": self.handle_subscribe,
            "UNSUBSCRIBE": self.handle_unsubscribe,
            "PUBLISH": self.handle_publish
        }

        self.routine = Thread(target=self._routine)
        self.routine.start()

    def _populate(self, http_route, ws_route):
        """ Adds HTTP ans WS route to the HTTP ans WS apps """

        # Adding Http Publish only route
        @self._http.route(http_route)
        def http_handling(*args, **kwargs):
            return "Success", 200

        # Adding WebSocket PubSub route
        @self._ws.route(ws_route)
        def ws_route(client, *args, **kwargs):
            self.serve(Client(client))


    def _routine(self):
        while True:
            time.sleep(0.05)
            try:
                self.client_pool.tick()

                # Iterating through all clients
                for client in self.client_pool.clients:

                    # Iterating through all messages received by individual clients
                    for message in client.messages:
                        client.log.info(message)
                        try:
                            # Targeting handle function in map
                            if "type" in message and message["type"] in self.handling:
                                self.handling[message["type"]](client, message)
                        except (PermissionError, AttributeError) as err:
                            client.send({"error": str(err)})

            except:
                traceback.print_exc()


    def handle_ping(self, client, message):
        client.ping()

    def handle_subscribe(self, client, message):
        errors = []
        success = []
        nonce = message["nonce"] if "nonce" in message else None

        """ Checking correct data structure for subscription handling"""

        if "topics" not in message:
            raise AttributeError("No topics in subscription request.")

        if not isinstance(message["topics"], list):
            raise AttributeError("<topics> value must be a list")

        """ END structure check """

        for sub_request in message["topics"]:
            # Getting topic name (full request include filters)
            topic_name = sub_request.split(".")[0]
            topic = self.topic_pool.get_topic(topic_name)

            # trying to subscribe if topic exists
            if topic:
                # Checking subscription authorization
                if topic.can_subscribe(message):
                    client.topics.append(sub_request)
                    success.append("{} topic subscribed with filters : {}".format(topic_name, sub_request))

                    # Persistent Handling
                    if topic.persistent and topic.last_publish:
                        if client.is_subscribed(topic.name, topic.last_publish["filters"]):
                            client.send(topic.last_publish["payload"])
                # Notifying if not authorized
                else:
                    errors.append("Can not subscribe to <{}> with provided auth method/credentials.".format(topic.name))
            else:
                errors.append("Topic <{}> doesn't exist".format(topic_name))
        payload = {
            "success": success,
            "errors": errors,
            "nonce": nonce
        }
        client.send(payload)

    def handle_unsubscribe(self, client, message):
        errors = []
        success = []
        nonce = message["nonce"] if "nonce" in message else None

        """ Checking correct data structure for unsubscription handling"""

        if "topics" not in message:
            raise AttributeError("No topics in unsubscription request.")

        if not isinstance(message["topics"], list):
            raise AttributeError("'topics' value must be a list")

        """ END structure check """
        for unsub in message["topics"]:
            if unsub in client.topics:
                client.topics.remove(unsub)
                success.append("Topic '{}' unsubscribed.".format(unsub))
            else:
                errors.append("Topic '{}' wasn't subscribed.")

        client.send({
            "success": success,
            "errors": errors,
            "nonce": nonce
        })

    def handle_publish(self, client, message):
        errors = []
        success = []
        nonce = message["nonce"] if "nonce" in message else None

        """ Checking correct data structure for publish handling """

        if "topic" not in message:
            raise AttributeError("No topic in publish request.")

        if not isinstance(message["topic"], str):
            raise AttributeError("'topic' value must be a string")

        if not "message" in message:
            raise AttributeError("No message in publish request")

        if not isinstance(message["message"], dict):
            raise AttributeError("message must be a associative array")

        """ Checking End """

        topic = self.topic_pool.get_topic(message["topic"])
        if topic.can_publish(message):
            payload = topic.get_payload(message)
            topic.validate_payload(payload)
            filters = topic.get_filters(payload)

            for other_client in self.client_pool.clients:
                if other_client.is_subscribed(payload["topic"], filters):
                    topic.last_publish = {
                        "payload": payload,
                        "filters": filters
                    }
                    other_client.send(payload)

            success.append("Content published to topic '{}' with filters {}".format(message["topic"], filters))

        else:
            errors.append("Can not publish to '{}' with provided auth method/credentials.".format(message["topic"]))

        payload = {
            "success": success,
            "errors": errors,
            "nonce": nonce
        }

        client.send(payload)




    def serve(self, client):
        self.client_pool.bind(client)
        while True:
            # Rule Validation.
            try:
                self.rule_set.validate(client)
            except BrokenRuleException as err:
                client.log.info(err)
                client.send({"error": str(err)})
                self.client_pool.disconnect(client)
                return

            # Sending awaiting messages
            try:
                client.send_all()
            except PubSubClientException:
                pass

            # Receiving messages
            client.fetch()

            if not client.alive:
                self.client_pool.clients.remove(client)
                break
