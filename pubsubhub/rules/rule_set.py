from . import Rule
from .exceptions import BrokenRuleException

class RuleSet:
    def __init__(self):
        self.rules = []

    def add_rules(self, *args):
        """
        Checks type then add Rules object to the RuleSet
        """
        for rule in args:
            if isinstance(rule, Rule):
                self.rules.append(rule)
            else:
                raise TypeError("Excepted Rule object, got {}".format(type(rule)))

    def validate(self, client):
        """
        Checks if the client respect all the rules in the set.
        """
        for rule in self.rules:
            if rule.is_respected_by(client):
                pass
            else:
                raise BrokenRuleException(rule.error_message)