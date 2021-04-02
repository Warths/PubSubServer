from flask import Flask, request
from flask_sockets import Sockets
from pubsub.pubsubhub import PubSubHub

# Declaring HTTP, WebSocket and PubSub app
http = Flask(__name__)
ws = Sockets(http)
pubsub = PubSubHub(http, ws)

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('127.0.0.1', 5000), http, handler_class=WebSocketHandler)
    server.serve_forever()
