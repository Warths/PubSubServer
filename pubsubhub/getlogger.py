import logging
from colorlog import ColoredFormatter

def getLogger(name):
    if name == "__main__":
        name = "SYSTEM"
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(asctime)s  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s[%(name)s] %(message)s%(reset)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log