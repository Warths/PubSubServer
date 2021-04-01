import json
import time

class PubSubHub:
    def __init__(self, http, ws, http_route="/publish/<string:name>", ws_route="/", name="PubSub"):
        """

        :param http: Flask Http server
        :param ws: Flask-Sockets WS server
        :param http_route: http adress root
        :param ws_route: ws adress root
        """
        self.name = name
        self._http = http
        self._ws = ws
        self._populate(http_route, ws_route)
        self.topics = []

    def _populate(self, http_route, ws_route):
        # Adding Http Publish route
        @self._http.route(http_route)
        def http_handling(*args, **kwargs):
            return "Success", 200

        # Declaring
        @self._ws.route(ws_route)
        def ws_route(client, *args, **kwargs):
            print(client)
            client.send(json.dumps({"status": 200, "success": True}))
            while not client.closed:
                pass

