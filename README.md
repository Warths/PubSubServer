# PubSub Implementation
This is a simple implementation of a pub/sub message broker meant to be used for Shreaddy's microservices

**Example:**
This will create an "echo" topic, which doesn't require any authentification to either publish and subscribe. Any publish will be forwarded to subscribers, without filtering.
```py
from flask import Flask
from flask_sockets import Sockets  
from pubsubhub import PubSubHub 
from pubsubhub.topic import EchoTopic
  
# Declaring http app, sockets app and PubSub app
http = Flask(__name__)  
ws = Sockets(http)  
pubsub = PubSubHub(http, ws)

# Adding an "example" topic
pubsub.add_topic(EchoTopic("echo"))
  
if __name__ == "__main__":  
    from gevent import pywsgi  
    from geventwebsocket.handler import WebSocketHandler  
    server = pywsgi.WSGIServer(('127.0.0.1', 5000), http, handler_class=WebSocketHandler)  
    server.serve_forever()
```
## Logic:
### Preparation : 
1. Building Flask App
2. Wrap Flask app in Flask-Sockets app
3. Creating PubSubHub(s)
4. Building composite(s) topic(s) using either provided or custom components
5. Adding topics to PubSubHub(s)
6. Serve through the server of your choice

### Websocket Client Handling Loop

1. Checking if the client is alive
	  - Has the client been closed ?
	  - Did the client respected ping interval ? 
	  - Was the client subscribed to any topic during the required interval ?
2. Sending and flushing all message in the queue
3. Receiving packets (0.1 timeout)
4. Handling received packet (if any)
5. Repeat

## Objects 
### Class: PubSubHub
> PubSubHub is a class that provide a closed Websocket/HTTP hub for client to connects, subscribe or publish. It takes the Flask and Flask-sockets Apps as arguments, and creates the ws and http endpoints automatically.
> 
> Routes for both endpoints can be customized, to allow multiple PubSubHub to work on the same application.

**Methods**: 
add_topic(topic)
> Allows to add a topic to the PubSub Hub. Topic is a class that is described below, which

serve(client):
> Client Handling loop (described above)

### Class: Client
> Client represent the websocket connection from the POV of the Hub, providing methods to serve and check connexion health.
>  
> It wraps the client handling loop as `serve()`
>
> It allows for non-blocking receive
>
> Checks ping requirements as well as subscription requirements      

**Properties**: 
alive: 
> Checks for 3 connexion maintain routines : 
>
> if the last ping/pong was issued before the timeout threshold 
>
> if websocket was closed
>
> if client was subscribed for 15 seconds


**Methods**:

alive(amount)
> Checks if the client was subscribed to anything within the `amount` last seconds

getaddr()
> Return formatted remote address with port, using one of those headers : 
>
> X_REAL_IP (internal header name: HTTP_X_REAL_IP), set by your reverse proxy
>
> REMOTE_ADDR if HTTP_X_REAL_IP doesn't exist
>
> REMOTE_PORT 

send(payload)
> Sends a payload to client. Take care of json encoding

send_all(flush=True)
> Sends every payload in the queue. Empty the queue if flush is set to true (default)

flush()
> Removes all messages in the queue

add_to_queue()
> Adds a payload to the queue