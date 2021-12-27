import time

class ServerTime:
    def __repr__(self):
        return int(time.time() * 1000)
