import json
import time
from threading import Lock
import geventwebsocket.exceptions
from gevent import Timeout

from pubsubhub.getlogger import getLogger


class Client:
    def __init__(self, websocket):
        """
        PubSubHub Client class
        :param websocket: websocket
        """
        self.websocket = websocket
        self.queue = []
        self.topics = []
        self._messages = []

        # Service timeout related
        self.last_ping = time.time()
        self.last_subscription_date = time.time()

        self.lock = Lock()
        self.log = getLogger("{}:{}".format(*self.getaddr()))

    def is_subscribed(self, name, filters):
        """
        Return if a user is subscribed to a topic (with modifiers)
        """
        for topic in self.topics:
            topic_filters = topic.split(".")
            topic_name = topic_filters.pop(0)
            topic_filters = set(topic_filters)

            # Checking topic match
            if topic_name != name:
                continue

            if len(topic_filters) == len(topic_filters.intersection(filters)):
                return True

        return False

    def receive(self, timeout=0.1):
        """
        Try receiving data from client. Ignore garbage data.
        :param timeout: Amount of time before giving up
        """
        with Timeout(timeout, False):
            try:
                pre = self.websocket.receive()
                message = json.loads(pre)
                return message
            except (TypeError, geventwebsocket.exceptions.WebSocketError):
                # Client probably closed and returned none
                self.close()
            except json.JSONDecodeError:
                self.log.info(pre)
                self.log.info("Couldn't be processed as a JSON string. Skipping")

    def fetch(self):
        message = self.receive()
        if message:
            with self.lock:
                self._messages.append(message)

    @property
    def messages(self):
        with self.lock:
            messages = self._messages
            self._messages = []
        return messages

    def send(self, payload):
        """ Send the payload to the client """
        try:
            self.websocket.send(json.dumps(payload, default=lambda o: o.__repr__()) + "\r\n")
        except Exception as e:
            self.log.warning("{}: {}".format(str(e), e))

    def send_all(self, flush=True):
        """ sends all payloads to the client"""
        for payload in self.queue:
            self.send(payload)

        if flush:
            self.flush()

    def send_one(self):
        if self.queue:
            with Lock():
                payload = self.queue.pop()
                self.send(payload)
                self.log.debug(payload)

    def flush(self):
        """ Removes all payloads in the queue """
        with Lock():
            self.queue = []

    def add_to_queue(self, payload):
        """ Adds a payload to the queue """
        self.queue.append(payload)

    @property
    def alive(self):
        """ Checks if websocket got closed """
        if self.websocket.closed:
            self.log.debug("Connexion closed gracefully")
            return False

        return True

    def ping(self):
        self.last_ping = time.time()
        self.queue.append({"type": "PONG"})

    def close(self):
        self.websocket.close()

    def getaddr(self):
        """ return address and port. Try to get real IP from Nginx """
        try:
            addr = self.websocket.environ["HTTP_X_REAL_IP"]
        except KeyError:
            addr = self.websocket.environ['REMOTE_ADDR']
        port = self.websocket.environ['REMOTE_PORT']

        return addr, port
