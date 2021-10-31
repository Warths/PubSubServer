from . import Rule
import time

class PingIntervalRule(Rule):
    def __init__(self, interval=300):
        super().__init__()
        self.interval = interval
        self.rule_funcs.append(self.alive)
        self.error_message = "Client must send a ping every {} at most".format(self.interval)

    def alive(self, client):
        return client.last_ping + self.interval > time.time()