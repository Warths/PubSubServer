from gevent import Timeout
import time


class Client:
    timeout = 300

    def __init__(self, websocket):
        """
        PubSubHub Client class
        :param websocket: websocket
        """
        self.websocket = websocket
        self.queue = []

        # Service timeout related
        self.last_ping = time.time()
        self.last_service = time.time()

    def receive(self, timeout=0.1):
        """
        Try receiving data from client
        :param timeout: Amount of time before giving up
        """
        with Timeout(timeout, False):
            return self.websocket.receive()


