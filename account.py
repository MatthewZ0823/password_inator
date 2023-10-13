def account_from_json(data):
    return Account(data["password"], data["username"], data["service"], data["url"])


class Account:
    def __init__(self, password, username, service, url):
        self.password = password
        self.username = username
        self.service = service
        self.url = url
