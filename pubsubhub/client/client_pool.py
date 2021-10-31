from threading import Lock
import json

class ClientPool:
    def __init__(self):
        """
        ClientPool handle global client management features
        """
        self.clients = []
        self.lock = Lock()

    def bind(self, client):
        """ Register client in ClientPool """
        with self.lock:
            client.log.info("Connected.")
            self.clients.append(client)

    def disconnect(self, client):
        """ Closes and unregister client """
        with self.lock:
            client.log.info("Disconnected.")
            self.clients.remove(client)

    def tick(self):
        pass

    def get_subscribers(self, topic, filters):
        return self.clients

    def publish(self, topic, filters, payload):
        subs = self.get_subscribers(topic, filters)
        full_payload = {
            "type": "MESSAGE",
            "data": {
                "topic": '.'.join([topic, *filters]),
                "message": json.dumps(payload)
            }
        }
        for sub in subs:
            sub.send(full_payload)


