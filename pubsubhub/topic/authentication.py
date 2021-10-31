import requests
import credentials
import time

class TwitchAuthCore:
    def __init__(self):
        self.tokens = {}

    def get_identity(self, token):
        return {
            "user_id": self.tokens[token]["user_id"],
            "login": self.tokens[token]["login"]
        }

    def verify(self, token):
        # Cache management
        if token in self.tokens:
            if time.time() < self.tokens[token]["expires_in"]:
                return True
            else:
                self.tokens.pop(token)

        # Authentication
        headers = {"Authorization": "Bearer {}".format(token)}
        r = requests.get("https://id.twitch.tv/oauth2/validate", headers=headers)

        # Checking request success
        if r.status_code != 200:
            return False

        result = r.json()

        # Checking that AUTH key was delivered by the app
        if result["client_id"] != credentials.TWITCH_CLIENT_ID:
            return False

        self.tokens[token] = result
        self.tokens[token]["expires_in"] = self.tokens[token]['expires_in'] + int(time.time()) - 500
        return True


twitch_auth = TwitchAuthCore()

def invalid():
    raise PermissionError("Invalid Token")

def is_authorized(permitted_status, auth_data):
    # ANONYMOUS SUBSCRIPTIONS
    if "any" in permitted_status:
        return ["anon"]

    # Checking correct authentication format
    if "type" not in auth_data:
        return False

    if "token" not in auth_data:
        return False

    # TO REWORK
    # APP SUBSCRIPTIONS
    if auth_data["token"] in credentials.SECRETS and "app" in permitted_status:
        return ["app:{}".format(credentials.SECRETS[auth_data["token"]])]

    # OAUTH2 SUBSCRIPTION (Twitch)
    if auth_data["type"] == "twitch" and twitch_auth.verify(auth_data['token']):
        return list(twitch_auth.get_identity(auth_data['token']).values())

    # If we reach this, auth data is not a known/supported type
    return False