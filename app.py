from flask import Flask
from flask_sockets import Sockets

from pubsubhub.pubsubhub import PubSubHub
from pubsubhub.rules import *
from pubsubhub.topic import Topic
from pubsubhub.topic.appended import ServerTime

# Declaring HTTP, WebSocket and PubSub app
http = Flask(__name__)
ws = Sockets(http)
pubsub = PubSubHub(http, ws)

# Declaring Pubsub rules
pubsub.rule_set.add_rules(
    SubsribedAmountRule(amount=1, grace_time=30, floor=True),
    SubsribedAmountRule(amount=50, grace_time=0),
    PingIntervalRule(interval=300)
)

pubsub.topic_pool.add_topics(
    Topic(
        "light_fx_cooldown",
        publishers=["app"],
        subscribers=["any"],
        appended=[
            lambda: {"server_time": ServerTime()},
            lambda: {"emitted": ServerTime().__repr__()}
        ],
        spec={
            "cooldown": int,
        }
    ),
    Topic(
        "light_cooldown",
        publishers=["app"],
        subscribers=["any"],
        appended=[
            lambda: {"server_time": ServerTime()},
            lambda: {"emitted": ServerTime().__repr__()}
        ],
        spec={
            "cooldown": int,
        }
    ),
    Topic(
        "light_availability",
        publishers=["app"],
        subscribers=["any"],
        spec={
            "available": bool,
        }
    ),
    Topic(
        "light_fx_availability",
        publishers=["app"],
        subscribers=["any"],
        spec={
            "available": bool,
        }
    ),
    Topic(
        "playlist",
        publishers=["app"],
        subscribers=["any"],
        spec={
            "available": list,
        }
    ),
)

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('127.0.0.1', 5000), http, handler_class=WebSocketHandler)
    server.serve_forever()
