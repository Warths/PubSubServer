from flask import Flask
from flask_sockets import Sockets

from pubsubhub.pubsubhub import PubSubHub
from pubsubhub.rules import *
from pubsubhub.topic import Topic

# Declaring HTTP, WebSocket and PubSub app
http = Flask(__name__)
ws = Sockets(http)
pubsub = PubSubHub(http, ws)

# Declaring Pubsub rules
pubsub.rule_set.add_rules(
    SubsribedAmountRule(
        amount=1,
        grace_time=30,
        floor=True
    ),
    SubsribedAmountRule(
        amount=50,
        grace_time=0
    ),
    PingIntervalRule(
        interval=300
    )
)
pubsub.topic_pool.add_topics(
    Topic("base",
          publishers=["twitch"],
          subscribers=["twitch"]
          ),
    Topic("secret",
          publishers=["app"],
          subscribers=["any"]
          )
)

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('127.0.0.1', 5000), http, handler_class=WebSocketHandler)
    server.serve_forever()
