from gevent import Timeout
from .getlogger import getLogger
import time


class PubSubClient:
    def __init__(self, websocket, ping_timeout=300, unsubscribed_timeout=15):
        """
        PubSubHub Client class
        :param websocket: websocket
        """
        self.websocket = websocket
        self.queue = []
        self.topics = []

        # Service timeout related
        self.last_ping = time.time()
        self.last_subscriber_date = time.time()

        self.ping_timeout = ping_timeout
        self.unsubscribed_timeout = unsubscribed_timeout

        self.log = getLogger("{}:{}".format(*self.getaddr()))


    def receive(self, timeout=0.1):
        """
        Try receiving data from client
        :param timeout: Amount of time before giving up
        """
        with Timeout(timeout, False):
            return self.websocket.receive()

    @property
    def alive(self):
        """ Checks if websocket got closed """
        if self.websocket.closed:
            self.log.debug("Connexion closed gracefully")
            return False

        return True

    @property
    def respect_guidelines(self):
        """ Checks if client respected guidelines """
        if self.no_subscription_check(self.unsubscribed_timeout):
            self.log.debug("Client wasn't subscribed to any topic for {} seconds".format(self.unsubscribed_timeout))
            return False

        if self.no_ping_check(self.ping_timeout):
            self.log.debug("Client didn't send ping for {}".format(self.ping_timeout))
            return False

        return True

    def no_subscription_check(self, seconds):
        """ Checks if client was subscribed to anything since a specific time period """
        if len(self.topics):
            self.last_subscriber_date = time.time()
        return self.last_subscriber_date + seconds < time.time()

    def no_ping_check(self, seconds):
        """ Checks if ping was issued since a specific time period"""
        return self.last_ping + seconds < time.time()

    def getaddr(self):
        """ return address and port. Try to get real IP from Nginx """
        try:
            addr = self.websocket.environ["HTTP_X_REAL_IP"]
        except KeyError:
            addr = self.websocket.environ['REMOTE_ADDR']
        port = self.websocket.environ['REMOTE_PORT']

        return addr, port
