from . import Rule
import time


class SubsribedAmountRule(Rule):
    """
    Allows to set a floor limit to subscription amount.
    The grace time allows for the user to regulate the situation.
    """
    def __init__(self, amount, grace_time, floor=False):
        super().__init__()

        self.amount = amount
        self.grace_time = grace_time
        self.is_floor_limit = floor
        self.error_message = "Subscription amount were outside the expected range for too long."

        self.rule_funcs.append(self.in_grace_time)
        self.rule_funcs.append(self.valid_amount)

    def in_grace_time(self, client):
        """ Return True if the last subscription exceeds grace time """
        return time.time() - self.grace_time < client.last_subscription_date

    def valid_amount(self, client):
        """ Return True if the amount is valid"""
        if self.is_floor_limit:
            return self.amount <= len(client.topics)
        else:
            return self.amount >= len(client.topics)
