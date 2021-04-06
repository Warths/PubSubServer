class PubSubException(Exception):
    pass


class PubSubServerException(PubSubException):
    """ Generic, PubSubHub related"""
    pass


class PubSubClientException(PubSubException):
    """ Generic, PubSubClient related """
    pass


class PublishError(PubSubServerException):
    """ Raised when a publication fails"""
    pass


class SendException(PubSubClientException):
    """ Raised when PubSubClient could not send its payload"""
    pass


class SubscribeError(PubSubClientException):
    """ Raised when a subscription fails """
    pass
