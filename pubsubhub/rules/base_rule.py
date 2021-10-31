class Rule:
    def __init__(self):
        """
        Caution : all rules funcs must be False to invalidate a rule
        """
        self.rule_funcs = []
        self.error_message = "UNSET MESSAGE"

    def is_respected_by(self, client):
        if any(rule(client) for rule in self.rule_funcs):
            return True
        else:
            return False