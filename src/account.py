from enum import Enum
import json
from typing import Optional
from rich.table import Table

from .constants import strings as STRINGS


class AccountFields(Enum):
    PASSWORD = 1
    USERNAME = 2
    SERVICE = 3
    URL = 4


class Account:
    def __init__(
        self,
        password: Optional[str],
        username: Optional[str],
        service: Optional[str],
        url: Optional[str],
    ):
        self.password = None if password == "" else password
        self.username = None if username == "" else username
        self.service = None if service == "" else service
        self.url = None if url == "" else url

    def _check_empty(self, val: str):
        if val == None or val == "":
            return STRINGS.EMPTY_TEXT
        return val

    def get_table(self, display_password: bool = False):
        """
        Return a rich table with the account's information
        If any field is None or "", it will display EMPTY_TEXT (Takes priority over display_password)
        If display_password is True, the password will be displayed, otherwise it will disply HIDDEN_TEXT
        """
        table = Table(title="Account")
        table.add_column("Field")
        table.add_column("Value")

        if display_password:
            table.add_row("Password", self._check_empty(self.password))
        elif self.password != None and self.password != "":
            table.add_row("Password", HIDDEN_TEXT)
        else:
            table.add_row("Password", EMPTY_TEXT)

        table.add_row("Username", self._check_empty(self.username))
        table.add_row("Service", self._check_empty(self.service))
        table.add_row("URL", self._check_empty(self.url))

        return table

    def __eq__(self, other):
        isAccount = isinstance(other, self.__class__)

        if not isAccount:
            return False

        return self.__dict__ == other.__dict__


def account_from_dict(data: dict) -> Account:
    return Account(data["password"], data["username"], data["service"], data["url"])


def load_accounts_from_file(path: str) -> list[Account]:
    """
    Return a list of accounts from the json file given by path. If a file is not found, create a new one
    Can raise a `JSONDecodeError`
    """
    try:
        with open(path, "r") as file:
            data = json.load(file)

        return list(map(lambda account: account_from_dict(account), data))
    except FileNotFoundError:
        with open("accounts.json", "w") as file:
            file.write("[]")
        return []


def save_account_to_file(path: str, account: Account) -> None:
    """
    Append the given account to the json file given by path
    Can raise a `JSONDecodeError`
    """
    accounts = load_accounts_from_file(path)
    accounts.append(account)

    with open(path, "w") as file:
        # Convert the accounts to a list of dicts so it's json serializable
        serialized_accounts = list(map(lambda account: account.__dict__, accounts))
        json.dump(serialized_accounts, file, indent=4)
